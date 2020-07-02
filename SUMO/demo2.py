def action(tls, ph, wait_time):  #parameters: the phase duration in the green signals
    tls_id = tls[0]
    init_p = traci.trafficlights.getPhase(tls_id) 
    prev = -1
    changed = False
    current_phases = ph
    p_state = np.zeros((60,60,2))

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        c_p = traci.trafficlights.getPhase(tls_id)
        if c_p != prev and c_p%2==0:
            traci.trafficlights.setPhaseDuration(tls_id, ph[int(c_p/2)]-0.5)
            prev = c_p
        if init_p != c_p:
            changed = True
        if changed:
            if c_p == init_p:
                break
        traci.simulationStep()
        step += 1
        if step%10==0:
            for veh_id in traci.vehicle.getIDList():
                wait_time_map[veh_id] = traci.vehicle.getAccumulatedWaitingTime(veh_id)
    for veh_id in traci.vehicle.getIDList():
        traci.vehicle.subscribe(veh_id, (tc.VAR_POSITION, tc.VAR_SPEED, tc.VAR_ACCUMULATED_WAITING_TIME))
    p = traci.vehicle.getSubscriptionResults()
    
    wait_temp = dict(wait_time_map)
    for x in p:
        ps = p[x][tc.VAR_POSITION]
        spd = p[x][tc.VAR_SPEED]
        p_state[int(ps[0]/5), int(ps[1]/5)] = [1, int(round(spd))]

    wait_t = sum(wait_temp[x] for x in wait_temp)
    
    d = False
    if traci.simulation.getMinExpectedNumber() == 0:
        d = True
        
    r = wait_time-wait_t
    p_state = np.reshape(p_state, [-1, 3600, 2])
    return p_state,r,d,wait_t


    '''
        收到1的指令以后, 后面一直给他 这个action 的kinetics 
            - 给他指令 需要反应 需要做时间延时
            - 可以用一下的方法来延迟
            - 金老师： 说会有几率执不执行这个指令 -- 比如0.8几率执行, 0。2不执行 -- 要numpy.random.geometric -- 模拟接下来司机在接下来step会不会做减速(yield)，就直接用most comfortable deceleration (预设的), 去行动.....
            - Step 不是 stamp 
            
        initial: 
            6-array 添一个0 （indicator: 行进中）
            - 控制在15辆车以内
            - 改成100米
            - txt --> np array 
    '''