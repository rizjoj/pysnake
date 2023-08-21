import sys
import time
import pygame  # type: ignore
import random
import itertools as it
import circularlist
from playsound import playsound
from moviepy.editor import *

SNAKE_BLOCK = 320  # Game size. Try 1, 5, 10, 20, 40, 80, 160, 320
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 640  # See IF suite below for valid values

if WINDOW_WIDTH / SNAKE_BLOCK % 2 != 0 or WINDOW_HEIGHT / SNAKE_BLOCK % 2 != 0:
    print("WINDOW_WIDTH and WINDOW_HEIGHT must be divisible by SNAKE_BLOCK")
    print("WINDOW_WIDTH and WINDOW_HEIGHT divided by SNAKE_BLOCK must be even")
    quit()

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

bgcolor = black

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
window.fill(bgcolor)

game_over = False

x1, y1 = WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2  # Snake head coordinates
x1_change, y1_change = SNAKE_BLOCK, 0  # Set snake initial direction

clock = pygame.time.Clock()


# Get frame rate from CLI arg. Default to 10 if blank/invalid. Min 1, Max 30.
snake_speed = 10
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    snake_speed = max(min(int(sys.argv[1]), 30), 1)

font_style = pygame.font.SysFont("", 50)


def message(msg, color):
    fontMsg = font_style.render(msg, True, color)
    window.blit(
        fontMsg,
        [
            WINDOW_WIDTH / 2 - fontMsg.get_width() / 2,
            WINDOW_HEIGHT / 2 - fontMsg.get_height() / 2,
        ],
    )


def get_image(filename):
    image = pygame.image.load(filename).convert_alpha()
    return pygame.transform.smoothscale(image, (SNAKE_BLOCK, SNAKE_BLOCK))


body = get_image("images/body.png")
fruit = get_image("images/fruit.png")
head_up = get_image("images/head.png")
head_left = pygame.transform.rotate(head_up, 90)
head_right = pygame.transform.flip(head_left, True, False)
head_down = pygame.transform.flip(head_up, False, True)

# Set Location of snake body parts for collision detection
snake_points = set()  # type: set[tuple]
snake = circularlist.CircularList((x1 + SNAKE_BLOCK, y1))
snake.insert((x1, y1))  # Add 1 body to snake's head
snake_points.add((x1, y1))


def is_board_full():
    return score == len(BOARD_POINTS) - 1


def is_outside_board(x1, y1) -> bool:
    return x1 not in range(WINDOW_WIDTH) or y1 not in range(WINDOW_HEIGHT)


# Used to find next food position. See put_food()
BOARD_POINTS = set(
    it.product(
        range(0, WINDOW_WIDTH, SNAKE_BLOCK), range(0, WINDOW_HEIGHT, SNAKE_BLOCK)
    )
)


def put_food():
    unoccupied_points = list(BOARD_POINTS.difference(snake_points))
    food_position = random.choice(unoccupied_points) if unoccupied_points else None
    window.blit(fruit, food_position or (-SNAKE_BLOCK, -SNAKE_BLOCK))
    return food_position


def increment_score() -> None:
    global score
    score += 1
    pygame.display.set_caption("Snake Game for IAN! Score: " + str(score))


# Initialize
head = head_right
score = -1
increment_score()  # Setup title bar with score: 0
food_position = put_food()
key_queue = []

while not game_over:
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                game_over = True
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        game_over = True
                    case pygame.K_LEFT | pygame.K_RIGHT | pygame.K_UP | pygame.K_DOWN:
                        key_queue.append(event.key)  # Queue all key strokes this frame
                    case pygame.K_SPACE:
                        print(food_position)  # For debugging

    current_key = key_queue.pop(0) if key_queue else None  # Dequeue 1 key per frame

    match current_key:
        case pygame.K_LEFT:
            if x1_change != SNAKE_BLOCK:  # Prevent 180° turn
                x1_change, y1_change, head = -SNAKE_BLOCK, 0, head_left
        case pygame.K_RIGHT:
            if x1_change != -SNAKE_BLOCK:  # Prevent 180° turn
                x1_change, y1_change, head = SNAKE_BLOCK, 0, head_right
        case pygame.K_UP:
            if y1_change != SNAKE_BLOCK:  # Prevent 180° turn
                x1_change, y1_change, head = 0, -SNAKE_BLOCK, head_up
        case pygame.K_DOWN:
            if y1_change != -SNAKE_BLOCK:  # Prevent 180° turn
                x1_change, y1_change, head = 0, SNAKE_BLOCK, head_down

    # Clear snake's tail
    snake_points.discard(snake.get_tail())
    if food_position != snake.get_tail():  # Edge case when snake length increases
        window.blit(body, snake.get_tail(), None, pygame.BLEND_SUB)

    # Cover up snake's head with a body piece
    window.blit(body, (x1, y1))

    # Snake's next move
    x1 += x1_change
    y1 += y1_change

    # Collision check
    is_in_snake = (x1, y1) in snake_points
    if is_in_snake or is_outside_board(x1, y1):
        game_over = True
        break

    # Add snake's new location for future collision detection
    snake_points.add((x1, y1))

    # Did snake eat/collide with food?
    if food_position == (x1, y1):
        playsound("audio/eat.mp3", False)
        increment_score()
        snake.insert((x1, y1))  # Increment snake's length
        food_position = put_food()
    else:
        snake.shift((x1, y1))  # Move snake's body (right shift pointer in CircularList)

    # Paint/Update frame with snake head at new position
    window.blit(head, (x1, y1), None, pygame.BLEND_ADD)
    pygame.display.update()
    clock.tick(snake_speed)

## Game Over ##
if is_outside_board(x1, y1):
    # Show Dying animation inside frame
    x1 -= x1_change
    y1 -= y1_change
# Dying animation: Rotate snake head 16 times
playsound("audio/lose.mp3", False)
for _ in range(24):
    head = pygame.transform.rotate(head, -90)
    window.blit(head, (x1, y1))
    pygame.display.update()
    clock.tick(15)

# Show "Game Over" screen
window.fill(bgcolor)

is_winner = is_board_full()
salutation = "YOU WIN" if is_winner else "Game Over"
color = white if is_winner else red

message(salutation + "! Your score: " + str(score), color)
pygame.display.update()
time.sleep(1)

if is_winner:
    video_clip = VideoFileClip("video/jablinski-sax.mp4")
    video_clip.subclip
    video_clip.preview()

pygame.quit()
quit()
