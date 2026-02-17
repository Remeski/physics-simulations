import numpy as np
import pygame

# This is (tries to be) a fluid simulator based on the work of Jos Stam.
# https://graphics.cs.cmu.edu/nsp/course/15-464/Fall09/papers/StamFluidforGames.pdf

DRAW_GRID = False
DRAW_VELOCIIES = False
VELOCITY_SCALE = 10
N = 100
DT_SCALE = 1000

DENSITY_DRAW_AMOUNT = 0.1
SOURCE_DRAW_AMOUNT = 0.1
FORCE_DRAW_AMOUNT = 0.1
VELOCITY_DRAW_AMOUNT = 0.1

VISCOSITY = 0.01
DENSITY_DIFFUSE = 0.0

GAUSS_SEIDEL_ITER = 20

def IX(x, y):
    return x + y * (N+2)

def coord_space(default=0.0, pad_value=0.0):
    r = [default for _ in range((N + 2) * (N + 2))]
    for i in range(0,N+2):
        r[IX(0,i)] = pad_value
        r[IX(N+1,i)] = pad_value
        r[IX(i,0)] = pad_value
        r[IX(i,N+1)] = pad_value

    return r

def density_to_color(index, densities):
    density = densities[index]
    value = np.clip(density, 0.0, 1.0) * 255
    return (value, 0.0, 0.0)

def set_bnd(n, b, x):
    for i in range(1, n):
        x[IX(0, i)] = -x[IX(1, i)] if b == 1 else x[IX(1, i)]
        x[IX(n + 1, i)] = -x[IX(n, i)] if b == 1 else x[IX(n, i)]
        x[IX(i, 0)] = -x[IX(i, 1)] if b == 2 else x[IX(i, 1)]
        x[IX(i, n + 1)] = -x[IX(i, n)] if b == 2 else x[IX(i, n)]
    x[IX(0, 0)] = 0.5 * (x[IX(0, 1)] + x[IX(1, 0)])
    x[IX(n + 1, 0)] = 0.5 * (x[IX(n + 1, 1)] + x[IX(n, 0)])
    x[IX(0, n + 1)] = 0.5 * (x[IX(0, n)] + x[IX(1, n + 1)])
    x[IX(n + 1, n + 1)] = 0.5 * (x[IX(n, n + 1)] + x[IX(n + 1, n)])
    return x


def diffuse(n, b, x, x0, diff, dt):
    a = diff * dt * n**2

    # Gauss-Seidel relaxation for solving linear systems of eqs.
    for _ in range(GAUSS_SEIDEL_ITER):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                x[IX(i, j)] = (x0[IX(i, j)] + a * (x[IX(i - 1, j)] + x[IX(i + 1, j)] + x[IX(i, j - 1)] + x[IX(i, j + 1)])) / (1 + 4 * a)
        x = set_bnd(n, b, x)

    # return x


# Updates field based on velocity. 
# This comes from Navier-Stokes equations' term that involves the material derivative (not totally sure; future me can fact check)
def advect(n, b, x, x0, u, v, dt):
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            # Backtrace
            sx = i - dt * u[IX(i, j)]
            sy = j - dt * v[IX(i, j)]

            if sx < 0.5:
                sx = 0.5
            if sx > n + 0.5:
                sx = n + 0.5
            if sy < 0.5:
                sy = 0.5
            if sy > n + 0.5:
                sy = n + 0.5
            # Indexes
            i0 = int(sx)
            j0 = int(sy)

            # Distances to neighboring cells
            w0 = sx - i0
            w1 = 1 - w0
            w2 = sy - j0
            w3 = 1 - w2

            # Linearly interpolate property of neighboring cells
            x[IX(i, j)] = w1 * (w3 * x0[IX(i0, j0)] + w2 * x0[IX(i0, j0 + 1)]) + w0 * (w3 * x0[IX(i0 + 1, j0)] + w2 * x0[IX(i0 + 1, j0 + 1)])
    set_bnd(n, b, x)


