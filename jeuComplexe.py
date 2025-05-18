import pygame
import random
import sys
import math
import matplotlib.pyplot as plt

# --- Constantes ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.3
JUMP_STRENGTH = -8
PIPE_WIDTH = 50
PIPE_GAP = 0
PIPE_SPEED = 0
PIPE_GAP_INIT = 200
PIPE_SPEED_INIT = 1
FPS = 60
NUM_PIPES = 3
WIND_STRENGTH = 0.2
GRACE_PERIOD = 0
PIPE_MOVE_AMPLITUDE = 30
PIPE_MOVE_SPEED = 0.03
PIPE_MAX_OFFSET = 80


class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def get_rect(self):
        return pygame.Rect(self.x - 20, self.y - 20, 40, 40)

class Pipe:
    def __init__(self, x):
        self.base_x = x
        self.x = x
        self.x_offset_bottom = random.randint(-PIPE_MAX_OFFSET, PIPE_MAX_OFFSET)
        self.base_height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.height = self.base_height
        self.osc_y = random.uniform(0, 2 * math.pi)
        self.osc_x = random.uniform(0, 2 * math.pi)

    def update(self):
        global frame
        self.osc_y += PIPE_MOVE_SPEED
        self.osc_x += PIPE_MOVE_SPEED
        self.height = self.base_height + int(math.sin(self.osc_y) * PIPE_MOVE_AMPLITUDE)
        self.x = self.base_x - PIPE_SPEED + int(math.cos(self.osc_x) * 5)
        self.base_x -= PIPE_SPEED

    def collides_with(self, bird_rect):
        pipe_top = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        pipe_bottom = pygame.Rect(self.x + self.x_offset_bottom, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT)
        return bird_rect.colliderect(pipe_top) or bird_rect.colliderect(pipe_bottom)


def should_jump_complexe(bird, pipes, weights, wind=0):
    min_dist = float('inf')
    next_pipe = None
    for pipe in pipes:
        pipe_end = max(pipe.x + PIPE_WIDTH + 20, pipe.x + pipe.x_offset_bottom + PIPE_WIDTH + 20)

        if pipe_end < bird.x:
            continue

        dx = pipe.x - bird.x
        if dx < min_dist:
            min_dist = dx
            next_pipe = pipe

    if not next_pipe:
        return False 

    pipe_top_height = next_pipe.height
    pipe_bottom_height = next_pipe.height + PIPE_GAP
    dx = next_pipe.x - bird.x 

    dy_top = bird.y - pipe_top_height
    dy_bottom = bird.y - pipe_bottom_height
    v = bird.velocity
    altitude = bird.y

    pipe_movement_y = math.sin(next_pipe.osc_y) * PIPE_MOVE_AMPLITUDE
    pipe_movement_x = math.cos(next_pipe.osc_x) * 5

    inputs_base = [dy_top, dy_bottom, dx, v, altitude, pipe_movement_y, pipe_movement_x, wind]
    inputs = []
    for val in inputs_base:
        inputs.extend([val, val ** 2])

    decision = sum(w * i for w, i in zip(weights, inputs))
    return decision < 0


def run_game_complexe(weights=None, render=False, manual=False):
    global PIPE_GAP, PIPE_SPEED, PIPE_GAP_INIT, PIPE_SPEED_INIT, frame
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + i * 300) for i in range(NUM_PIPES)]
    score = 0
    frame = 0
    alive_distance = 0
    pipe_count = 0
    wind = 0

    PIPE_SPEED = PIPE_SPEED_INIT
    PIPE_GAP = PIPE_GAP_INIT

    while True:
        if render:
            screen.fill((135, 206, 250))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        wind = random.uniform(-WIND_STRENGTH, WIND_STRENGTH)
        if manual:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bird.jump()
        else:
            if should_jump_complexe(bird, pipes, weights, wind=wind):
                bird.jump()

        bird.velocity += GRAVITY + wind
        bird.update()
        for pipe in pipes:
            pipe.update()

        for pipe in pipes:
            if pipe.x + PIPE_WIDTH < 0:
                pipes.remove(pipe)
                pipes.append(Pipe(300 * NUM_PIPES - PIPE_WIDTH)) 
                score += 1
                pipe_count += 1
                if pipe_count % 5 == 0:
                    if PIPE_GAP > 60:
                        PIPE_GAP -= 10 
                    if PIPE_SPEED < 10: 
                        PIPE_SPEED += 0.5

        bird_rect = bird.get_rect()
        collision = bird.y > SCREEN_HEIGHT or bird.y < 0 or any(pipe.collides_with(bird_rect) for pipe in pipes)

        alive_distance += 1

        if render:
            pygame.draw.circle(screen, (255, 255, 0), (int(bird.x), int(bird.y)), 20)
            for pipe in pipes:
                pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pipe.x, 0, PIPE_WIDTH, pipe.height))
                pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pipe.x + pipe.x_offset_bottom, pipe.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT))

            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            screen.blit(score_text, (10, 10))
            pygame.display.flip()
            clock.tick(FPS)

        if collision:
            break

        frame += 1
        if frame > 30000:
            break

    return score * 1000 + alive_distance

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    import json

    if len(sys.argv) < 2:
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        weights = json.load(f)
        print(weights[3])

    score = run_game_complexe(weights=weights, render=True, manual=False)

    print("Score final :", score)