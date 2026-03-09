import scipy as sp
import numpy as np
import matplotlib.pyplot as plt

def fourier_factor(f, n):
    s = 1/(np.pi)
    if n == 0:
        return np.array([s*sp.integrate.quad(lambda x: f(x), -np.pi, np.pi)[0]])

    an = sp.integrate.quad(lambda x: f(x)*np.cos(n*x), -np.pi, np.pi, limit=500)
    bn = sp.integrate.quad(lambda x: f(x)*np.sin(n*x), -np.pi, np.pi, limit=500)
    return np.array([s*an[0], s*bn[0]])

def square_wave(x):
    if x < 0.0:
        return -1
    else:
        return 1

def fourier(f, x, n, factors=[]):
    fact = fourier_factor(f, 0)
    factors.append(fact)
    r = fact * x

    for i in range(1,n+1):
        fact = fourier_factor(f, i)
        factors.append(fact)
        r += fact.dot(np.array([np.cos(i*x), np.sin(i*x)]))

    return r

ts = np.linspace(0, 2*np.pi, 200)

x = lambda t: np.cos(t)*np.sin(2*t)
y = lambda t: np.sin(t)*np.sin(2*t)/2

fig,ax = plt.subplots()
ax.scatter(x(ts), y(ts))

n = 3

factors = []

x_fourier = fourier(x, ts, n, factors=factors)
y_fourier = fourier(y, ts, n, factors=factors)

ax.scatter(x_fourier, y_fourier)

ax.set_aspect("equal")

plt.show()