# force div = 0 i.e. make the field incompressible
# involves solving Poisson eq. I have no idea what this is actually doing (as a 1st year physics student)
def project(n, u, v, p, d):
    # d = copy.deepcopy(v)
    # p = copy.deepcopy(u)

    h = 1 / n

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            d[IX(i, j)] = -0.5 * h * (u[IX(i + 1, j)] - u[IX(i - 1, j)] + v[IX(i, j + 1)] - v[IX(i, j - 1)])
            p[IX(i, j)] = 0.0
    d = set_bnd(n, 0, d)
    p = set_bnd(n, 0, p)

    for _ in range(GAUSS_SEIDEL_ITER):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                p[IX(i, j)] = (d[IX(i, j)] + p[IX(i - 1, j)] + p[IX(i + 1, j)] + p[IX(i, j - 1)] + p[IX(i, j + 1)]) / 4
        p = set_bnd(n, 0, p)

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            u[IX(i, j)] -= 0.5 * (p[IX(i + 1, j)] - p[IX(i - 1, j)]) / h
            v[IX(i, j)] -= 0.5 * (p[IX(i, j + 1)] - p[IX(i, j - 1)]) / h
    u = set_bnd(n, 1, u)
    v = set_bnd(n, 2, v)
    # return u, v

def add_source(n, densities, sources, dt):
    for i in range(1,n+1):
        for j in range(1,n+1):
            densities[IX(i,j)] += sources[IX(i,j)]*dt
    # return densities

def add_forces(n, u, v, forces, dt):
    for i in range(1,n+1):
        for j in range(1,n+1):
            u[IX(i,j)] += forces[0][IX(i,j)]*dt
            v[IX(i,j)] += forces[1][IX(i,j)]*dt
    # return u,v

# for debug
def print_table(x):
    for i in range(0,N+2):
        for j in range(0,N+2):
            print(f"{x[IX(i,j)]} ", end="")
        print("")

pygame.init()
screen_size = 1000
grid_spacing = screen_size // N

screen = pygame.display.set_mode((screen_size, screen_size))
clock = pygame.time.Clock()
running = True
paused = True

densities = coord_space()
densities0 = coord_space()
u = coord_space()
v = coord_space()
u0 = coord_space()
v0 = coord_space()


# for i in range(1,N+1):
#     for j in range(1,N+1):
#         if j > 0 and j < N:
#             u[IX(i,j)] = 1.0

sources = coord_space()
forces = (coord_space(default=0), coord_space())

ticks_last_frame = 0

velocity_draw_mode = False
density_draw_mode = False
source_draw_mode = False
force_draw_mode = False

mouse_dragging = False
mouse_lastpos = pygame.mouse.get_pos()

