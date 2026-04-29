import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation

N = 100
L = 3
# R = lambda x: 0.05 if x <= 2 else 0.03
# v = lambda x: 1 if x <= 2 else 2
v = lambda x: 1 if x < 1.7 and x > 1.3 else 2
R = lambda x: 1/v(x)*0.03

points = [np.array([L/N*x,0]) for x in range(N)]
velocities = np.zeros((N,))

a0 = lambda t: 1 if t < 0.2 else 0
# v0 = lambda t: 5*np.sin(2*np.pi/0.5*t) if t < 0.5 else 0
v0 = lambda t: 5*np.sin(2*np.pi/0.5*t)

u0 = lambda t: 0.3*np.sin(2*np.pi/0.5*t) if t < 4 else 0

mu = 0.0

dx = L/(N-1)
ddx = dx**2
def update(t, dt):
    points[0][1] = u0(t)
    for i in range(1,N-1):
        points[i][1] += velocities[i]*dt

    # ddu2 = -2*points[1][1] + points[3][1]
    # a2 = ddu2/ddx
    # velocities[1] += a2*dt

    for i in range(1,N-1):
        ddu = -2*points[i][1] + points[i-1][1] + points[i+1][1]
        a = v(i*dx)**2*ddu/ddx - velocities[i]*mu
        velocities[i] += a*dt

    # dduN = -2*points[-1][1] + points[-2][1]
    # aN = dduN/ddx
    velocities[-1] = velocities[-2]

    return points, velocities


fig = plt.figure()
ax = fig.add_subplot()
ax.set_xlim(-1, L+1)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect("equal")

cs = [Circle(p, R(p[0])) for p in points]

for c in cs:
    ax.add_patch(c)

dt = 0.01

def animate(i):
    global points, velocities, cs
    t = i*dt
    points, velocities = update(t, dt)
    for c,p in zip(cs, points):
        c.set_center(p)
    return cs


anim = FuncAnimation(fig, animate, frames=100000, interval=dt*1000)

plt.show()
