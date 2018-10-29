
# coding: utf-8

# In[1]:


import numpy as np
import scipy as sp
import scipy.sparse as sparse
import random as rd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import time
from scipy.integrate import *
from collections import OrderedDict
import random
import string
import json


# In[2]:


def distance(X,Y):
    return np.sqrt((X-X.transpose())**2+(Y-Y.transpose())**2)
def force(MM,X,Y):
    G=6.674e-11
    n=X.shape[1]
    D=(X-X.transpose())**2+(Y-Y.transpose())**2
    return np.multiply(G*(MM/(D+0.00001)),np.where(np.identity(n), 0, 1))
def force_sum(force):
    return np.sum(force,1)
def vec_to_angle(X,Y):
    Xd=X-X.transpose()
    Yd=Y-Y.transpose()
    return np.arctan2(Yd,Xd+0.00001)
def angle_to_vec_stuff(ang,hyp):
    X=np.multiply(np.cos(ang),hyp)
    Y=np.multiply(np.sin(ang),hyp)
    return X,Y
def f_to_a(f,M):
    return np.divide(f,M)
def get_acc(X,Y,M):
    MM=M*np.transpose(M)
    ang=vec_to_angle(X,Y)
    FORCE=force(MM,X,Y)
    Xf,Yf=angle_to_vec_stuff(ang,FORCE)
    Xf=force_sum(Xf)
    Yf=force_sum(Yf)
    Xa=f_to_a(Xf,M)
    Ya=f_to_a(Yf,M)
    return Xa,Ya
def new_v(h,DX,DY,DX2,DY2):
    DX=DX+h*DX2
    DY=DY+h*DY2
def extract(y,n):
    X=(y[0:n]).reshape(1,n)
    Y=(y[n:2*n]).reshape(1,n)
    DX=(y[2*n:3*n]).reshape(1,n)
    DY=(y[3*n:4*n]).reshape(1,n)
    #M=(y[4*n:5*n]).reshape(1,n)
    return X,Y,DX,DY
def derive(t,y,n,r,M):
    X,Y,DX,DY=extract(y,n);
    Xa,Ya=get_acc(X,Y,M)
    DX=DX+Xa
    DY=DY+Ya
    X=X+DX
    Y=Y+DY
    ans=[DX,DY,Xa,Ya]
    ans=np.concatenate(ans).ravel()
    return ans


# In[3]:


class Entity(object):
    def __init__(self,name,coor,r,M,v=[0,0],spin=0,movable=True):
        self.name=name
        self.coordinates=coor
        self.r=r
        self.M=M
        self.V=v
        self.spin=spin
        self.movable=movable
    def json_save(self):
        return {"name":self.name,"velocity":self.V,"mass":self.M,"radius":self.r,"coordinates":self.coordinates,"angular speed":self.spin}


# In[4]:


