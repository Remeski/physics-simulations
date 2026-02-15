# Example file showing a basic pygame "game loop"
import pygame
import numpy as np

# space = pause
# + = zooms in (also scroll)
# - = zooms out
# m = toggles follow com
# r = restart

screen_width = 2400
screen_height = 1200
aspect_ratio = screen_width / screen_height

g = 10**3

# m = [50.0, 50.0, 50.0, 50.0]
# r_start = [
#     np.array([0.0, 0.0]),
#     np.array([100.0, 0.0]),
#     np.array([200.0, 50.0]),
#     np.array([-200.0, -10.0]),
# ]
# v_start = [
#     np.array([-10.0, 20.0]),
#     np.array([0.0, 10.0]),
#     np.array([10.0, -50.0]),
#     np.array([0.0, 30.0]),
# ]

# m = []
# r_start = []
# v_start = []

m = [10.0, 1.0, 10.0]
r_start = [np.array([0.0, 0.0]), np.array([100.0, 0.0]), np.array([-200.0, -50.0])]
v_start = [np.array([0.0, 0.0]), np.array([0.0, np.sqrt(g*m[0]/100.0)]), 5.0*np.array([-1, 5])]

static = [False, False, False]

rho = 30.0

trail_length = 100
trail_size = 0.1
show_trails = True
show_com = True

trail_colors = ["#aa0000", "#0000aa", "#aa00aa", "#aabb00"]
colors = ["red", "blue", "purple", "yellow"]
# colors = []
# trail_colors = []

# plate_size = 10
# # Negative side
# for y in range(plate_size):
#     m.append(-10.0)
#     r_start.append(np.array([-50.0, -30.0 + y * (60.0 / plate_size)]))
#     v_start.append(np.array([0.0, 0.0]))
#     static.append(True)
#     colors.append("blue")
#     trail_colors.append("white")
# # Positive side
# for y in range(plate_size):
#     m.append(10.0)
#     r_start.append(np.array([50.0, -30.0 + y * (60.0 / plate_size)]))
#     v_start.append(np.array([0.0, 0.0]))
#     static.append(True)
#     colors.append("red")
#     trail_colors.append("white")
#
# r_start.append(np.array([10.0, -10.0]))
# v_start.append(np.array([0.0, 0.0]))
# m.append(-10.0)
# colors.append("blue")
# trail_colors.append("#0000aa")
# static.append(False)
#
# r_start.append(np.array([0.0, 2.0]))
# v_start.append(np.array([0.0, 0.0]))
# m.append(-10.0)
# colors.append("blue")
# trail_colors.append("#0000aa")
# static.append(False)
#
# r_start.append(np.array([-10.0, 10.0]))
# v_start.append(np.array([0.0, 0.0]))
# m.append(10.0)
# colors.append("red")
# trail_colors.append("#aa0000")
# static.append(False)
#
# r_start.append(np.array([-20.0, -5.0]))
# v_start.append(np.array([0.0, 0.0]))
# m.append(10.0)
# colors.append("red")
# trail_colors.append("#aa0000")
# static.append(False)

n = len(m)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

base_font = pygame.font.Font(None, 32)


def translate_coords(pos, game_scale, game_x, game_y):
    x_scale = game_scale
    y_scale = game_scale / aspect_ratio
    return (
        ((pos[0] - game_x) / x_scale + 0.5) * screen_width,
        ((-pos[1] + game_y) / y_scale + 0.5) * screen_height,
    )


def translate_size(x, game_scale):
    return np.max((np.abs(x) / game_scale * screen_width, 2))


# regions = [{name: "name", start: (x,y), end: (x,y)}]
def get_mouse_region(pos, regions):
    for region in regions:
        if pos[0] >= region.start[0] and pos[0] <= region.end[0] and pos[1] >= region.start[1] and pos[1] <= region.end[1]:
            return region.name
    return False


def index_combinations(n):
    for i in range(n):
        for j in range(i + 1, n):
            yield (i, j)


