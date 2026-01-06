
"""
Entraînement d'un agent A2C sur Snake
Note: A2C supporte les actions discrètes, contrairement à SAC
"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gymnasium as gym
from stable_baselines3 import A2C

# Importer l'environnement personnalisé
from envs.snake_env import SnakeEnv

os.makedirs("models", exist_ok=True)

print("=" * 60)
print("🚀 Entraînement A2C sur Snake-v0")
print("=" * 60)

# Créer l'environnement Snake
env = SnakeEnv(grid_size=10, render_mode=None)
print(f"✅ Environnement créé : Snake-v0")
print(f"   - Grille : 10x10")
print(f"   - Actions : 4 (Haut, Droite, Bas, Gauche)")
print(f"   - Observation : 6 variables (position, pomme, direction, longueur)")

# Créer le modèle A2C
model = A2C(
    "MlpPolicy",
    env,
    learning_rate=7e-4,
    n_steps=5,
    gamma=0.99,
    gae_lambda=0.98,
    ent_coef=0.0,
    use_rms_prop=False,
    use_sde=False,
    verbose=1,
    device="cpu"
)

print(f"\n✅ Modèle A2C créé")
print(f"   - Learning rate : 7e-4")
print(f"   - N steps : 5")
print(f"   - Gamma : 0.99")

# Entraîner
print(f"\n⏳ Entraînement en cours... (500,000 timesteps)")
print(f"   Cela devrait prendre environ 10-15 minutes...")
print("-" * 60)

model.learn(total_timesteps=500000)

# Sauvegarder
model.save("models/a2c_snake")
print("-" * 60)
print(f"\n✅ Entraînement A2C terminé !")
print(f"   Modèle sauvegardé : models/a2c_snake.zip")

env.close()
print("=" * 60)
