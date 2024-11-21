from board import boards

WIDTH = 700
HEIGHT = 750

level = boards


def check_collisions(self):
    # Initialize turns: [Right, Left, Up, Down]
    self.turns = [False, False, False, False]

    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    num3 = 7

    if 0 < self.center_x // 30 < 29:
        if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
            self.turns[2] = True
        # Checking Left
        if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 or \
                (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)):
            self.turns[1] = True  # Left turn available

        # Checking Right
        if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 or \
                (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)):
            self.turns[0] = True  # Right turn available

        # Checking Down
        if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or \
                (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
            self.turns[3] = True  # Down turn available

        # Checking Up
        if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or \
                (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
            self.turns[2] = True  # Up turn available

        if self.direction in [2, 3]:  # If the direction is Up or Down
            if 7 <= self.center_x % num2 <= 14:
                # Checking Down again (for finer control)
                if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or \
                        (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                                self.in_box or self.dead)):
                    self.turns[3] = True  # Down turn available

                # Checking Up again (for finer control)
                if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or \
                        (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                                self.in_box or self.dead)):
                    self.turns[2] = True  # Up turn available

        if self.direction in [0, 1]:  # If the direction is Right or Left
            if 7 <= self.center_x % num2 <= 14:
                # Checking Left again (for finer control)
                if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 or \
                        (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                                self.in_box or self.dead)):
                    self.turns[1] = True  # Left turn available

                # Checking Right again (for finer control)
                if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 or \
                        (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                                self.in_box or self.dead)):
                    self.turns[0] = True  # Right turn available
    else:
        # If the object is on the edge, allow left and right turns by default
        self.turns[0] = True  # Right turn available
        self.turns[1] = True  # Left turn available

    # Check if the object is within a specific box
    if 250 < self.x_pos < 320 and 170 < self.y_pos < 310:
        self.in_box = True
    else:
        self.in_box = False

    return self.turns, self.in_box


def check_collisions(scor, power, power_count, eaten_ghost):
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    if 0 < player_x < 720:
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghost = [False, False, False, False]
    return scor, power, power_count, eaten_ghost
