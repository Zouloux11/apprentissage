import pygame
import random
import sys
import math
import matplotlib.pyplot as plt

# --- Constantes ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.5
 
JUMP_STRENGTH = -6
PIPE_WIDTH = 50
PIPE_GAP = 0
PIPE_SPEED = 0
PIPE_GAP_INIT = 200
PIPE_SPEED_INIT = 1
FPS = 60
NUM_PIPES = 3


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
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)

    def update(self):
        self.x -= PIPE_SPEED 

    def collides_with(self, bird_rect):
        pipe_top = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        pipe_bottom = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT)
        return bird_rect.colliderect(pipe_top) or bird_rect.colliderect(pipe_bottom)

def should_jump(bird, pipes, weights):
    min_dist = float('inf')
    next_pipe = None
    for pipe in pipes:
        dx = (pipe.x + PIPE_WIDTH + 20) - bird.x
        if dx < 0: continue 
        
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


    decision = (weights[0] * dy_top + 
                 weights[1] * dy_bottom + 
                 weights[2] * dx + 
                 weights[3] * v + 
                 weights[4] * altitude) 

    return decision < 0

def run_game(weights=None, render=False, manual=False):
    global PIPE_GAP, PIPE_SPEED, PIPE_GAP_INIT, PIPE_SPEED_INIT
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + i * 300) for i in range(NUM_PIPES)]
    score = 0
    frame = 0
    alive_distance = 0
    pipe_count = 0

    PIPE_SPEED = PIPE_SPEED_INIT
    PIPE_GAP = PIPE_GAP_INIT

    video_frames = []  # <--- collect frames for video if render=True

    while True:
        if render:
            screen.fill((135, 206, 250))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        if manual:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bird.jump()
        else:
            if should_jump(bird, pipes, weights):
                bird.jump()

        bird.update()
        for pipe in pipes:
            pipe.update()

        # NIVEAUX DE DIFFICULTES
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
        collision = (
            bird.y > SCREEN_HEIGHT or bird.y < 0 or
            any(pipe.collides_with(bird_rect) for pipe in pipes)
        )

        alive_distance += 1

        if render:
            pygame.draw.circle(screen, (255, 255, 0), (int(bird.x), int(bird.y)), 20)
            for pipe in pipes:
                pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pipe.x, 0, PIPE_WIDTH, pipe.height))
                pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pipe.x, pipe.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT))

            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            screen.blit(score_text, (10, 10))
            pygame.display.flip()

            # Capture current frame for video
            frame_data = pygame.surfarray.array3d(screen)
            frame_data = frame_data.swapaxes(0, 1)  # (width, height, 3) → (height, width, 3)
            video_frames.append(frame_data)

            clock.tick(FPS)

        if collision:
            break

        frame += 1
        if frame > 30000:
            break

    # Save video if needed
    if render and video_frames:
        import imageio
        imageio.mimsave('gameplay.mp4', video_frames, fps=FPS)

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

    score = run_game(weights=weights, render=True, manual=False)

    print("Score final :", score)

