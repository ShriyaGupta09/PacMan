import copy
import pygame
import math
from board import boards

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('loop.mp3')  # Replace with your music file
pygame.mixer.music.play(-1)

win_sound = pygame.mixer.Sound('gamewin.mp3')
lose_sound = pygame.mixer.Sound('gameover.mp3')
ghost_eaten_sound = pygame.mixer.Sound('ghost_eaten.mp3')
ghost_eats_pacman_sound = pygame.mixer.Sound('ghost_eats_pacman.mp3')
game_state = "playing"

WIDTH = 700
HEIGHT = 750

screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font("freesansbold.ttf", 20)
level = copy.deepcopy(boards)
PI = math.pi
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f"assets/player_images/{i}.png"), (30, 30)))
blinky_img = pygame.transform.scale(pygame.image.load(f"assets/ghost_images/red.png"), (30, 30))
pinky_img = pygame.transform.scale(pygame.image.load(f"assets/ghost_images/pink.png"), (30, 30))
inky_img = pygame.transform.scale(pygame.image.load(f"assets/ghost_images/blue.png"), (30, 30))
clyde_img = pygame.transform.scale(pygame.image.load(f"assets/ghost_images/orange.png"), (30, 30))
spooked_img = pygame.transform.scale(pygame.image.load(f"assets/ghost_images/powerup.png"), (30, 30))
dead_img = pygame.transform.scale(pygame.image.load(f"assets/ghost_images/dead.png"), (30, 30))

player_x = 330
player_y = 498
blinky_x = 42
blinky_y = 42
blinky_direction = 0
inky_x = 329
inky_y = 328
inky_direction = 2
pinky_x = 329
pinky_y = 298
pinky_direction = 2
clyde_x = 329
clyde_y = 298
clyde_direction = 2

direction = 0
counter = 0
flicker = False
# R, L, U, D
turns_allowed = [False, False, False, False]
direction_command = 0
player_speed = 2
score = 0
power = False
power_count = 0
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]

blinky_dead = False
inky_dead = False
clyde_dead = False
pinky_dead = False
blinky_box = False
inky_box = False
clyde_box = False
pinky_box = False

moving = False
ghost_speed = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = False
game_won = False

win_sound_played = False
lose_sound_played = False
previous_game_won = False
previous_game_over = False


