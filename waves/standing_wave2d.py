import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import TwoSlopeNorm

X,Y = np.meshgrid(np.linspace(-10,10,100), np.linspace(-10,10,100))

fig = plt.figure()
ax = fig.add_subplot()

k = 1
v = 2
omega = v/k
r = lambda x,y: np.sqrt(x**2+y**2)
wave = lambda k,t: np.sin(k*r(X,Y)-omega*t)

F = lambda t: wave(k,t)-wave(-k,t)

norm = TwoSlopeNorm(vmin=-1.5, vcenter=0, vmax=1.5)
c = ax.contourf(X,Y,F(0), norm=norm)

def animate(t):
    global c
    c.remove()
    c = ax.contourf(X,Y,F(t), norm=norm)
    return c


anim = FuncAnimation(fig, animate, frames=np.linspace(0,10,200), interval=30)

plt.show()
