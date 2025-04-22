import pygame
import random
import sys
import math
import matplotlib.pyplot as plt

from jeuSimple import run_game as run_game_simple
from jeuComplexe import run_game_complexe
from jeuComplexeSecondDegre import run_game_complexe as run_game_complexe_second_degre

from jeuComplexeBonus import run_game_complexe as run_game_complexe_bonus
from jeuComplexeBonusSecondDegre import run_game_complexe as run_game_complexe_bonus_second_degre
from jeuComplexeBonusQuadratique import run_game_complexe as run_game_complexe_bonus_quadratique


from jeuPowerUP import run_game_powerUP
from jeuPowerUPSecondDegre import run_game_powerUP as run_game_powerUP_second_degre

from jeuSimple3Invincibilite import run_game_simple3Invincibilite

def train(run_game_function, weight_size, generations=1000, epsilon=0, epsilon_decay=1, name="No Name", dual_weights=False):
    if dual_weights:
        weight_size_jump, weight_size_invincibility = weight_size 
        best_weights_jump = [random.uniform(-1, 1) for _ in range(weight_size_jump)]
        best_weights_invincibility = [random.uniform(-1, 1) for _ in range(weight_size_invincibility)]
        best_score = run_game_function(best_weights_jump, best_weights_invincibility)
    else:
        best_weights = [random.uniform(-1, 1) for _ in range(weight_size)]
        best_score = run_game_function(best_weights)

    epsilon_min = 0
    scores = []
    moving_avg = []

    for gen in range(generations):
        if dual_weights:
            if random.random() < epsilon:
                weights_jump = [random.uniform(-2, 2) for _ in range(weight_size_jump)]
                weights_invincibility = [random.uniform(-2, 2) for _ in range(weight_size_invincibility)]
            else:
                weights_jump = [w + random.uniform(-0.2, 0.2) for w in best_weights_jump]
                weights_invincibility = [w + random.uniform(-0.2, 0.2) for w in best_weights_invincibility]

            score = run_game_function(weights_jump, weights_invincibility)
        else:
            if random.random() < epsilon:
                weights = [random.uniform(-2, 2) for _ in range(weight_size)]
            else:
                weights = [w + random.uniform(-0.2, 0.2) for w in best_weights]

            score = run_game_function(weights)

        scores.append(score)
        avg = sum(scores[-100:]) / min(len(scores), 100)
        moving_avg.append(avg)

        print(f"Génération {gen} | Score: {score:.2f} | ε={epsilon:.4f}")

        if score > best_score:
            best_score = score
            if dual_weights:
                best_weights_jump = weights_jump
                best_weights_invincibility = weights_invincibility
            else:
                best_weights = weights
            print("🎉 Nouveau meilleur score:", best_score)

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    print("\n--- Entraînement terminé ---")
    print("Meilleur score:", best_score)

    if dual_weights:
        print("Poids saut :", best_weights_jump)
        print("Poids invincibilité :", best_weights_invincibility)
        final_weights = (best_weights_jump, best_weights_invincibility)
    else:
        print("Poids optimaux trouvés:", best_weights)
        final_weights = best_weights

    plt.plot(scores, label="Scores")
    plt.plot(moving_avg, label="Moyenne mobile 100 générations", color='red', linestyle='dashed')
    plt.xlabel("Générations")
    plt.ylabel("Score")
    plt.title(name)
    plt.legend()
    plt.show()

    print("Lancement de la meilleure partie...")
    if dual_weights:
        run_game_function(best_weights_jump, best_weights_invincibility, render=True, manual=False)
    else:
        run_game_function(final_weights, render=True, manual=False)


def play_manually(run_game_function):
    run_game_function(manual=True, render=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python jeuEpsilon.py [simple|complexe|powerup|manual|simple3Invincibilite]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "simple":
        train(run_game_function=run_game_simple, weight_size=5, generations=1000, epsilon=1, epsilon_decay=0.995, name="Mode Simple")
    elif mode == "complexe":
        train(run_game_function=run_game_complexe, weight_size=8, generations=1000, epsilon=1, epsilon_decay=0.995, name="Mode Complexe")
    elif mode == "complexeseconddegre":
        train(run_game_function=run_game_complexe_second_degre, weight_size=16, generations=5000, epsilon=1, epsilon_decay=0.9995, name="Mode Complexe")
    elif mode == "complexebonus":
        train(run_game_function=run_game_complexe_bonus, weight_size=10, generations=10000, epsilon=1, epsilon_decay=0.9995, name="Mode Complexe Bonus")
    elif mode == "complexebonusseconddegre":
        train(run_game_function=run_game_complexe_bonus_second_degre, weight_size=20, generations=20000, epsilon=1, epsilon_decay=0.9999, name="Mode Complexe Bonus")
    elif mode == "complexebonusquadratique":
        train(run_game_function=run_game_complexe_bonus_quadratique, weight_size=30, generations=20000, epsilon=1, epsilon_decay=0.9999, name="Mode Complexe Bonus")
    elif mode == "powerup":
        train(
            run_game_function=run_game_powerUP,
            weight_size=(10, 10),
            generations=10000,
            epsilon=1,
            epsilon_decay=0.9995,
            name="Mode PowerUP",
            dual_weights=True
        )
    elif mode == "powerupseconddegre":
        train(
            run_game_function=run_game_powerUP_second_degre,
            weight_size=(20, 20),
            generations=200000,
            epsilon=1,
            epsilon_decay=0.99999,
            name="Mode PowerUP",
            dual_weights=True
        )
    elif mode == "simple3invincibilite": 
        train(
            run_game_function=run_game_simple3Invincibilite, 
            weight_size=(5, 5), 
            generations=50000,
            epsilon=1,
            epsilon_decay=0.9999,
            name="Mode Simple avec Invincibilité",
            dual_weights=True
        )
    elif mode == "manualsimple":
        play_manually(run_game_function=run_game_simple)
    elif mode == "manualcomplexe":
        play_manually(run_game_function=run_game_complexe)
    else:
        print("Mode inconnu. Utilise 'simple', 'complexe', 'powerup', 'manual' ou 'simple3Invincibilite'")
