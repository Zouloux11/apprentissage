import json
import imageio
import pygame
import random
import sys
import math
import matplotlib.pyplot as plt
import os
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import numpy as np

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
PIPE_MOVE_AMPLITUDE = 0
PIPE_MOVE_SPEED = 0
PIPE_MAX_OFFSET = 0
POWERUP_DURATION = 25
PROBA_POWER_UP= 150
POWERUP_SCORE_MULTIPLIER = 100
SURVIVAL_BONUS = 1000



class PowerUp:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(100, SCREEN_HEIGHT - 100)
        self.active = True 

    def get_rect(self):
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)

    def update(self):
        self.x -= PIPE_SPEED


class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.powerups = 0
        self.powerUP = False
        self.invincibility_timer = 0
        self.survived_powerup = False 

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.powerUP:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.powerUP = False
                self.survived_powerup = True 

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def use_powerup(self):
        if self.powerups > 0 and not self.powerUP:
            self.powerups -= 1
            self.powerUP = True
            self.invincibility_timer = POWERUP_DURATION
            self.survived_powerup = False 

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

def should_jump_complexe(bird, pipes, weights_jump, weights_powerup, wind=0, powerups=[]):
    # Pipe le plus proche
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

    # Power-up le plus proche
    dx_powerup = dy_powerup = 1000
    for p in powerups:
        if not p.active:
            continue
        dx = p.x - bird.x
        if dx >= 0 and dx < dx_powerup:
            dx_powerup = dx
            dy_powerup = p.y - bird.y

    jump_inputs = [
        bird.y - next_pipe.height,
        bird.y - (next_pipe.height + PIPE_GAP),
        next_pipe.x - bird.x,
        bird.velocity,
        bird.y,
        dx_powerup,
        dy_powerup
    ]

    power_up_inputs = [
        bird.y - next_pipe.height,
        bird.y - (next_pipe.height + PIPE_GAP),
        next_pipe.x - bird.x,
        bird.velocity,
        bird.y,
        dx_powerup,
        dy_powerup
    ]

    jump_decision_value = sum(w * i for w, i in zip(weights_jump, jump_inputs))
    powerup_decision_value = sum(w * i for w, i in zip(weights_powerup, power_up_inputs))

    jump = jump_decision_value < 0
    use_powerup = powerup_decision_value < 0

    return jump, use_powerup


def run_game_powerUP(weightsJump=None, weightsPowerUp=None, render=False, manual=False):
    global PIPE_GAP, PIPE_SPEED, PIPE_GAP_INIT, PIPE_SPEED_INIT, frame
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + i * 300) for i in range(NUM_PIPES)]
    powerups = []
    score = 0
    pipes_passed = 0 
    frame = 0
    alive_distance = 0
    pipe_count = 0
    wind = 0
    distance_points = 0
    survival_bonuses = 0

    PIPE_SPEED = PIPE_SPEED_INIT
    PIPE_GAP = PIPE_GAP_INIT

    if render:
        video_frames = []

    while True:
        if render:
            screen.fill((135, 206, 250))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        wind = random.uniform(-WIND_STRENGTH, WIND_STRENGTH)

        if int(random.uniform(0, PROBA_POWER_UP)) == 1:
            powerups.append(PowerUp(SCREEN_WIDTH + 100))

        if bird.survived_powerup:
            score += SURVIVAL_BONUS
            survival_bonuses += 1
            bird.survived_powerup = False

        if manual:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bird.jump()
            if keys[pygame.K_p]:
                bird.use_powerup()
        else:
            jump, use = should_jump_complexe(bird, pipes, weightsJump, weightsPowerUp, powerups=powerups, wind=wind)
            if jump:
                bird.jump()
            if use:
                bird.use_powerup()

        bird.velocity += GRAVITY + wind
        bird.update()

        for pipe in pipes:
            pipe.update()
        for p in powerups:
            p.update()

        distance_points += 1

        for pipe in pipes:
            if pipe.x + PIPE_WIDTH < 0:
                pipes.remove(pipe)
                pipes.append(Pipe(300 * NUM_PIPES - PIPE_WIDTH)) 
                pipes_passed += 1

                if bird.powerUP:
                    score += 1000 * POWERUP_SCORE_MULTIPLIER

                pipe_count += 1
                if pipe_count % 5 == 0:
                    if PIPE_GAP > 60:
                        PIPE_GAP -= 10 
                    if PIPE_SPEED < 10: 
                        PIPE_SPEED += 0.5

        bird_rect = bird.get_rect()

        for p in powerups:
            if p.active and bird_rect.colliderect(p.get_rect()):
                p.active = False
                bird.powerups += 1

        collision = (
            bird.y > SCREEN_HEIGHT or bird.y < 0 or
            any(pipe.collides_with(bird_rect) for pipe in pipes)
        )

        if bird.powerUP:
            collision = False

        alive_distance += 1

        if render:
            total_score = score + distance_points

            color = (0, 0, 255) if bird.powerUP else (255, 255, 0)
            pygame.draw.circle(screen, color, (int(bird.x), int(bird.y)), 20)

            for pipe in pipes:
                pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pipe.x, 0, PIPE_WIDTH, pipe.height))
                pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pipe.x + pipe.x_offset_bottom, pipe.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT))

            for p in powerups:
                if p.active:
                    pygame.draw.circle(screen, (255, 0, 255), (int(p.x), int(p.y)), 10)

            score_text = font.render(f"Score: {total_score}", True, (0, 0, 0))
            screen.blit(score_text, (10, 10))

            info_text = font.render(f"Pipes: {pipes_passed} | PowerUps: {bird.powerups}", True, (0, 0, 0))
            screen.blit(info_text, (10, 50))

            if bird.powerUP:
                powerup_status = small_font.render(f"PowerUp Active: x{POWERUP_SCORE_MULTIPLIER} (Time: {bird.invincibility_timer})", True, (0, 0, 255))
                screen.blit(powerup_status, (10, 90))

            if survival_bonuses > 0:
                survival_info = small_font.render(f"Survival Bonuses: {survival_bonuses} x {SURVIVAL_BONUS}", True, (255, 0, 0))
                screen.blit(survival_info, (10, 130))

            pygame.display.flip()

            # Capture frame for video
            frame_surface = pygame.display.get_surface()
            frame_data = pygame.surfarray.array3d(frame_surface)
            frame_data = np.transpose(frame_data, (1, 0, 2))  # (width, height) to (height, width)
            video_frames.append(frame_data.copy())

            clock.tick(FPS)

        if collision:
            break

        frame += 1
        if frame > 30000:
            break

    total_score = score + distance_points

    if render and video_frames:
        output_filename = f"gameplay_{total_score}.mp4"
        imageio.mimsave(output_filename, video_frames, fps=FPS)

    return total_score


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    if len(sys.argv) < 2:
        print("Usage: python jeuPowerUP.py weights.json")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        loaded_weights = json.load(f)

    if not isinstance(loaded_weights, list) or len(loaded_weights) != 2:
        print("Erreur : le fichier JSON doit contenir une liste avec deux sous-listes de poids.")
        sys.exit(1)

    weights_jump, weights_powerup = loaded_weights

    score = run_game_powerUP(weightsJump=weights_jump, weightsPowerUp=weights_powerup, render=True, manual=False)

    print("Score final :", score)

