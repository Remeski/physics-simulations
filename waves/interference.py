# from matplotlib.patches import Arrow, Circle
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.colors import TwoSlopeNorm

fig = plt.figure()
ax = fig.add_subplot()

density = 100
L = 2

X,Y = np.meshgrid(np.linspace(-L,L,density), np.linspace(-L,L,density))

lambd = 0.5
k = 6/lambd  # m^-1
v = 0.1

N = 20
l = 3
start_x = -l/2
end_x = l/2
y0 = -1.5

omega = lambda k: v*k

r = lambda x,y: np.sqrt(x**2 + y**2)

A0 = 1
A = lambda r: A0/r

pulse = lambda offset,k: lambda x0,y0,t: A(r(X-x0,Y-y0))*np.cos(k*r(X-x0,Y-y0)-omega(k)*t)

F1 = lambda t: pulse(0,k)(-3/k,-1.0,t)
F2 = lambda t: pulse(0,k)(3/k,-1.0,t)


dx = (end_x-start_x)/(N-1) if N > 1 else 0
positions = [(start_x + i*dx,y0) for i in range(N)]

def F(t):
    return np.sum(np.array([pulse(0,k)(x0,y0,t) for (x0,y0) in positions]), axis=0)


print(F(0))
# F = lambda t: F1(t) + F2(t)


norm = TwoSlopeNorm(vmin=-1.5*A0, vcenter=0, vmax=1.5*A0)
field = ax.pcolormesh(X, Y, F(0), norm=norm, cmap="plasma")

t_label = ax.text(-2,2, "t = ")

delta = 100
t_end = 10  # s
Nt = int(t_end*1000/delta)

def animate(i):
    global field
    t = i*delta/1000

    field.set_array(F(t))

    t_label.set_text(f"t = {t}")

    return t_label, field


ani = animation.FuncAnimation(fig, animate, frames=Nt, interval=delta)

plt.show()
