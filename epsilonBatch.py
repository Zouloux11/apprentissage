import pygame
import random
import sys
import math
import matplotlib.pyplot as plt

from jeuClassique import run_game as run_game_simple
from jeuComplexe import run_game_complexe
from jeuPowerUP import run_game_powerUP
from jeuClassiqueBonus import run_game_complexe as run_game_complexe_bonus
from jeuComplexeBonusSecondDegre import run_game_complexe as run_game_complexe_bonus_second_degre
from jeuComplexeBonusQuadratique import run_game_complexe as run_game_complexe_bonus_quadratique


def train(run_game_function, weight_size, batch_size = 10, generations=1000, epsilon=0, epsilon_decay=1, name="No Name", dual_weights=False):
    def avg_score_single(weights):
        return sum(run_game_function(weights) for _ in range(batch_size)) / batch_size

    def avg_score_dual(weights_jump, weights_powerup):
        return sum(run_game_function(weights_jump, weights_powerup) for _ in range(batch_size)) / batch_size

    if dual_weights:
        weight_size_jump, weight_size_powerup = weight_size
        best_weights_jump = [random.uniform(-2, 2) for _ in range(weight_size_jump)]
        best_weights_powerup = [random.uniform(-2, 2) for _ in range(weight_size_powerup)]
        best_score = avg_score_dual(best_weights_jump, best_weights_powerup)
    else:
        best_weights = [random.uniform(-2, 2) for _ in range(weight_size)]
        best_score = avg_score_single(best_weights)

    epsilon_min = 0
    scores = []
    moving_avg = []

    for gen in range(generations):
        if dual_weights:
            if random.random() < epsilon:
                weights_jump = [random.uniform(-2, 2) for _ in range(weight_size_jump)]
                weights_powerup = [random.uniform(-2, 2) for _ in range(weight_size_powerup)]
            else:
                weights_jump = [w + random.uniform(-0.2, 0.2) for w in best_weights_jump]
                weights_powerup = [w + random.uniform(-0.2, 0.2) for w in best_weights_powerup]

            score = avg_score_dual(weights_jump, weights_powerup)
        else:
            if random.random() < epsilon:
                weights = [random.uniform(-2, 2) for _ in range(weight_size)]
            else:
                weights = [w + random.uniform(-0.2, 0.2) for w in best_weights]

            score = avg_score_single(weights)

        scores.append(score)
        avg = sum(scores[-100:]) / min(len(scores), 100)
        moving_avg.append(avg)

        print(f"Génération {gen} | Score moyen: {score:.2f} | ε={epsilon:.4f}")

        if score > best_score:
            best_score = score
            if dual_weights:
                best_weights_jump = weights_jump
                best_weights_powerup = weights_powerup
            else:
                best_weights = weights
            print("🎉 Nouveau meilleur score moyen:", best_score)

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    print("\n--- Entraînement terminé ---")
    print("Meilleur score moyen:", best_score)

    if dual_weights:
        print("Poids saut :", best_weights_jump)
        print("Poids power-up :", best_weights_powerup)
        final_weights = (best_weights_jump, best_weights_powerup)
    else:
        print("Poids optimaux trouvés:", best_weights)
        final_weights = best_weights

    plt.plot(scores, label="Scores moyens")
    plt.plot(moving_avg, label="Moyenne mobile 100 générations", color='red', linestyle='dashed')
    plt.xlabel("Générations")
    plt.ylabel("Score moyen")
    plt.title(name)
    plt.legend()
    plt.show()

    print("Lancement de la meilleure partie...")
    if dual_weights:
        run_game_function(best_weights_jump, best_weights_powerup, render=True, manual=False)
    else:
        run_game_function(final_weights, render=True, manual=False)


def play_manually(run_game_function):
    run_game_function(manual=True, render=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python jeuEpsilon.py [simple|complexe|powerup|manual]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "simple":
        train(run_game_function=run_game_simple, weight_size=5, generations=1000, epsilon=1, epsilon_decay=0.995, name="Mode Simple")
    elif mode == "complexe":
        train(run_game_function=run_game_complexe, weight_size=8, generations=1000, epsilon=1, epsilon_decay=0.995, name="Mode Complexe")
    elif mode == "powerup":
        train(
            run_game_function=run_game_powerUP,
            weight_size=(10, 10),
            batch_size=10,
            generations=5000,
            epsilon=1,
            epsilon_decay=0.999,
            name="Mode PowerUP",
            dual_weights=True
        )
    elif mode == "complexebonus":
        train(run_game_function=run_game_complexe_bonus, weight_size=10, batch_size=5, generations=10000, epsilon=1, epsilon_decay=0.9999, name="Mode Complexe Bonus")
    elif mode == "complexebonusseconddegre":
        train(run_game_function=run_game_complexe_bonus_second_degre, batch_size=5, weight_size=20, generations=10000, epsilon=1, epsilon_decay=0.99995, name="Mode Complexe Bonus")
    elif mode == "complexebonusquadratique":
        train(run_game_function=run_game_complexe_bonus_quadratique, batch_size=5, weight_size=30, generations=5000, epsilon=1, epsilon_decay=0.9995, name="Mode Complexe Bonus")
    
    else:
        print("Mode inconnu. Utilise 'simple', 'complexe', 'powerup' ou 'manual'")
