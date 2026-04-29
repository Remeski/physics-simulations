import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import scipy as sp

L = 1
v = 1

m = 5
n = 2

alpha = sp.special.jn_zeros(m,n)[-1]
k = alpha/L

R = lambda r: 0.5*sp.special.jv(m, r*k)
Theta = lambda theta: np.exp(1j*m*theta)
T = lambda t: np.exp(1j*k*v*t)
f = lambda r,theta,t: np.real(R(r)*Theta(theta)*np.real(T(t)))

fig = plt.figure()
ax = fig.add_subplot(projection="3d")

ax.set_zlim(0, 1)

rs = np.linspace(0,L, 30)
ps = np.linspace(0,2*np.pi, 60)
Rs,Ps = np.meshgrid(rs, ps)

F = f(Rs,Ps,0)

X,Y = Rs*np.cos(Ps), Rs*np.sin(Ps)

surf = ax.plot_surface(X, Y, F, cmap="summer")

def animate(t):
    global surf
    F = f(Rs,Ps,t)
    surf.remove()
    surf = ax.plot_surface(X, Y, F, cmap="summer")
    return surf


anim = FuncAnimation(fig=fig, func=animate, frames=np.linspace(0,10,300), blit=False, interval=30)

plt.show()
