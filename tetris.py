import pygame
import random

# Цвета
COLORS = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122)
]

# Фигуры
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],
    [[4, 5, 9, 10], [2, 6, 5, 9]],
    [[6, 7, 9, 10], [1, 5, 6, 10]],
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
    [[1, 2, 5, 6]]
]

# Параметры
field = []
current_shape = None
current_x = 0
current_y = 0
current_rot = 0
current_color = 0
field_h = 20
field_w = 10
level = 2
score = 0
state = "start"
px = 100
py = 60
pzoom = 20
pressing_down = False

def create_field(w, h):
    global field
    field = []
    for _ in range(h):
        field.append([0] * w)

def new_shape():
    global current_shape, current_x, current_y, current_rot, current_color
    current_x = 3
    current_y = 0
    current_shape = random.randint(0, len(SHAPES) - 1)
    current_rot = 0
    current_color = random.randint(1, len(COLORS) - 1)

def rotate_shape():
    global current_rot
    current_rot = (current_rot + 1) % len(SHAPES[current_shape])

def shape_image():
    return SHAPES[current_shape][current_rot]

def intersects():
    img = shape_image()
    for i in range(4):
        for j in range(4):
            if i * 4 + j in img:
                if i + current_y >= field_h or j + current_x >= field_w or j + current_x < 0:
                    return True
                if field[i + current_y][j + current_x] > 0:
                    return True
    return False

def freeze():
    global field
    img = shape_image()
    for i in range(4):
        for j in range(4):
            if i * 4 + j in img:
                field[i + current_y][j + current_x] = current_color
    break_lines()
    new_shape()
    if intersects():
        global state
        state = "gameover"

def break_lines():
    global field, score
    lines = 0
    for i in range(1, field_h):
        zeros = 0
        for j in range(field_w):
            if field[i][j] == 0:
                zeros += 1
        if zeros == 0:
            lines += 1
            for k in range(i, 1, -1):
                for l in range(field_w):
                    field[k][l] = field[k-1][l]
    score += lines * lines

def go_down():
    global current_y
    current_y += 1
    if intersects():
        current_y -= 1
        freeze()

def move_sideways(dx):
    global current_x
    current_x += dx
    if intersects():
        current_x -= dx

def drop_down():
    global current_y
    while not intersects():
        current_y += 1
    current_y -= 1
    freeze()

def restart():
    global score, state, level
    score = 0
    state = "start"
    create_field(field_w, field_h)
    new_shape()

def draw_board(screen):
    for i in range(field_h):
        for j in range(field_w):
            pygame.draw.rect(screen, (128, 128, 128), [px + pzoom * j, py + pzoom * i, pzoom, pzoom], 1)
            if field[i][j] > 0:
                pygame.draw.rect(screen, COLORS[field[i][j]], [px + pzoom * j + 1, py + pzoom * i + 1, pzoom - 2, pzoom - 1])

def draw_shape(screen):
    img = shape_image()
    for i in range(4):
        for j in range(4):
            if i * 4 + j in img:
                pygame.draw.rect(screen, COLORS[current_color], [px + pzoom * (j + current_x) + 1, py + pzoom * (i + current_y) + 1, pzoom - 2, pzoom - 2])

def draw_texts(screen):
    font = pygame.font.SysFont('Calibri', 25, True, False)
    font_big = pygame.font.SysFont('Calibri', 65, True, False)
    text_score = font.render("Score: " + str(score), True, (0, 0, 0))
    text_over = font_big.render("Game Over", True, (255, 125, 0))
    text_restart = font_big.render("Press ESC", True, (255, 215, 0))

    screen.blit(text_score, [0, 0])
    if state == "gameover":
        screen.blit(text_over, [20, 200])
        screen.blit(text_restart, [25, 265])

# Инициализация
pygame.init()
screen = pygame.display.set_mode((400, 500))
pygame.display.set_caption("Bad Tetris")
clock = pygame.time.Clock()

restart()
counter = 0
fps = 25
running = True

while running:
    if current_shape is None:
        new_shape()
    counter += 1
    if counter > 100000:
        counter = 0
    if (counter % (fps // level // 2) == 0) or pressing_down:
        if state == "start":
            go_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                rotate_shape()
                if intersects():
                    rotate_shape()
                    rotate_shape()
                    rotate_shape()
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                move_sideways(-1)
            if event.key == pygame.K_RIGHT:
                move_sideways(1)
            if event.key == pygame.K_SPACE:
                drop_down()
            if event.key == pygame.K_ESCAPE:
                restart()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

    screen.fill((255, 255, 255))
    draw_board(screen)
    if current_shape is not None:
        draw_shape(screen)
    draw_texts(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()