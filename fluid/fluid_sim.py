import numpy as np
import pygame
import random
import copy
import sys

# This is (tries to be) a fluid simulator based on the work of Jos Stam.
# https://graphics.cs.cmu.edu/nsp/course/15-464/Fall09/papers/StamFluidforGames.pdf

DRAW_GRID = False
DRAW_VELOCIIES = False
N = 50
DT_SCALE = 1000

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


def diffuse(n, b, x0, diff, dt):
    a = diff * dt * n**2
    x = copy.deepcopy(x0)

    # Gauss-Seidel relaxation for solving linear systems of eqs.
    for _ in range(20):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                x[IX(i, j)] = (x0[IX(i, j)] + a * (x[IX(i - 1, j)] + x[IX(i + 1, j)] + x[IX(i, j - 1)] + x[IX(i, j + 1)])) / (1 + 4 * a)
        x = set_bnd(n, b, x)

    return x


def density_to_color(index, densities):
    density = densities[index]
    # print(density)
    # densities_max = np.max(densities)
    # densities_min = np.min(densities)
    densities_max = 1.0
    densities_min = 0.0
    # if density == 0.0:
    #     value = 0.0
    # else:
    value = np.clip(density, 0.0, 1.0) * 255
    return (value, 0.0, 0.0)
    # color = np.array(colorsys.hls_to_rgb(value, 1.0, 1.0))
    # return list(color * 255)

# Updates field based on velocity. 
# This comes from Navier-Stokes equations' term that involves the material derivative (not totally sure; future me can fact check)
def advect(n, b, x0, u, v, dt):
    x = copy.deepcopy(x0)

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
    return set_bnd(n, b, x)


# force div = 0 i.e. make the field incompressible
# involves solving Poisson eq. I have no idea what this is actually doing (as a 1st year physics student)
def project(n, u, v):
    d = copy.deepcopy(v)
    p = copy.deepcopy(u)

    h = 1 / n

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            d[IX(i, j)] = -0.5 * h * (u[IX(i + 1, j)] - u[IX(i - 1, j)] + v[IX(i, j + 1)] - v[IX(i, j - 1)])
            p[IX(i, j)] = 0.0
    d = set_bnd(n, 0, d)
    p = set_bnd(n, 0, p)

    for _ in range(20):
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
    return u, v

def add_source(n, densities, sources, dt):
    for i in range(1,n+1):
        for j in range(1,n+1):
            densities[IX(i,j)] += sources[IX(i,j)]*dt
    return densities

def add_forces(n, u, v, forces, dt):
    for i in range(1,n+1):
        for j in range(1,n+1):
            u[IX(i,j)] += forces[0][IX(i,j)]*dt
            v[IX(i,j)] += forces[1][IX(i,j)]*dt
    return u,v

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

densities = coord_space(default=0.0)
u = coord_space()
v = coord_space()


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
                    u[IX(i, j)] += 0.01 * delta[0]
                    v[IX(i, j)] += 0.01 * delta[1]

            mouse_lastpos = mouse_pos

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_dragging = True
            i = mouse_pos[0] // grid_spacing + 1
            j = mouse_pos[1] // grid_spacing + 1
            if density_draw_mode:
                densities[IX(i, j)] += 0.1
                print("updating density")
            if source_draw_mode:
                sources[IX(i, j)] += 0.1
                print("updating density")
            if force_draw_mode:
                forces[0][IX(i,j)] += 1.0
            print(f"density at {(i,j)} is {densities[IX(i,j)]}")
            print(f"source at {(i,j)} is {sources[IX(i,j)]}")
            print(f"force at {(i,j)} is {forces[0][IX(i,j)]},{forces[1][IX(i,j)]}")

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_dragging = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
                print("Now running!" if not paused else "Paused")
            elif event.key == ord("v"):
                velocity_draw_mode = not velocity_draw_mode
            elif event.key == ord("d"):
                density_draw_mode = not density_draw_mode
            elif event.key == ord("s"):
                source_draw_mode = not source_draw_mode
            elif event.key == ord("f"):
                force_draw_mode = not force_draw_mode
            print(f"Density draw mode: {density_draw_mode}")
            print(f"Source draw mode: {source_draw_mode}")
            print(f"Force draw mode: {force_draw_mode}")
            print(f"Velocity draw mode: {velocity_draw_mode}")

    if not paused:
        # Update densities
        densities = add_source(N, densities, sources, dt)
        densities = diffuse(N, 0, densities, 0.0, dt)
        densities = advect(N, 0, densities, u, v, dt)

        u,v = add_forces(N, u, v, forces, dt)

        u = diffuse(N, 1, u, 0.0, dt)
        v = diffuse(N, 2, v, 0.0, dt)
        u, v = project(N, u, v)
        #
        u0 = copy.deepcopy(u)
        v0 = copy.deepcopy(v)
        u = advect(N, 1, u, u0, v0, dt)
        v = advect(N, 2, v, u0, v0, dt)
        u, v = project(N, u, v)
        # print(np.array(densities))

        # total_dens = np.sum(densities)
        # print(f"total density is {total_dens}")

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
                scale = 50.0
                start = ((i-1 + 0.5) * grid_spacing, (j-1 + 0.5) * grid_spacing)
                end = (start[0] + scale * u[IX(i, j)], start[1] + scale * v[IX(i, j)])
                pygame.draw.line(screen, "blue", start_pos=start, end_pos=end)

    pygame.display.flip()
    clock.tick(240)

pygame.quit()