class PEngine(object):
    class Bad_Merge(Exception): # exception for merging same object
        def __init__(self, code=0):
            self.code = code
    def __init__(self,time=0):
        self.reset()
        self.time=time
    def reset(self):
        self.Entities=OrderedDict({})
        self.integrator=None
        self.init=False
    def _random_name(self):
        name=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        return name
    def random_entity(self,name=None):
        name=self._random_name(self)
        X=random.uniform(1e25, 1e30)
        Y=random.uniform(1e25, 1e30)
        r=random.uniform(1e5, 1e6)
        M=random.uniform(1e24, 1e26)
        self.Entities[name]=Entity(name,[X,Y],r,M)
    def create_entity(self,name,coor,r,M,v=[0,0],spin=0,movable=True):
        self.Entities[name]=Entity(name,coor,r,M,v,spin,movable)
    def add_entity(self,Entity):
        self.Entities[Entity.name]=Entity
    def Load_json(self,file):
        try:
            with open(file) as f:
                data = json.load(f)
        except IOError:
            print("Load file failure, no such file")
        self.reset()
        if "time" in data:
            self.time=data["time"]
        else:
            self.time=0
        for Entity in data["entities"]:
            if "name" in Entity:
                name=Entity["name"]
            else:
                name=PE._random_name()
            if "displacement" in Entity:
                coor=Entity["displacement"]
            elif "coordinates" in Entity:
                coor=Entity["coordinates"]
            else:
                coor=[random.uniform(1e25, 1e30),random.uniform(1e25, 1e30)]
            if "radius" in Entity:
                r=Entity["radius"]
            else:
                r=random.uniform(1e25, 1e30)
            if "mass" in Entity:
                m=Entity["mass"]
            else:
                m=random.uniform(1e24, 1e26)
            if "velocity" in Entity:
                v=Entity["velocity"]
            else:
                v=[0,0]
            if "angular speed" in Entity:
                spin=Entity["angular speed"]
            else:
                spin=0
            self.create_entity(name,coor,r,m,v,spin)
    def Save_json(PE,file="save.json"):
        json_dict={"entities":[]}
        json_dict["time"]=PE.time
        for _,Entity in PE.Entities.items():
            json_dict["entities"]+=[Entity.json_save()]
        with open(file, 'w') as outfile:  
            json.dump(json_dict, outfile, indent=4)
    def gather_data(self):
        self.X=np.asarray([entity.coordinates[0] for _,entity in self.Entities.items()]).reshape(1,len(self.Entities))
        self.Y=np.asarray([entity.coordinates[1] for _,entity in self.Entities.items()]).reshape(1,len(self.Entities))
        self.DX=np.asarray([entity.V[0] for _,entity in self.Entities.items()]).reshape(1,len(self.Entities))
        self.DY=np.asarray([entity.V[1] for _,entity in self.Entities.items()]).reshape(1,len(self.Entities))
        self.r=np.asarray([entity.r for _,entity in self.Entities.items()]).reshape(1,len(self.Entities))
        self.M=np.asarray([entity.M for _,entity in self.Entities.items()]).reshape(1,len(self.Entities))
        self.X=self.X.astype(object, copy=False)
        self.Y=self.Y.astype(object, copy=False)
        self.DX=self.DX.astype(object, copy=False)
        self.DY=self.DY.astype(object, copy=False)
        self.r=self.r.astype(object, copy=False)
        self.M=self.M.astype(object, copy=False)
    def initialize(self):
        self.gather_data()
        #add code here for init
        self.init=True
    def update(self,y):
        for X,Y,DX,DY,Entity in zip(y[0][0],y[1][0],y[2][0],y[3][0],[E[1] for E in PE.Entities.items()]):
            Entity.coordinates=[X,Y]
            Entity.V=[DX,DY]
    def merge(self,e1,e2):
        if e1==e2:
            raise self.Bad_Merge()
        e1=list(self.Entities.keys())[e1]
        e2=list(self.Entities.keys())[e2]
        if type(self.Entities[e1]) is str or type(self.Entities[e2]) is str:
            raise self.Bad_Merge()
        main=max([(e1,self.Entities[e1].M),(e2,self.Entities[e2].M)])
        if e1 is main[0]:
            victim=(e2,self.Entities[e2].M)
        else:
            victim=(e1,self.Entities[e1].M)
        mV=self.Entities[main[0]].V
        vV=self.Entities[victim[0]].V
        #need change speed
        self.Entities[main[0]].M+=self.Entities[victim[0]].M
        self.Entities[main[0]].r+=3 # change radius, to change
        self.Entities[victim[0]]=main[0]
    def collison_handle(self,coll):
        for i,j in zip(coll[0],coll[1]):
            try:
                self.merge(i,j)
            except self.Bad_Merge:
                continue
            #except:
            #    print("Merge fail")
        for name in list(self.Entities.keys()):
            if type(self.Entities[name]) is str:
                del self.Entities[name]
        self.gather_data()
    def collision_detect(self,out):
        X=out[0]
        Y=out[1]
        D=distance(X,Y)
        R=self.r+self.r.transpose()
        #coll=np.where(((D-R)<0))
        coll=np.where(((D-R)<0)-np.identity(D.shape[0]))
        if coll[0].shape[0]==0:
            return False
        self.collison_handle(coll)
        return True
    def run_step(self,step_size,atol=0.5,nsteps=750):
        if not self.init:
            self.initialize()
        if self.integrator is None:
            t0=self.time
            y0=[self.X,self.Y,self.DX,self.DY]
            y0=np.concatenate(y0).ravel()
            self.integrator = ode(derive).set_integrator('vode', method='bdf',atol=atol,nsteps=nsteps)
            self.integrator.set_initial_value(y0,t0).set_f_params(len(self.Entities),self.r,self.M)
        out=self.integrator.integrate(self.integrator.t+step_size)
        out=extract(out,len(self.Entities))
        self.out=out
        self.update(out)
        self.collision_detect(out)
    def get_time(self):
        return 0 #time in date + time


# In[ ]:


PE=PEngine()
PE.Load_json("data.json")
PE.run_step(1)
for i in range(0,90000000):
    PE.run_step(1)

