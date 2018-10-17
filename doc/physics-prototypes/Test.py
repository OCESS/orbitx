import numpy as np
import scipy as sp
import scipy.sparse as sparse
import random as rd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import time
from scipy.integrate import *

n=3 # number of entities simulated
h=720 # step size for time acceleration (sec)

#define base variables

X=np.random.rand(1,n)*60000000000 # X coordinates of entities in vector
Y=np.random.rand(1,n)*60000000000 # Y coordinates of entities in vector
DX=(np.random.rand(1,n)-0.5)*40000 # X component of the speed vector of entities in vector
DY=(np.random.rand(1,n)-0.5)*40000 # Y component of the speed vector of entities in vector

M=np.random.rand(1,n) #mass of entities in vector
Mr=M.round(0) #random var for later
M=M.astype(object, copy=False)	# using object type for elements in array to avoid overflow
Mr=Mr.astype(object, copy=False) # using object type for elements in array to avoid overflow
#M=M*(10**24)+Mr*((10**26)*np.random.rand())	#choose objects to be large (now always choose the 0-th element)
M=M*(10**24)	# use realistic weights
M[0][0]=1.988e30	# use sun weights
DX[0][0]=0	#set initial sun speed to 0
DY[0][0]=0

def force(MM,X,Y):
    G=6.674e-11	# gravitational constant
    D=(X-X.transpose())**2+(Y-Y.transpose())**2	# distance between all objects in vector form (r^2)
    return np.multiply(G*(MM/(D+0.00001)),np.where(np.identity(n), 0, 1))	# GM1M2/(r^2)
def force_sum(force):	# function to sum up all force applied on objects
    return np.sum(force,1)
def vec_to_angle(X,Y): # calculate the angle of objects
    Xd=X-X.transpose()
    Yd=Y-Y.transpose()
    return np.arctan2(Yd,Xd+0.00001)
def angle_to_vec_stuff(ang,hyp):	# convert angle and force to force vectors
    X=np.multiply(np.cos(ang),hyp)
    Y=np.multiply(np.sin(ang),hyp)
    return X,Y
def f_to_a(f,M):	#covert force to acceleration
    return np.divide(f,M)
	
def get_acc(X,Y,M):	#compute accelerations
    MM=M*np.transpose(M)
    ang=vec_to_angle(X,Y)
    FORCE=force(MM,X,Y)
    Xf,Yf=angle_to_vec_stuff(ang,FORCE)
    Xf=force_sum(Xf)
    Yf=force_sum(Yf)
    Xa=f_to_a(Xf,M)
    Ya=f_to_a(Yf,M)
    return Xa,Ya
def new_v(h,DX,DY,DX2,DY2):	#calculate speed
    DX=DX+h*DX2
    DY=DY+h*DY2
def extract(y,n):	#ode only accept flattened array, this func extract from such arrays
    X=(y[0:n]).reshape(1,n)
    Y=(y[n:2*n]).reshape(1,n)
    DX=(y[2*n:3*n]).reshape(1,n)
    DY=(y[3*n:4*n]).reshape(1,n)
    M=(y[4*n:5*n]).reshape(1,n)
    return X,Y,DX,DY,M
	

def f(t,y,n=n):	# function for calculating change for ode
    X,Y,DX,DY,M=extract(y,n);
    Xa,Ya=get_acc(X,Y,M)
    DX=DX+Xa
    DY=DY+Ya
    X=X+DX
    Y=Y+DY
    ans=[DX,DY,Xa,Ya,np.zeros(M.shape)]
    ans=np.concatenate(ans).ravel()
    return ans
def fr(y,t,n):	#not used
    return f(t,y,n)
def euler(f,t0,y0,n):	#not used
    pass
	

#set up test
y0=[X,Y,DX,DY,M]
y0=np.concatenate(y0).ravel()
t0=0
	
r = ode(f).set_integrator('vode', method='bdf',atol=0.5,nsteps=750)	#ode in scipy
r.set_initial_value(y0,t0).set_f_params(n)	# feed ode initial values
ans=r.integrate(r.t+h)		# run ode
#X,Y,_,_,_=extract(ans,n)
all_out=[extract(ans,n)]

figure(num=None, figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')


scat=plt.scatter(X, Y)
plt.draw()

for i in range(0,int(2600000/h)):
    if not r.successful():
        break;
    ans=r.integrate(r.t+h)
    all_out+=[extract(ans,n)]
    plt.scatter(all_out[i][0], all_out[i][1])

