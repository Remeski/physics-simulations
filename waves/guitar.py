import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import scipy as sp

N = 200
L = 1  # m
v = 0.5  # m/s

N_x = 300
N_t = 300

xs = np.linspace(0, L, N_x)
ts = np.linspace(0, 10,N_t)

X,T = np.meshgrid(xs, ts)

M = L/3
A = 0.2

def f(x):
    return A/M*x if x < M else -A/(L-M)*(x-M) + A

def find_bn(f, n, N_start, N_end):
    b_n = 2/L * sp.integrate.quad(lambda x: f(x)*np.sin(np.pi*n/L * x), 0, L)[0]
    return b_n

def u(x,t):
    sol_tot = np.zeros((N_x,N_t))
    sols = []
    for n in range(0,N):
        b_n = find_bn(f, n, 0, N)
        sol = b_n * np.cos(np.pi*v*n/L * t)*np.sin(np.pi*n/L * x)
        sols.append(sol)
        sol_tot += sol
    return sol_tot, sols


U, sines = u(X,T)

fig = plt.figure()
ax = fig.add_subplot()

ax.set_ylim(-A,A)

artists = []

# plt.plot(xs, np.vectorize(f)(xs))
# plt.show()

N_waves = 5
string = ax.plot(ts, U[0,:], color="0")
waves = [ax.plot(ts, sines[n][0,:]) for n in range(0,N_waves)]

def animate(t_index):
    global string, waves
    ax.clear()
    ax.set_ylim(-A,A)
    string = ax.plot(ts, U[t_index,:], color="0")
    waves = [ax.plot(ts, sines[n][t_index,:]) for n in range(0,N_waves)]

    return string, *waves


anim = FuncAnimation(fig=fig, func=animate, frames=100, interval=100)

plt.show()
