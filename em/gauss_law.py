from matplotlib.patches import Arrow, Circle
import matplotlib.pyplot as plt
import numpy as np
import itertools
import matplotlib.animation as animation

FLUX_TEXTS = False
N = 30
EFIELD_SCALE = 10
COLOR_SCALE = (-1,1)
CHARGE_MODIFY_SENSITIVITY = 0.08
MOUSE_MOVING_CHARGE = 0 #-0.5

fig,ax = plt.subplots()
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])

xs = np.linspace(0,1,N)
ys = np.linspace(0,1,N)
coords = list(itertools.product(list(range(0,N)), list(range(0,N))))

X,Y = np.meshgrid(xs, ys)

rho = np.zeros(X.shape)

rho_moving = np.zeros(X.shape)

hs = np.zeros((X.shape[0] + 1, X.shape[1]))
vs = np.zeros((X.shape[0], X.shape[1] + 1))

U = np.zeros(X.shape)
V = np.zeros(X.shape)

# plates
# for x in range(15,45):
#     rho[19,x] = 0.5
#     rho[39,x] = -0.5

# dipole
# rho[20,30] = 1.0
# rho[40,30] = -1.0


pressing = False
sign = 1
def mouse_press(event):
    global pressing, sign
    if event.button == 1:
        sign = 1
        pressing = True
    elif event.button == 3:
        sign = -1
        pressing = True

def mouse_release(event):
    global pressing, sign
    pressing = False
    sign = 1

def mouse_move(event):
    if event.inaxes:
        ax = event.inaxes
        inv = ax.transAxes.inverted()
        ax_coords = inv.transform((event.x, event.y))
        x,y = ax_coords * N
        x,y = int(x),int(y)

        if MOUSE_MOVING_CHARGE != 0.0:
            global rho,rho_moving
            rho -= rho_moving
            rho_moving = np.zeros(X.shape)
            rho_moving[y,x] = MOUSE_MOVING_CHARGE
            rho += rho_moving
        if pressing and event.inaxes:
            rho[y,x] += sign * CHARGE_MODIFY_SENSITIVITY


def update_field():
    for (x,y) in coords:
        S = rho[x,y]/4 - (-hs[x,y] + hs[x+1,y] - vs[x,y] + vs[x,y+1])/4
        hs[x,y] -= S
        hs[x+1,y] += S
        vs[x,y] -= S
        vs[x,y+1] += S

def format_value(v):
    return str(round(v, 2))


def update_texts(hs_texts, vs_texts):
    for x in range(0,N+1):
        for y in range(0,N):
            hs_texts[x,y].set_text(format_value(hs[x,y]))
    for x in range(0,N):
        for y in range(0,N+1):
            vs_texts[x,y].set_text(format_value(vs[x,y]))


def update(frame):
    update_field()
    if FLUX_TEXTS: update_texts(hs_texts, vs_texts)

    mesh.set_array(rho)

    for (x,y) in coords:
        V[x,y] = hs[x,y]+hs[x+1,y]
        U[x,y] = vs[x,y]+vs[x,y+1]
    field.set_UVC(U ,V)

    return (mesh, *hs_texts, *vs_texts, field)

mesh = ax.pcolormesh(X, Y, rho, vmin=COLOR_SCALE[0], vmax=COLOR_SCALE[1], cmap="bwr")
field = ax.quiver(X, Y, U, V, scale=EFIELD_SCALE, headlength=1, headaxislength=1)

fig.canvas.mpl_connect("button_press_event", mouse_press)
fig.canvas.mpl_connect("motion_notify_event", mouse_move)
fig.canvas.mpl_connect("button_release_event", mouse_release)

hs_texts = dict()
vs_texts = dict()

if FLUX_TEXTS:
    for x in range(0,N+1):
        for y in range(0,N):
            hs_texts[x,y] = ax.text((x-0.5)/(N-1), y/(N-1), format_value(hs[x,y]), horizontalalignment="center", verticalalignment="center")
    for x in range(0,N):
        for y in range(0,N+1):
            vs_texts[x,y] = ax.text((x)/(N-1), (y-0.5)/(N-1), format_value(vs[x,y]), horizontalalignment="center", verticalalignment="center")

anim = animation.FuncAnimation(fig=fig, func=update, frames=100, interval=10)

plt.show()