while running:
    t = pygame.time.get_ticks()
    dt = (t - ticks_last_frame) / DT_SCALE

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_dragging:
                delta = (
                    mouse_pos[0] - mouse_lastpos[0],
                    mouse_pos[1] - mouse_lastpos[1],
                )
                i = mouse_pos[0] // grid_spacing + 1
                j = mouse_pos[1] // grid_spacing + 1
                if velocity_draw_mode:
                    u[IX(i, j)] += VELOCITY_DRAW_AMOUNT * delta[0]
                    v[IX(i, j)] += VELOCITY_DRAW_AMOUNT * delta[1]
                if density_draw_mode:
                    densities[IX(i, j)] += DENSITY_DRAW_AMOUNT
                if source_draw_mode:
                    sources[IX(i, j)] += SOURCE_DRAW_AMOUNT
                # if force_draw_mode:
                    # forces[0][IX(i,j)] += FORCE_DRAW_AMOUNT

            mouse_lastpos = mouse_pos

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_dragging = True
            i = mouse_pos[0] // grid_spacing + 1
            j = mouse_pos[1] // grid_spacing + 1
            if density_draw_mode:
                densities[IX(i, j)] += DENSITY_DRAW_AMOUNT
            if source_draw_mode:
                sources[IX(i, j)] += SOURCE_DRAW_AMOUNT
            if force_draw_mode:
                # forces[0][IX(i,j)] += FORCE_DRAW_AMOUNT
                u[IX(i,j)] += 1.0
            print(f"""at ({i}, {j}):
    density: {densities[IX(i,j)]},
    source: {sources[IX(i,j)]},
    velocities: ({u[IX(i,j)]}, {v[IX(i,j)]}),
    force: ({forces[0][IX(i,j)]}, {forces[1][IX(i,j)]}
                  """)

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_dragging = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
                print("Now running!" if not paused else "Paused")
            elif event.key == ord("v"):
                velocity_draw_mode = not velocity_draw_mode
                density_draw_mode = False
                source_draw_mode = False
                force_draw_mode = False
                print(f"Velocity draw mode: {velocity_draw_mode}")
            elif event.key == ord("d"):
                density_draw_mode = not density_draw_mode
                velocity_draw_mode = False
                source_draw_mode = False
                force_draw_mode = False
                print(f"Density draw mode: {density_draw_mode}")
            elif event.key == ord("s"):
                source_draw_mode = not source_draw_mode
                velocity_draw_mode = False
                density_draw_mode = False
                force_draw_mode = False
                print(f"Source draw mode: {source_draw_mode}")
            elif event.key == ord("f"):
                force_draw_mode = not force_draw_mode
                velocity_draw_mode = False
                density_draw_mode = False
                source_draw_mode = False
                print(f"Force draw mode: {force_draw_mode}")

    if not paused:
        # Update densities
        add_source(N, densities, sources, dt)

        densities, densities0 = densities0, densities
        diffuse(N, 0, densities, densities0, DENSITY_DIFFUSE, dt)

        densities, densities0 = densities0, densities
        advect(N, 0, densities, densities0, u, v, dt)

        add_forces(N, u, v, forces, dt)

        u, u0, v, v0 = u0, u, v0, v

        diffuse(N, 1, u, u0, VISCOSITY, dt)
        diffuse(N, 2, v, v0, VISCOSITY, dt)

        u, u0, v, v0 = u0, u, v0, v
        project(N, u, v, u0, v0)

        u, u0, v, v0 = u0, u, v0, v
        advect(N, 1, u, u0, u0, v0, dt)
        advect(N, 2, v, v0, u0, v0, dt)

        u, u0, v, v0 = u0, u, v0, v
        project(N, u, v, u0, v0)

    # Draw densities
    for i in range(1,N+1):
        for j in range(1,N+1):
            pygame.draw.rect(
                screen,
                density_to_color(IX(i, j), densities),
                (
                    (i-1) * grid_spacing,
                    (j-1) * grid_spacing,
                    grid_spacing,
                    grid_spacing,
                ),
                width=0,
            )

    # Draw grid
    if DRAW_GRID:
        for i in range(int(screen_size / grid_spacing)):
            pygame.draw.line(
                screen,
                "gray",
                start_pos=(i * grid_spacing, 0.0),
                end_pos=(i * grid_spacing, screen_size),
            )
        for j in range(int(screen_size / grid_spacing)):
            pygame.draw.line(
                screen,
                "gray",
                start_pos=(0.0, j * grid_spacing),
                end_pos=(screen_size, j * grid_spacing),
            )
    # Draw velocities
    if DRAW_VELOCIIES:
        for i in range(1,N+1):
            for j in range(1,N+1):
                scale = VELOCITY_SCALE
                start = ((i-1 + 0.5) * grid_spacing, (j-1 + 0.5) * grid_spacing)
                end = (start[0] + scale * u[IX(i, j)], start[1] + scale * v[IX(i, j)])
                pygame.draw.line(screen, "blue", start_pos=start, end_pos=end)

    pygame.display.flip()
    clock.tick(240)

pygame.quit()
