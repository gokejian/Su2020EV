import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

# # Deep Q Network Agent
# class DeepQNetwork(nn.Module):
#     def __init__(self, lr, input_dims, fc1_dims, fc2_dims,
#             n_actions):
#         super(DeepQNetwork, self).__init__()
#         self.input_dims = input_dims
#         self.fc1_dims = fc1_dims
#         self.fc2_dims = fc2_dims
#         self.n_actions = n_actions
#         self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
#         self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
#         self.fc3 = nn.Linear(self.fc2_dims, self.n_actions)
#
#         self.optimizer = optim.Adam(self.parameters(), lr=lr)
#         self.loss = nn.MSELoss()
#         self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
#         self.to(self.device)
#
#     def forward(self, state):
#         x = F.relu(self.fc1(state))
#         x = F.relu(self.fc2(x))
#         actions = self.fc3(x)
#
#         return actions
# dimensions for MLP and FC layers
MLP_dims = [16, 16, 32, 32, 64, 128, 256, 1]
FC_dims = [1, 16, 32, 64, 1]

# Some utility functions
def get_and_init_FC_layer(din, dout):
    li = nn.Linear(din, dout)
    #init weights/bias
    nn.init.xavier_uniform_(li.weight.data, gain=nn.init.calculate_gain('relu'))
    li.bias.data.fill_(0.)
    return li


def get_MLP_layers(dims, doLastRelu):
    layers = []
    for i in range(1, len(dims)):
        layers.append(get_and_init_FC_layer(dims[i-1], dims[i]))
        if (i == len(dims)-1) and not doLastRelu:
            continue
        layers.append(nn.ReLU())
    return layers


class PointwiseMLP(nn.Sequential):
    '''Nxdin ->Nxd1->Nxd2->...-> Nxdout'''

    def __init__(self, dims, doLastRelu=False):
        layers = get_MLP_layers(dims, doLastRelu)
        super(PointwiseMLP, self).__init__(*layers)


class GlobalPool(nn.Module):
    """ BxNxK -> BxK
    B stands for number of batches
    N stands for number of vehicles
    K stands for number of attributes per vehicle, 6 in this case"""

    def __init__(self, pool_layer):
        super(GlobalPool, self).__init__()
        self.Pool = pool_layer

    def forward(self, X):
        X = X.unsqueeze(-3) #Bx1xNxK
        X = self.Pool(X)
        X = X.squeeze(-2)
        X = X.squeeze(-2)   #BxK
        return X


class PointNetGlobalMax(nn.Sequential):
    '''BxNxdims[0] -> Bxdims[-1]'''
    def __init__(self, dims, doLastRelu=False):
        layers = [
            PointwiseMLP(dims, doLastRelu=doLastRelu),      #BxNxK
            GlobalPool(nn.AdaptiveMaxPool2d((1, dims[-1]))),#BxK
        ]
        super(PointNetGlobalMax, self).__init__(*layers)


# The main class defined our neural network
class VehicleNet(nn.Module):
    def __init__(self, lr, MLP_dims, FC_dims):
        # The dimension of the last layer of the MLP must equal the first layer of FC
        assert(MLP_dims[-1] == FC_dims[0])
        # layers = [
        #     PointNetGlobalMax(MLP_dims, doLastRelu=False),#BxK
        # ]
        # layers.extend(get_MLP_layers(FC_dims, False))
        super(VehicleNet, self).__init__()
        self.pointNetGlobalMax = PointNetGlobalMax(MLP_dims)
        self.PointwiseMLP = PointwiseMLP(FC_dims)
        # Hyperparameters
        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, state):
        # Get the global maximum feature
        x = self.pointNetGlobalMax(state)
        # Concatenate the local feature with the global feature along the x-axis
        y = T.cat((x, state), 0)
        # Append the fully connected layers after the concatenation
        actions = self.PointwiseMLP(y)

        return T.sigmoid(actions) > 0.5


# Agent class
class Agent():
    def __init__(self, gamma, epsilon, lr, input_dims, batch_size,
            max_mem_size=100000, eps_end=0.05, eps_dec=5e-4):
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_end
        self.eps_dec = eps_dec
        self.lr = lr
        # n_actions is no longer fixed
        # self.action_space = [i for i in range(n_actions)]
        self.mem_size = max_mem_size
        self.batch_size = batch_size
        self.mem_cntr = 0
        self.iter_cntr = 0
        self.replace_target = 100

        # self.Q_eval = DeepQNetwork(lr, n_actions=n_actions, input_dims=input_dims,
        #                             fc1_dims=256, fc2_dims=256)
        # self.Q_next = DeepQNetwork(lr, n_actions=n_actions, input_dims=input_dims,
        #                             fc1_dims=64, fc2_dims=64)

        # Define the evaluation network and target network
        self.Q_eval = VehicleNet(lr, MLP_dims, FC_dims)
        self.Q_next = VehicleNet(lr, MLP_dims, FC_dims)

        self.state_memory = np.zeros((self.mem_size, *input_dims), dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, *input_dims), dtype=np.float32)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.bool)

    def store_transition(self, state, action, reward, state_, terminal):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = terminal

        self.mem_cntr += 1

    def choose_action(self, observation):
        if np.random.random() > self.epsilon:
            state = T.tensor([observation]).to(self.Q_eval.device)
            actions = self.Q_eval.forward(state)
            action = T.argmax(actions).item()
        else:
            action = []
            # Generate action based on number of vehicles
            for i in range(len(observation)):
                action.append(np.random.randint(0, 1))
        return action

    def learn(self):
        if self.mem_cntr < self.batch_size:
            return

        self.Q_eval.optimizer.zero_grad()
        
        max_mem = min(self.mem_cntr, self.mem_size)

        batch = np.random.choice(max_mem, self.batch_size, replace=False)
        
        batch_index = np.arange(self.batch_size, dtype=np.int32)

        state_batch = T.tensor(self.state_memory[batch]).to(self.Q_eval.device)
        new_state_batch = T.tensor(self.new_state_memory[batch]).to(self.Q_eval.device)
        action_batch = self.action_memory[batch]
        reward_batch = T.tensor(self.reward_memory[batch]).to(self.Q_eval.device)
        terminal_batch = T.tensor(self.terminal_memory[batch]).to(self.Q_eval.device)

        q_eval = self.Q_eval.forward(state_batch)[batch_index, action_batch]
        q_next = self.Q_eval.forward(new_state_batch)
        q_next[terminal_batch] = 0.0

        q_target = reward_batch + self.gamma*T.max(q_next, dim=1)[0]

        loss = self.Q_eval.loss(q_target, q_eval).to(self.Q_eval.device)
        loss.backward()
        self.Q_eval.optimizer.step()

        self.iter_cntr += 1
        self.epsilon = self.epsilon - self.eps_dec if self.epsilon > self.eps_min \
                       else self.eps_min