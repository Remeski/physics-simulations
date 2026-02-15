# Example file showing a basic pygame "game loop"
import pygame
import numpy as np

# pygame setup
pygame.init()
screen = pygame.display.set_mode((400, 700))
clock = pygame.time.Clock()
running = True

ball_pos = np.array([200, 100])
ball_velocity = np.array([0, 0])

k = 1.1

gravity = 9.81 * 10

getTicksLastFrame = 0

while running:
    t = pygame.time.get_ticks()
    # deltaTime in seconds.
    deltaTime = (t - getTicksLastFrame) / 1000
    getTicksLastFrame = t

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    pygame.draw.line(screen, "black", [0, 355], [400, 355], 5)

    ball_velocity = ball_velocity + np.array([0, 1]) * gravity * deltaTime

    ball_pos = ball_pos + ball_velocity * deltaTime

    if ball_pos[1] > 300:
        ball_velocity = ball_velocity + np.array([0, -1 - k]) * ball_velocity

    # RENDER YOUR GAME HERE
    pygame.draw.circle(screen, "black", list(ball_pos), 50)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(120)

pygame.quit()
