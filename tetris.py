import pygame
import random
from enum import Enum

# Определим цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]

# Enum для состояний игры
class GameState(Enum):
    STARTED = 1
    PAUSED = 2
    GAMEOVER = 3


class Figure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class TetrisGame:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.field = [[0] * width for _ in range(height)]
        self.score = 0
        self.state = GameState.STARTED
        self.figure = None
        self.level = 1
        self.fall_counter = 0
        self.x_offset = 100
        self.y_offset = 60
        self.cell_size = 20

    def new_figure(self):
        self.figure = Figure(self.width // 2 - 2, 0)

    def intersects(self):
        if self.figure is None:
            return False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y >= self.height or j + self.figure.x >= self.width or j + self.figure.x < 0 or self.field[i + self.figure.y][j + self.figure.x] > 0:
                        return True
        return False

    def break_lines(self):
        lines = 0
        for i in range(self.height - 1, 0, -1):
            if all(self.field[i][j] != 0 for j in range(self.width)):
                lines += 1
                for i1 in range(i, 0, -1):
                    self.field[i1] = self.field[i1 - 1][:]
        self.score += lines ** 2

    def go_down(self):
        if self.figure is None:
            return
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        if self.figure is None:
            return
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = GameState.GAMEOVER

    def rotate(self):
        if self.figure is None:
            return
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

    def move_side(self, dx):
        if self.figure is None:
            return
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def update(self, pressing_down):
        if self.figure is None:
            self.new_figure()
        if self.state == GameState.STARTED:
            if self.fall_counter % (30 // self.level) == 0 or pressing_down:
                self.go_down()
            self.fall_counter += 1

    def draw_board(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, GRAY, [self.x_offset + self.cell_size * j, self.y_offset + self.cell_size * i, self.cell_size, self.cell_size], 1)
                if self.field[i][j] > 0:
                    pygame.draw.rect(screen, colors[self.field[i][j]], [self.x_offset + self.cell_size * j + 1, self.y_offset + self.cell_size * i + 1, self.cell_size - 2, self.cell_size - 2])

        if self.figure is not None:
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in self.figure.image():
                        pygame.draw.rect(screen, colors[self.figure.color], [self.x_offset + self.cell_size * (j + self.figure.x) + 1, self.y_offset + self.cell_size * (i + self.figure.y) + 1, self.cell_size - 2, self.cell_size - 2])


# Инициализация Pygame
pygame.init()

# Настройка экрана и прочее
size = (400, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
game = TetrisGame(10, 20)

pressing_down = False
done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                game.move_side(-1)
            if event.key == pygame.K_RIGHT:
                game.move_side(1)
            if event.key == pygame.K_SPACE:
                while not game.intersects():
                    game.figure.y += 1
                game.figure.y -= 1
                game.freeze()
            if event.key == pygame.K_ESCAPE:
                game = TetrisGame(10, 20)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

    screen.fill(WHITE)
    game.update(pressing_down)
    game.draw_board(screen)

    # Отображение очков и состояния
    font = pygame.font.SysFont('Calibri', 25, True, False)
    score_text = font.render(f"Score: {game.score}", True, BLACK)
    screen.blit(score_text, [0, 0])

    if game.state == GameState.GAMEOVER:
        font_large = pygame.font.SysFont('Calibri', 65, True, False)
        game_over_text = font_large.render("Game Over", True, (255, 125, 0))
        press_escape_text = font_large.render("Press ESC to Restart", True, (255, 215, 0))
        screen.blit(game_over_text, [20, 200])
        screen.blit(press_escape_text, [25, 265])

    pygame.display.flip()
    clock.tick(30)

pygame.quit()