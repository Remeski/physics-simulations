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

def fourier(f, x, n):
    r = fourier_factor(f, 0) * x

    for i in range(1,n+1):
        r += fourier_factor(f, i).dot(np.array([np.cos(i*x), np.sin(i*x)]))

    return r

xs = np.linspace(-np.pi, np.pi, 100)

plt.plot(xs, np.vectorize(square_wave)(xs))

plt.plot(xs, fourier(square_wave, xs, 1))
plt.plot(xs, fourier(square_wave, xs, 10))
plt.plot(xs, fourier(square_wave, xs, 100))

plt.show()
