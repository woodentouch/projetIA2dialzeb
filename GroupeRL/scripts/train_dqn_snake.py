"""
Entraînement d'un agent DQN sur Snake
"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gymnasium as gym
from stable_baselines3 import DQN

# Importer l'environnement personnalisé
from envs.snake_env import SnakeEnv

os.makedirs("models", exist_ok=True)

print("=" * 60)
print("🚀 Entraînement DQN sur Snake-v0")
print("=" * 60)

# Créer l'environnement Snake
env = SnakeEnv(grid_size=10, render_mode=None)
print(f"✅ Environnement créé : Snake-v0")
print(f"   - Grille : 10x10")
print(f"   - Actions : 4 (Haut, Droite, Bas, Gauche)")
print(f"   - Observation : 6 variables (position, pomme, direction, longueur)")

# Créer le modèle DQN
model = DQN(
    "MlpPolicy",
    env,
    learning_rate=1e-3,
    buffer_size=50000,
    learning_starts=1000,
    target_update_interval=500,
    exploration_fraction=0.1,
    exploration_initial_eps=1.0,
    exploration_final_eps=0.05,
    verbose=1,
    device="cpu"
)

print(f"\n✅ Modèle DQN créé")
print(f"   - Learning rate : 1e-3")
print(f"   - Buffer size : 50000")
print(f"   - Learning starts : 1000")

# Entraîner
print(f"\n⏳ Entraînement en cours... (500,000 timesteps)")
print(f"   Cela devrait prendre environ 10-15 minutes...")
print("-" * 60)

model.learn(total_timesteps=500000)

# Sauvegarder
model.save("models/dqn_snake")
print("-" * 60)
print(f"\n✅ Entraînement DQN terminé !")
print(f"   Modèle sauvegardé : models/dqn_snake.zip")

env.close()
print("=" * 60)
