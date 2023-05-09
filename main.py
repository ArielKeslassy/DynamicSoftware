import pygame as pg
pg.init()
from dynamic_edit_codex import InputBox

# animation of ball.jpeg bouncing off the walls of the screen

# set up the window
screen = pg.display.set_mode((500, 500))
pg.display.set_caption('Bouncing Ball')

# set up the colors
BLACK = (0, 0, 0)

# input box
input_box = InputBox(100, 100, 140, 32)

# set up the ball
ball = pg.image.load('ball.jpeg')
ballrect = ball.get_rect()
ballrect.center = (250, 250)
speed = [2, 2]

# set up the clock
clock = pg.time.Clock()

# main loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(60)

    # process input (events)
    for event in pg.event.get():
        # check for closing the window
        if event.type == pg.QUIT:
            running = False
        input_box.handle_event(event)

    # update the input box
    input_box.update()

    # move the ball
    ballrect = ballrect.move(speed)

    # check if the ball is off the screen
    if ballrect.left < 0 or ballrect.right > 500:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > 500:
        speed[1] = -speed[1]

    # fill the background with black
    screen.fill(BLACK)
    input_box.draw(screen)

    # draw the ball on the screen
    screen.blit(ball, ballrect)

    # update the screen
    pg.display.flip()

# end pygame
pg.quit()
