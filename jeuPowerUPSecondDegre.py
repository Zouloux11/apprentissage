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
POWERUP_DURATION = 150
PROBA_POWER_UP= 500
POWERUP_SCORE_MULTIPLIER = 10
SURVIVAL_BONUS = 10000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

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
        self.invincible = False
        self.invincibility_timer = 0
        self.survived_powerup = False 

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False
                self.survived_powerup = True 

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def use_powerup(self):
        if self.powerups > 0 and not self.invincible:
            self.powerups -= 1
            self.invincible = True
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

    dx_powerup = dy_powerup = 1000
    for p in powerups:
        if not p.active:
            continue
        dx = p.x - bird.x
        if dx >= 0 and dx < dx_powerup:
            dx_powerup = dx
            dy_powerup = p.y - bird.y

    base_inputs = [
        bird.y - next_pipe.height,
        bird.y - (next_pipe.height + PIPE_GAP),
        next_pipe.x - bird.x,
        bird.velocity,
        bird.y,
        math.sin(next_pipe.osc_y) * PIPE_MOVE_AMPLITUDE,
        math.cos(next_pipe.osc_x) * 5,
        wind,
        dx_powerup,
        dy_powerup
    ]

    extended_inputs = base_inputs + [x ** 2 for x in base_inputs]

    jump_decision_value = sum(w * i for w, i in zip(weights_jump, extended_inputs))
    powerup_decision_value = sum(w * i for w, i in zip(weights_powerup, extended_inputs))

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

    while True:
        if render:
            screen.fill((135, 206, 250))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        wind = random.uniform(-WIND_STRENGTH, WIND_STRENGTH)

        # Spawner des powerups aléatoirement
        shouldWeSpawnAPowerUp = int(random.uniform(0, PROBA_POWER_UP))
        if (shouldWeSpawnAPowerUp == 1):
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

        if bird.invincible:
            distance_points += POWERUP_SCORE_MULTIPLIER
        else:
            distance_points += 1

        for pipe in pipes:
            if pipe.x + PIPE_WIDTH < 0:
                pipes.remove(pipe)
                pipes.append(Pipe(300 * NUM_PIPES - PIPE_WIDTH)) 
                pipes_passed += 1
                
                if bird.invincible:
                    score += 1000 * POWERUP_SCORE_MULTIPLIER
                else:
                    score += 1000
                
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

        if bird.invincible:
            collision = False

        alive_distance += 1

        if render:
            total_score = score + distance_points
            
            color = (0, 0, 255) if bird.invincible else (255, 255, 0)
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
            
            if bird.invincible:
                powerup_status = small_font.render(f"PowerUp Active: x{POWERUP_SCORE_MULTIPLIER} (Time: {bird.invincibility_timer})", True, (0, 0, 255))
                screen.blit(powerup_status, (10, 90))
            
            if survival_bonuses > 0:
                survival_info = small_font.render(f"Survival Bonuses: {survival_bonuses} x {SURVIVAL_BONUS}", True, (255, 0, 0))
                screen.blit(survival_info, (10, 130))
            
            pygame.display.flip()
            clock.tick(FPS)

        if collision:
            break

        frame += 1
        if frame > 30000:
            break

    # Calculate final score
    total_score = score + distance_points
    return total_score