class Ghost:
    def __init__(self, x_cord, y_cord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_cord
        self.y_pos = y_cord
        self.center_x = self.x_pos + 15
        self.center_y = self.y_pos + 15
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()

    def draw(self):
        if (not power and not self.dead) or (eaten_ghost[self.id] and power and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif power and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 14, self.center_y - 8), (32, 32))
        return ghost_rect

    def check_collisions(self):
        # R, L, U, D
        num1 = (HEIGHT - 50) // 32
        num2 = WIDTH // 30
        num3 = 7

        self.turns = [False, False, False, False]

        # Calculate indices with bounds checking
        x_idx_left = max(0, (self.center_x - num3) // num2)
        x_idx_right = min(len(level[0]) - 1, (self.center_x + num3) // num2)
        y_idx_up = max(0, (self.center_y - num3) // num1)
        y_idx_down = min(len(level) - 1, (self.center_y + num3) // num1)

        # Debugging information
        print(f"x_idx_left: {x_idx_left}, x_idx_right: {x_idx_right}, y_idx_up: {y_idx_up}, y_idx_down: {y_idx_down}")

        # Check if indices are within valid bounds
        if 0 <= y_idx_up < len(level) and 0 <= x_idx_right < len(level[0]):
            if level[y_idx_up][x_idx_right] == 9:
                self.turns[2] = True

        if 0 <= self.center_y // num1 < len(level) and 0 <= x_idx_left < len(level[0]):
            if level[self.center_y // num1][x_idx_left] < 3 or \
                    (level[self.center_y // num1][x_idx_left] == 9 and (self.in_box or self.dead)):
                self.turns[1] = True  # Left turn available

        if 0 <= self.center_y // num1 < len(level) and 0 <= x_idx_right < len(level[0]):
            if level[self.center_y // num1][x_idx_right] < 3 or \
                    (level[self.center_y // num1][x_idx_right] == 9 and (self.in_box or self.dead)):
                self.turns[0] = True  # Right turn available

        if 0 <= y_idx_down < len(level) and 0 <= self.center_x // num2 < len(level[0]):
            if level[y_idx_down][self.center_x // num2] < 3 or \
                    (level[y_idx_down][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[3] = True  # Down turn available

        if 0 <= y_idx_up < len(level) and 0 <= self.center_x // num2 < len(level[0]):
            if level[y_idx_up][self.center_x // num2] < 3 or \
                    (level[y_idx_up][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[2] = True  # Up turn available

        # Fine-tune turns based on direction
        if self.direction in [2, 3]:  # Up or Down
            if 7 <= self.center_x % num2 <= 14:
                if 0 <= y_idx_down < len(level) and 0 <= self.center_x // num2 < len(level[0]):
                    if level[y_idx_down][self.center_x // num2] < 3 or \
                            (level[y_idx_down][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True  # Down turn available

                if 0 <= y_idx_up < len(level) and 0 <= self.center_x // num2 < len(level[0]):
                    if level[y_idx_up][self.center_x // num2] < 3 or \
                            (level[y_idx_up][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True  # Up turn available

        if self.direction in [0, 1]:  # Right or Left
            if 7 <= self.center_x % num2 <= 14:
                if 0 <= self.center_y // num1 < len(level) and 0 <= x_idx_left < len(level[0]):
                    if level[self.center_y // num1][x_idx_left] < 3 or \
                            (level[self.center_y // num1][x_idx_left] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True  # Left turn available

                if 0 <= self.center_y // num1 < len(level) and 0 <= x_idx_right < len(level[0]):
                    if level[self.center_y // num1][x_idx_right] < 3 or \
                            (level[self.center_y // num1][x_idx_right] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True  # Right turn available

        # Edge case handling
        if 250 < self.x_pos < 320 and 170 < self.y_pos < 310:
            self.in_box = True
        else:
            self.in_box = False

        return self.turns, self.in_box

    def move_clyde(self):
        # r, l, u, d
        # clyde is going to turn whenever advantageous for pursuit
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed

        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed

        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed

        if self.x_pos < -20:
            self.x_pos = 700
        elif self.x_pos > 700:
            self.x_pos = 20

        if self.y_pos < 20:
            self.y_pos = HEIGHT - 20
        elif self.y_pos > HEIGHT - 20:
            self.y_pos = 20
        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        # r, l, u, d
        # blinky is going to turn whenever colliding with walls, otherwise continue straight
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed

        elif self.direction == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed

        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed

        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:
                self.y_pos += self.speed

        if self.x_pos < -20:
            self.x_pos = 700
        elif self.x_pos > 700:
            self.x_pos = 20

        if self.y_pos < 20:
            self.y_pos = HEIGHT - 20
        elif self.y_pos > HEIGHT - 20:
            self.y_pos = 20
        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
        # r, l, u, d
        # inky turns up or down at any point to pursue, but left and right only on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed

        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed

        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed

        if self.x_pos < -20:
            self.x_pos = 700
        elif self.x_pos > 700:
            self.x_pos = 20

        if self.y_pos < 20:
            self.y_pos = HEIGHT - 20
        elif self.y_pos > HEIGHT - 20:
            self.y_pos = 20
        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # r, l, u, d
        # pinky is going to turn left or right whenever advantageous, but only up or down on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed

        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed

        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed

        if self.x_pos < -20:
            self.x_pos = 700
        elif self.x_pos > 700:
            self.x_pos = 20

        if self.y_pos < 20:
            self.y_pos = HEIGHT - 20
        elif self.y_pos > HEIGHT - 20:
            self.y_pos = 20
        return self.x_pos, self.y_pos, self.direction


def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 720))
    if power:
        pygame.draw.circle(screen, 'purple', (140, 729), 10)
    for j in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (450 + j * 40, 705))

    custom_font = pygame.font.Font('ARCADECLASSIC.TTF', 37)
    custom_font2 = pygame.font.Font('ARCADECLASSIC.TTF', 32)
    if game_over:
        pygame.draw.rect(screen, 'red', [160, 270, 375, 150], 0)
        pygame.draw.rect(screen, 'orange', [170, 280, 355, 130], 0)
        gameover_text = custom_font.render('Game Over !!', True, 'black')
        gameover_text2 = custom_font2.render('Space Bar  to  Restart', True, 'black')
        screen.blit(gameover_text, (260, 305))
        screen.blit(gameover_text2, (190, 355))

    if game_won:
        pygame.draw.rect(screen, 'dark green', [160, 270, 375, 150], 0)
        pygame.draw.rect(screen, 'yellow', [170, 280, 355, 130], 0)
        gameover_text = custom_font.render('Victory !!', True, 'black')
        gameover_text2 = custom_font2.render('Space Bar  to  Restart', True, 'black')
        screen.blit(gameover_text, (270, 305))
        screen.blit(gameover_text2, (190, 355))


def check_collisions(scor, power, power_count, eaten_ghost):
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    if 0 < player_x < 670:
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
            eat_sound = pygame.mixer.Sound('pop.mp3')
            eat_sound.play()

        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            power_up_sound = pygame.mixer.Sound('gamebonus.mp3')
            if(power == True):
                power_up_sound.play()
            eaten_ghost = [False, False, False, False]
    return scor, power, power_count, eaten_ghost


def draw_board():
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 3.5)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 8)
            if level[i][j] == 3:
                pygame.draw.line(screen, 'orange', (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 2)
            if level[i][j] == 4:
                pygame.draw.line(screen, 'orange', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 2)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 2)

#             for arcs optional
#             if level[i][j] == 5:
#                 pygame.draw.arc(screen, 'orange', [(j*num2 - (num2*0.5)), (i*num1 + (num1*0.5)), num1, num2],
#                                 0, PI/2, 3)

def draw_player():
    # 0-R , 1-L , 2-U , 3-D
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    if direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    if direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    if direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], -90), (player_x, player_y))


def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH // 30)
    num3 = 6
    # check collisions based on center x and center y of player +/- fudge number
    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 7 <= centerx % num2 <= 30:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 7 <= centery % num1 <= 20:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 7 <= centerx % num2 <= 20:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 7 <= centery % num1 <= 20:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns


def move_player(play_x, play_y):
    # R, L, U, D
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed

    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed

        if play_x < 0:
            play_x = WIDTH
        elif play_x > WIDTH:
            play_x = 0

    return play_x, play_y


def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    if player_x < 225:
        runaway_x = 700
    else:
        runaway_x = 0
    if player_y < 225:
        runaway_y = 700
    else:
        runaway_y = 0
    return_target = (300, 360)
    if power:
        if not blinky.dead and not eaten_ghost[0]:
            blink_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghost[0]:
            if 170 < blink_x < 280 and 160 < blink_y < 250:
                blink_target = (200, 50)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target

        if not inky.dead and not eaten_ghost[1]:
            ink_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghost[1]:
            if 170 < ink_x < 280 and 160 < ink_y < 250:
                ink_target = (200, 50)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target

        if not pinky.dead:
            pink_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghost[2]:
            if 170 < pink_x < 280 and 160 < pink_y < 250:
                pink_target = (200, 50)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target

        if not clyde.dead and not eaten_ghost[3]:
            clyd_target = (225, 225)
        elif not clyde.dead and eaten_ghost[3]:
            if 170 < clyd_x < 280 and 160 < clyd_y < 250:
                clyd_target = (200, 50)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    else:
        if not blinky.dead:
            if 170 < blink_x < 280 and 160 < blink_y < 250:
                blink_target = (200, 50)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target
        if not inky.dead:
            if 170 < ink_x < 280 and 160 < ink_y < 250:
                ink_target = (200, 50)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target
        if not pinky.dead:
            if 170 < pink_x < 280 and 160 < pink_y < 250:
                pink_target = (200, 50)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target
        if not clyde.dead:
            if 170 < clyd_x < 280 and 160 < clyd_y < 250:
                clyd_target = (200, 50)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    return [blink_target, ink_target, pink_target, clyd_target]


run = True
while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 10:
            flicker = False
    else:
        counter = 0
        flicker = True
    if power and power_count < 400:
        power_count += 1
    elif power and power_count >= 400:
        power_count = 0
        power = False
        eaten_ghost = [False, False, False, False]
    if startup_counter < 100 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill("black")
    draw_board()

    center_x = player_x + 16
    center_y = player_y + 16

    if power:
        ghost_speed = [1, 1, 1, 1]
    else:
        ghost_speed = [2, 2, 2, 2]
    if eaten_ghost[0]:
        ghost_speed[0] = 2
    if eaten_ghost[1]:
        ghost_speed[1] = 2
    if eaten_ghost[2]:
        ghost_speed[2] = 2
    if eaten_ghost[3]:
        ghost_speed[3] = 2
    if blinky_dead:
        ghost_speed[0] = 4
    if inky_dead:
        ghost_speed[1] = 4
    if pinky_dead:
        ghost_speed[2] = 4
    if clyde_dead:
        ghost_speed[3] = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False



    if game_won and not previous_game_won:
        win_sound.play()
        win_sound_played = True

    if game_over and not previous_game_over:
        lose_sound.play()
        lose_sound_played = True

    # Update previous state after checking
    previous_game_won = game_won
    previous_game_over = game_over

    player_circle = pygame.draw.circle(screen, "black", (center_x, center_y), 16, 2)
    draw_player()

    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speed[0], blinky_img, blinky_direction, blinky_dead,
                   blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speed[1], inky_img, inky_direction, inky_dead,
                 inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speed[2], pinky_img, pinky_direction, pinky_dead,
                  pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speed[3], clyde_img, clyde_direction, clyde_dead,
                  clyde_box, 3)

    draw_misc()
    targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)

    turns_allowed = check_position(center_x, center_y)

    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not blinky_dead and not blinky.in_box:
            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
        else:
            blinky_x, blinky_y, blinky_direction = blinky.move_clyde()
        if not pinky_dead and not pinky.in_box:
            pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
        else:
            pinky_x, pinky_y, pinky_direction = pinky.move_clyde()
        if not inky_dead and not inky.in_box:
            inky_x, inky_y, inky_direction = inky.move_inky()
        else:
            inky_x, inky_y, inky_direction = inky.move_clyde()
        clyde_x, clyde_y, clyde_direction = clyde.move_clyde()

    score, power, power_count, eaten_ghost = check_collisions(score, power, power_count, eaten_ghost)

    # add to if not powerup to check if eaten ghosts

    if not power:
        if (player_circle.colliderect(blinky.rect) and not blinky.dead) or \
                (player_circle.colliderect(inky.rect) and not inky.dead) or \
                (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
                (player_circle.colliderect(clyde.rect) and not clyde.dead):
            if lives > 0:
                lives -= 1
                startup_counter = 0
                power = False
                power_count = 0
                player_x = 330
                player_y = 498
                direction = 0
                direction_command = 0
                blinky_x = 42
                blinky_y = 42
                blinky_direction = 0
                inky_x = 329
                inky_y = 298
                inky_direction = 2
                pinky_x = 329
                pinky_y = 242
                pinky_direction = 2
                clyde_x = 329
                clyde_y = 328
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                pinky_dead = False
                inky_dead = False
                clyde_dead = False
                ghost_eaten_sound.play()
            else:
                game_over = True
                moving = False
                startup_counter = 0

    if power and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky.dead:
        if lives > 0:
            power = False
            power_count = 0
            lives -= 1
            startup_counter = 0
            player_x = 330
            player_y = 498
            direction = 0
            direction_command = 0
            blinky_x = 42
            blinky_y = 42
            blinky_direction = 0
            inky_x = 329
            inky_y = 298
            inky_direction = 2
            pinky_x = 329
            pinky_y = 242
            pinky_direction = 2
            clyde_x = 329
            clyde_y = 328
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            pinky_dead = False
            inky_dead = False
            clyde_dead = False
            ghost_eaten_sound.play()
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if power and player_circle.colliderect(inky.rect) and eaten_ghost[1] and not inky.dead:
        if lives > 0:
            power = False
            power_count = 0
            lives -= 1
            startup_counter = 0
            player_x = 330
            player_y = 498
            direction = 0
            direction_command = 0
            blinky_x = 42
            blinky_y = 42
            blinky_direction = 0
            inky_x = 329
            inky_y = 298
            inky_direction = 2
            pinky_x = 329
            pinky_y = 242
            pinky_direction = 2
            clyde_x = 329
            clyde_y = 328
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            pinky_dead = False
            inky_dead = False
            clyde_dead = False
            ghost_eaten_sound.play()
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if power and player_circle.colliderect(pinky.rect) and eaten_ghost[2] and not pinky.dead:
        if lives > 0:
            power = False
            power_count = 0
            lives -= 1
            startup_counter = 0
            player_x = 330
            player_y = 498
            direction = 0
            direction_command = 0
            blinky_x = 42
            blinky_y = 42
            blinky_direction = 0
            inky_x = 329
            inky_y = 298
            inky_direction = 2
            pinky_x = 329
            pinky_y = 242
            pinky_direction = 2
            clyde_x = 329
            clyde_y = 328
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            pinky_dead = False
            inky_dead = False
            clyde_dead = False
            ghost_eaten_sound.play()
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if power and player_circle.colliderect(clyde.rect) and eaten_ghost[3] and not clyde.dead:
        if lives > 0:
            power = False
            power_count = 0
            lives -= 1
            startup_counter = 0
            player_x = 330
            player_y = 498
            direction = 0
            direction_command = 0
            blinky_x = 42
            blinky_y = 42
            blinky_direction = 0
            inky_x = 329
            inky_y = 298
            inky_direction = 2
            pinky_x = 329
            pinky_y = 242
            pinky_direction = 2
            clyde_x = 329
            clyde_y = 328
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            pinky_dead = False
            inky_dead = False
            clyde_dead = False
            ghost_eaten_sound.play()
        else:
            game_over = True
            moving = False
            startup_counter = 0

    if power and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]:
        blinky_dead = True
        eaten_ghost[0] = True
        score += (2 ** eaten_ghost.count(True)) * 100
        ghost_eaten_sound.play()
    if power and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghost[1]:
        inky_dead = True
        eaten_ghost[1] = True
        score += (2 ** eaten_ghost.count(True)) * 100
        ghost_eaten_sound.play()
    if power and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghost[2]:
        pinky_dead = True
        eaten_ghost[2] = True
        score += (2 ** eaten_ghost.count(True)) * 100
        ghost_eaten_sound.play()
    if power and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghost[3]:
        clyde_dead = True
        eaten_ghost[3] = True
        score += (2 ** eaten_ghost.count(True)) * 100
        ghost_eaten_sound.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):
                power = False
                power_count = 0
                lives -= 1
                startup_counter = 0
                player_x = 330
                player_y = 498
                direction = 0
                direction_command = 0
                blinky_x = 42
                blinky_y = 42
                blinky_direction = 0
                inky_x = 329
                inky_y = 298
                inky_direction = 2
                pinky_x = 329
                pinky_y = 242
                pinky_direction = 2
                clyde_x = 329
                clyde_y = 328
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                pinky_dead = False
                inky_dead = False
                clyde_dead = False
                score = 0
                lives = 3
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False
                win_sound_played = False
                lose_sound_played = False

                game_state = "start"  # Add this line to reset to the starting screen

            if game_state == "playing":  # Add this line to ensure the game only plays when in "playing" state
                if game_won:
                    if not win_sound_played:
                        win_sound.play()
                        win_sound_played = True
                    game_state = "start"  # Add this line to move to the starting screen after winning

                if game_over:
                    if not lose_sound_played:
                        lose_sound.play()
                        lose_sound_played = True
                    game_state = "start"  # Add this line to move to the starting screen after losing

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    if blinky.in_box and blinky_dead:
        blinky_dead = False
    if inky.in_box and inky_dead:
        inky_dead = False
    if pinky.in_box and pinky_dead:
        pinky_dead = False
    if clyde.in_box and clyde_dead:
        clyde_dead = False

    pygame.display.flip()
pygame.quit()
