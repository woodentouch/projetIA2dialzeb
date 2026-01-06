"""
Test des agents Snake avec visualisation Pygame
"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
script_dir = os.path.dirname(__file__)
project_dir = os.path.join(script_dir, '..')
sys.path.insert(0, project_dir)

import gymnasium as gym
from stable_baselines3 import PPO, DQN, A2C
from envs.snake_env import SnakeEnv

print("=" * 70)
print("🎮 TEST DES AGENTS SNAKE AVEC VISUALISATION")
print("=" * 70)

# Créer l'environnement avec rendu Pygame
env = SnakeEnv(grid_size=10, render_mode="human")

# Charger les modèles avec chemins absolus
models_dir = os.path.join(project_dir, "models")
models = {
    "PPO": PPO.load(os.path.join(models_dir, "ppo_snake")),
    "DQN": DQN.load(os.path.join(models_dir, "dqn_snake")),
    "A2C": A2C.load(os.path.join(models_dir, "a2c_snake")),
}

for algo_name, model in models.items():
    print(f"\n🎬 Test de {algo_name} sur Snake 🐍")
    print(f"   Vous verrez le serpent jouer avec Pygame !")
    
    # 3 épisodes de test
    scores = []
    for episode in range(3):
        obs, info = env.reset()
        done = False
        total_reward = 0
        food_eaten = 0
        steps = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            food_eaten = info.get('food_eaten', 0)
            steps += 1
            
            # Afficher le jeu
            env.render()
        
        scores.append(food_eaten)
        print(f"   Episode {episode+1}: Pommes = {food_eaten}, Score = {total_reward:.1f}, Étapes = {steps}")
    
    avg_score = sum(scores) / len(scores)
    print(f"   ✅ Pommes moyennes {algo_name} : {avg_score:.1f}")
    print()

env.close()

print("=" * 70)
print("✅ TESTS TERMINÉS !")
print("=" * 70)
print("\n💡 Résumé :")
print("   - Les serpents viennent d'apprendre à jouer !")
print("   - Chaque couleur = algorithme différent")
print("   - Le score = nombre de pommes mangées")
print("=" * 70)
