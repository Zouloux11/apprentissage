import pygame
import random
import sys
import math
import matplotlib.pyplot as plt

from jeuSimple import run_game as run_game_simple
from jeuComplexe import run_game_complexe
from jeuPowerUP import run_game_powerUP

def play_manually(run_game_function):
    run_game_function(manual=True, render=True)

def crossover(parent1, parent2):
    return [(p1 + p2) / 2 for p1, p2 in zip(parent1, parent2)]

def mutate(weights, mutation_rate=0.2, mutation_strength=0.5):
    return [
        w + random.uniform(-mutation_strength, mutation_strength) if random.random() < mutation_rate else w
        for w in weights
    ]

def train_genetic(
    run_game_function,
    weight_size,
    generations=100,
    population_size=30,
    elite_size=5,
    mutation_rate=0.2,
    mutation_strength=0.3,
    name="Genetic Algorithm",
    dual_weights=False
):
    if dual_weights:
        # Pour les modes à deux sets de poids (mode PowerUp)
        weight_size_jump, weight_size_powerup = weight_size
        population = [
            (
                [random.uniform(-1, 1) for _ in range(weight_size_jump)],
                [random.uniform(-1, 1) for _ in range(weight_size_powerup)]
            )
            for _ in range(population_size)
        ]
    else:
        # Pour les modes à un set de poids (simple/complexe)
        population = [
            [random.uniform(-1, 1) for _ in range(weight_size)]
            for _ in range(population_size)
        ]
    
    scores_history = []
    moving_avg = []

    for gen in range(generations):
        if dual_weights:
            # Évaluation avec double poids
            scored_population = [
                ((weights_jump, weights_powerup), run_game_function(weights_jump, weights_powerup))
                for weights_jump, weights_powerup in population
            ]
        else:
            # Évaluation avec un seul poids
            scored_population = [(weights, run_game_function(weights)) for weights in population]
        
        scored_population.sort(key=lambda x: x[1], reverse=True)
        elites = [weights for weights, _ in scored_population[:elite_size]]
        best_score = scored_population[0][1]

        print(f"Génération {gen} | Meilleur score: {best_score:.2f}")

        scores_history.append(best_score)
        if len(scores_history) > 100:
            moving_avg.append(sum(scores_history[-100:]) / 100)
        else:
            moving_avg.append(sum(scores_history) / len(scores_history))

        new_population = elites.copy()
        
        while len(new_population) < population_size:
            parent1 = random.choice(elites)
            parent2 = random.choice(elites)
            
            if dual_weights:
                # Croisement et mutation pour chaque ensemble de poids
                parent1_jump, parent1_powerup = parent1
                parent2_jump, parent2_powerup = parent2
                
                child_jump = crossover(parent1_jump, parent2_jump)
                child_jump = mutate(child_jump, mutation_rate, mutation_strength)
                
                child_powerup = crossover(parent1_powerup, parent2_powerup)
                child_powerup = mutate(child_powerup, mutation_rate, mutation_strength)
                
                new_population.append((child_jump, child_powerup))
            else:
                child = crossover(parent1, parent2)
                child = mutate(child, mutation_rate, mutation_strength)
                new_population.append(child)

        population = new_population

    best_weights = scored_population[0][0]
    print("\n--- Entraînement terminé ---")
    print("Meilleur score:", scored_population[0][1])
    
    if dual_weights:
        best_weights_jump, best_weights_powerup = best_weights
        print("Poids de saut optimaux:", best_weights_jump)
        print("Poids de powerup optimaux:", best_weights_powerup)
    else:
        print("Poids optimaux trouvés:", best_weights)

    plt.plot(scores_history, label="Scores")
    plt.plot(moving_avg, label="Moyenne mobile", color='red', linestyle='dashed')
    plt.xlabel("Générations")
    plt.ylabel("Score")
    plt.title(name)
    plt.legend()
    plt.savefig(f"{name.replace(' ', '_')}.png")
    plt.show()

    print("Lancement de la meilleure partie...")
    if dual_weights:
        run_game_function(best_weights_jump, best_weights_powerup, render=True, manual=False)
    else:
        run_game_function(best_weights, render=True, manual=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python jeuGenetique.py [simple|complexe|powerup|manual|manual_powerup]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "simple":
        train_genetic(
            run_game_function=run_game_simple,
            weight_size=5,
            generations=50,
            population_size=30,
            name="Genetic - Simple"
        )
    elif mode == "complexe":
        train_genetic(
            run_game_function=run_game_complexe,
            weight_size=8,
            generations=50,
            population_size=30,
            name="Genetic - Complexe"
        )
    elif mode == "powerup":
        train_genetic(
            run_game_function=run_game_powerUP,
            weight_size=(10, 10),
            generations=100,
            population_size=40,
            elite_size=8,
            mutation_rate=0.2,
            mutation_strength=0.3,
            name="Genetic - PowerUP",
            dual_weights=True
        )
    elif mode == "manual":
        play_manually(run_game_complexe)
    elif mode == "manual_powerup":
        play_manually(run_game_powerUP)
    else:
        print("Mode inconnu. Utilise 'simple', 'complexe', 'powerup', 'manual' ou 'manual_powerup'")