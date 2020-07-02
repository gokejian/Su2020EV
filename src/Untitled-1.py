import math


import Consts


class DriverModel(object):

    @staticmethod
    def calc_acceleration(vehicle):
        raise NotImplementedError()

    @staticmethod
    def calc_velocity(vehicle):
        raise NotImplementedError()

    @staticmethod
    def calc_position(vehicle):
        raise NotImplementedError()

    @staticmethod
    def calc_gap(vehicle):
        raise NotImplementedError()


class IDM(DriverModel):

'''
staticmethod: can do IDM.calc_desired_gap(vehicle)

'''

    @staticmethod
    def calc_gap(vehicle):  '''net distance'''
        if vehicle.lead_vehicle:
            return float(vehicle.lead_vehicle.position -
                         IDM.calc_position(vehicle) -
                         vehicle.lead_vehicle.length)
        else:
            return float(Consts.ROAD_LENGTH + 100)

    @staticmethod
    def calc_acceleration(vehicle):
        """
        dv(t)/dt = a[1 - (v(t)/v0)^4  - (s*(t)/s(t))^2]
        """
        acceleration = math.pow(
            (vehicle.velocity / vehicle.get_desired_velocity()), 4)
        deceleration = math.pow(IDM.calc_desired_gap(vehicle) / vehicle.gap, 2)
        return float(vehicle.max_acceleration * (1 - acceleration - deceleration))

    @staticmethod
    def calc_desired_gap(vehicle): "S_star"
        pv = vehicle.velocity
        if vehicle.lead_vehicle: 
            lpv = vehicle.lead_vehicle.velocity
        else:
            lpv = pv "else if lead_vehicle is None, then equal the two"
        c = ((vehicle.get_safetime_headway() * pv) +
             ((pv * (pv - lpv)) / (2 * math.sqrt(
                 vehicle.max_acceleration * vehicle.max_deceleration)))) 
                 '''change max_deceleration to comfor_decel
                 '''
        ret = float(vehicle.minimum_distance + max(0, c)) '''avoid any negativity'''
        return ret

    @staticmethod
    def calc_velocity(vehicle):
        new_velocity = IDM.calc_raw_velocity(vehicle)
        return float(max(0, new_velocity))  '''avoid any negativity'''

    @staticmethod
    def calc_raw_velocity(vehicle):
        return float(vehicle.velocity + (IDM.calc_acceleration(vehicle) *
                                         Consts.TIME_STEP))

    @staticmethod
    def calc_position(vehicle):
        if IDM.calc_raw_velocity(vehicle) < 0:
            new_position = (vehicle.position -
                            (0.5 * (math.pow(vehicle.velocity, 2) /
                                    IDM.calc_acceleration(vehicle))))
        else:
            new_position = (vehicle.position +
                            (vehicle.velocity * Consts.TIME_STEP) +
                            (0.5 * IDM.calc_acceleration(vehicle) *
                             math.pow(Consts.TIME_STEP, 2)))
        return float(new_position)

   