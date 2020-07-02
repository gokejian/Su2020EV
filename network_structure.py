# -*- coding: utf-8 -*-
"""Author: Haoran Su
Email: hs1854@nyu.edu
"""

import torch
import torch.nn as nn
import torch.nn.functional as Functional


# Initialize a full connected layer.
# Input: input_dim, output_dim
def get_and_init_FC_layer(input_dim, output_dim):
    linear_layer = nn.Linear(input_dim, output_dim)
    # Initialize weights and bias for this linear layer
    nn.init.xavier_uniform_(linear_layer.weight.data, gain=nn.init.calculate_gain('relu'))
    linear_layer.bias.data.fill_(0.)
    return linear_layer


# Generate a fully connected layers/Multilayer Perceptrons network
# We ignore the last ReLU operation if noted
def get_mlp_layers(dims, do_last_relu):
    layers = []
    for i in range(1, len(dims)):
        layers.append(get_and_init_FC_layer(dims[i-1], dims[i]))
        # If this is the last layer and is asked not to ReLU:
        if i == len(dims)-1 and not do_last_relu:
            continue
        layers.append(nn.ReLU())
    return layers


class VehiclewiseMLP(nn.Sequential):
    def __init__(self, dims, do_last_relu=False):
        # Initialize layers with
        layers = get_mlp_layers(dims, do_last_relu)
        super(VehiclewiseMLP, self).__init__(*layers)


# Define a global pool class to yield global pooling
class GlobalPool(nn.Module):
    '''BxNxK -> BxK'''
    def __init__(self, pool_layer):
        super(GlobalPool, self).__init__()
        self.Pool = pool_layer

    def forward(self, X):
        X = self.Pool(X)
        X = torch.squeeze(X)
        return X


# Global Max Pooling
class PointNetGlobalMax(nn.Sequential):
    """Suppose 1 batch * 6 vehicles * 5 attributes, we would like to get 1 batch * 6 actions
    Which is saying the dimension change should be B*N*dim[0] -> B*N"""
    '''BxNxdims[0] -> Bxdims[-1]'''

    def __init__(self, dims, do_last_relu=False):
        layers = [
            VehiclewiseMLP(dims, do_last_relu = do_last_relu),      #BxNxK
            GlobalPool(nn.AdaptiveMaxPool2d((1, dims[-1]))),#BxK
        ]
        super(PointNetGlobalMax, self).__init__(*layers)


class VehicleNet(nn.Module):
    def __init__(self, dim_pointNet, dim_output):
        super(VehicleNet, self).__init__()
        self.pointNetGlobalMax = PointNetGlobalMax(dim_pointNet, do_last_relu=False)

        self.VehiclewiseMLP = VehiclewiseMLP(dim_output, do_last_relu=False)

    def forward(self, state):
        x = self.pointNetGlobalMax(state)
        # concatenate the global feature with local feature
        y = torch.cat()
        y = torch.sigmoid(y)
        return y




# # Main Structure: PointNet Vanilla structure
# class PointNetVanilla(nn.Sequential):
#     def __init__(self, MLP_dims, FC_dims, MLP_doLastRelu=False):
#
#         # MLP
#         assert(MLP_dims[-1] == FC_dims[0])
#         layers = [
#             PointNetGlobalMax(MLP_dims, do_last_relu= MLP_doLastRelu),
#         ]
#         layers.extend(get_mlp_layers(FC_dims, False))
#         super(PointNetVanilla, self).__init__(*layers)


