import numpy as np

from . import orbitx_pb2 as protos


class PhysicsEntity(object):
    def __init__(self, entity):
        assert isinstance(entity, protos.Entity)
        self.name = entity.name
        self.pos = np.asarray([entity.x, entity.y])
        self.R = entity.r
        self.v = np.asarray([entity.vx, entity.vy])
        self.m = entity.mass
        self.spin = entity.spin
        self.heading = entity.heading
        self.fuel = entity.fuel
        self.throttle = entity.throttle

    def as_proto(self):
        return protos.Entity(
            name=self.name,
            x=self.pos[0],
            y=self.pos[1],
            vx=self.v[0],
            vy=self.v[1],
            r=self.R,
            mass=self.m,
            spin=self.spin,
            heading=self.heading,
            fuel=self.fuel,
            throttle=self.throttle
        )



class BasicFuelComp(object):
    def __init__(self):
        self.maxfuel=1000
class BasicEngine(object):
    def __init__(self,fuel_cons=0.1,max_t=0.01,max_acc=100):
        self.fuel_consumption=fuel_cons #fuel consumed per sec at max throttle
        self.max_throttle_increase=max_t # max throttle increase every second 
        self.max_acc=max_acc #max acceleration
    def action_check(self,throttle): #set throttle into possible range in 1 action
        if throttle>self.max_throttle_increase:
            throttle=self.max_throttle_increase
        elif throttle<(-self.max_throttle_increase):
            throttle=-self.max_throttle_increase
        return throttle
    def _calc_acc(self,throttle):
        return min(max(0,self.max_acc*throttle),self.max_acc)
class BasicReactionWheel(object):
    def __init__(self,fuel_cons=0.1,max_spin_increase=0.01,max_spin_acc=1): #spin acc in rad
        self.fuel_consumption=fuel_cons #fuel consumed per sec at max throttle
        self.max_spin_increase=max_spin_increase # max spin increase every second
        self.max_spin_acc=max_spin_acc #max spin acceleration
    def action_check(self,spin): #set spin into possible range in 1 action
        if spin>self.max_spin_increase:
            spin=self.max_spin_increase
        elif spin<(-self.max_spin_increase):
            spin=-self.max_spin_increase
        return spin
    def _calc_acc(self,spin):
        return min(max(-self.max_spin_acc,self.max_spin_acc*spin),self.max_spin_acc)
class Habitat(PhysicsEntity):
    def __init__(self, entity):
        super().__init__(entity)
        self.components={} #framework for system
        self.connection={} #framework for relation between system
        self.Engine=BasicEngine()
        self.RW=BasicReactionWheel()
        self.fuel=1000
        self.throttle=0.0 #current throttle between 0 and 1,(need loading)
    def _cal_fuel(self):
        pass
        #for possible future modular fuel tanks
        #for name,com in self.components.items():
        #    if type(com) is FuelComp:
        #        self.fuel+=com.maxfuel
    def update(self,spin,throttle,fuel):
        self.spin=spin
        self.throttle=throttle
        self.fuel=fuel
    def get_fuel_cons(self,Engine,RW):
        #if CHEAT_FUEL:
        #    return 0
        fuel=0
        if Engine:
            fuel+=self.Engine.fuel_consumption
        if RW:
            fuel+=self.RW.fuel_consumption
        return fuel
    def step(self,actions=None,index=None): # need major rewrite
        '''
        for now actions is a dict {"throttle":x,"spin":x}
        return additional vector acceleration and spin acceleration 
        '''
        if actions is not None:
            #if fuel<0 and not CHEAT_FUEL:
            #    t_acc=np.zeros(len(throttle))
            #    spin_acc=np.zeros(len(spin))
            #    return t_acc,spin_acc
            throttle=actions["throttle"]
            spin=actions["spin"]
            throttle[index]=self.Engine.action_check(throttle[index])
            spin[index]=self.RW.action_check(spin[index])
            #t_acc=np.zeros(len(throttle))
            #spin_acc=np.zeros(len(spin))
            #t_acc[index]=self.Engine._calc_acc(last[throttle][index]+throttle[index])
            #spin_acc[index]=self.RW._calc_acc(last[spin][index]+spin[index])
            #print(throttle[index])
            #print(spin[index])
            return throttle,spin 
        t_acc=np.zeros(len(throttle))
        spin_acc=np.zeros(len(spin))
        return t_acc,spin_acc
    def max_check(self,throttle,spin,index):
        throttle[index]=self.Engine._calc_acc(throttle[index])
        spin[index]=self.RW._calc_acc(spin[index])
        return throttle,spin
    def XY_acc(self,acc,spin_angle): #use for throttle acceleration probably can be removed later
        return np.cos(spin_angle)*acc,np.sin(spin_angle)*acc
