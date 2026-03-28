import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow
from matplotlib.animation import FuncAnimation

ARROW_SCALE = 0.2

L = 3
pendulum_origin = np.array([0,L])

theta = 0.0  # rad
omega = 0  # rad/s

m = 1.0  # kg
I = m*L**2  # kgm^2

g = 9.81  # m/s^2
mu = 1

F = 3
ext_omega = 1.808
external_force = lambda t,theta: F*np.sin(ext_omega * t)
external_torque = lambda t,theta: external_force(t,theta)*np.cos(theta)*L

def xy(theta):
    return pendulum_origin + np.array([L*np.sin(theta), -L*np.cos(theta)])


T = np.inf
t_prev = 0
A = 0
def update(t, dt):
    global theta, omega, T, checked, t_prev, A
    torque = -np.sin(theta)*g*L - mu*omega + external_torque(t,theta)
    last_omega = omega
    omega += torque/I*dt
    theta += omega*dt
    if omega*last_omega < 0:
        T = (t-t_prev)*2
        A = abs(np.sin(theta)*L)
        t_prev = t


fig = plt.figure()
ax = fig.add_subplot(xlim=(-1.15*L,1.15*L), ylim=(-1,2*L+1), aspect="equal")

ball = Circle(xy(theta), 0.1)
ax.add_patch(ball)
line_data = lambda theta: (np.linspace(0,xy(theta)[0],20), np.linspace(L,xy(theta)[1], 20))
line, = ax.plot(*line_data(theta))
arr = Arrow(*xy(theta), external_force(0,0)*ARROW_SCALE, 0, width=0.1, color="r")
ax.add_patch(arr)


def text_label():
    global maximum, minimum
    return f"$\\omega_\\text{{mitattu}} = {round(2*np.pi/T, 3)}$\n$A_\\text{{mitattu}} = {round(A, 3)}$\n$\\omega_\\text{{resonanssi}} = {round(np.sqrt(g/L),3)}$\n$\\omega_\\text{{ulkoinen}} = {ext_omega}$"


label = ax.text(-L,1.7*L,text_label())

fps = 30
dt = 1/fps

def animate(t):
    global theta, ball, line,label,arr
    update(t, dt)
    ball.set_center(xy(theta))
    line.set_data(*line_data(theta))
    label.set_text(text_label())
    arr.set_data(*xy(theta),external_force(t,dt)*ARROW_SCALE, 0)
    return ball,line,label,arr


anim = FuncAnimation(fig, animate, frames=np.linspace(0,40,40*fps), interval=1000/30)

plt.show()