def start():
    running = True
    paused = True
    follow_com = False
    ticks_last_frame = 0

    game_scale = 100
    game_x = 0
    game_y = 0

    mouse_dragging = False
    mouse_lastpos = pygame.mouse.get_pos()
    mouse_sens = 0.1

    trail_updatetime = 0.1  # in seconds
    trail_last = 0

    r = np.copy(r_start)
    v = np.copy(v_start)
    trails = [[] for i in range(n)]

    com_trail = []

    while running:
        t = pygame.time.get_ticks()

        # deltaTime in seconds.
        dt = (t - ticks_last_frame) / 1000
        ticks_last_frame = t

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == ord("r"):
                    r = np.copy(r_start)
                    v = np.copy(v_start)
                    trails = [[] for i in range(n)]

                    com_trail = []
                elif event.key == ord("q"):
                    running = False
                elif event.key == ord("m"):
                    follow_com = not follow_com
                elif event.key == pygame.K_MINUS:
                    game_scale += 50
                elif event.key == pygame.K_PLUS and game_scale > 10:
                    game_scale -= 50
                elif event.key == pygame.K_SPACE:
                    paused = not paused

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_dragging = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()

                if mouse_dragging:
                    delta = (
                        mouse_pos[0] - mouse_lastpos[0],
                        mouse_pos[1] - mouse_lastpos[1],
                    )
                    game_x -= dt * game_scale * mouse_sens * delta[0]
                    game_y += dt * game_scale / aspect_ratio * mouse_sens * delta[1]
                mouse_lastpos = mouse_pos

            elif event.type == pygame.MOUSEWHEEL:
                if event.y == 1 and game_scale > 10:
                    game_scale -= 10
                if event.y == -1:
                    game_scale += 10

            elif event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        # Draw x ticks
        for x in range(-game_scale, game_scale + 1):
            pygame.draw.line(
                screen,
                "gray",
                start_pos=translate_coords([x, -0.1], game_scale, game_x, game_y),
                end_pos=translate_coords([x, 0.1], game_scale, game_x, game_y),
            )
        # Draw y ticks
        for y in range(-game_scale, game_scale + 1):
            pygame.draw.line(
                screen,
                "gray",
                start_pos=translate_coords([-0.1, y], game_scale, game_x, game_y),
                end_pos=translate_coords([0.1, y], game_scale, game_x, game_y),
            )

        if not paused:
            for i, j in index_combinations(n):
                rij = r[j] - r[i]
                rij_norm = np.linalg.norm(rij)
                v[i] += (g * m[j] * rij / rij_norm**3) * dt
                # v[i] -= (g * m[i] * m[j] * rij / rij_norm**3) * dt
                v[j] -= (g * m[i] * rij / rij_norm**3) * dt
                # v[j] += (g * m[j] * m[i] * rij / rij_norm**3) * dt

            for i in range(n):
                if not static[i]:
                    r[i] += v[i] * dt

        com = 1 / np.sum(m) * np.dot(r.T, m)

        if follow_com:
            game_x = com[0]
            game_y = com[1]

        if show_trails:
            for i in range(n):
                for pos in trails[i]:
                    if m[i] != 0:
                        pygame.draw.circle(
                            screen,
                            trail_colors[i],
                            translate_coords(pos, game_scale, game_x, game_y),
                            translate_size(trail_size, game_scale),
                        )

            # Trail update
            if trail_last >= trail_updatetime:
                trail_last = 0
                for i in range(n):
                    trails[i] = [np.copy(r[i]), *trails[i][:trail_length]]

                com_trail = [com, *com_trail[:trail_length]]
            trail_last += dt

        for i in range(n):
            if m[i] != 0:
                pygame.draw.circle(
                    screen,
                    colors[i],
                    translate_coords(r[i], game_scale, game_x, game_y),
                    translate_size(m[i] / rho, game_scale),
                )

        if show_com:
            # Draw com trail
            for pos in com_trail:
                pygame.draw.circle(
                    screen,
                    "gray",
                    translate_coords(pos, game_scale, game_x, game_y),
                    translate_size(trail_size, game_scale),
                )

            pygame.draw.circle(
                screen,
                "gray",
                translate_coords(com, game_scale, game_x, game_y),
                translate_size(0.5, game_scale),
            )

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(120)


start()

pygame.quit()
