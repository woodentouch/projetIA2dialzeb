"""
Jeu Snake interactif - Jouez manuellement avec les flèches du clavier !
"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
script_dir = os.path.dirname(__file__)
project_dir = os.path.join(script_dir, '..')
sys.path.insert(0, project_dir)

import pygame
from envs.snake_env import SnakeEnv, Direction

print("=" * 70)
print("🎮 JEU SNAKE INTERACTIF")
print("=" * 70)
print("\n📋 CONTRÔLES :")
print("   ⬆️  Flèche HAUT     → Aller vers le haut")
print("   ⬅️  Flèche GAUCHE   → Aller vers la gauche")
print("   ⬇️  Flèche BAS      → Aller vers le bas")
print("   ➡️  Flèche DROITE   → Aller vers la droite")
print("   Q                  → Quitter le jeu")
print("=" * 70)
print("\n🚀 Démarrage du jeu...")
print()

# Créer l'environnement
env = SnakeEnv(grid_size=10, render_mode="human")

# État du jeu
obs, info = env.reset()
done = False
total_reward = 0
food_eaten = 0
steps = 0

print("🐍 Mangez les pommes ! 🍎")
print("-" * 70)

# Boucle de jeu
while not done:
    # Rendu
    env.render()
    
    # Gestion des événements Pygame
    action = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                action = 0  # Haut
            elif event.key == pygame.K_RIGHT:
                action = 1  # Droite
            elif event.key == pygame.K_DOWN:
                action = 2  # Bas
            elif event.key == pygame.K_LEFT:
                action = 3  # Gauche
            elif event.key == pygame.K_q:
                print("\n👋 Jeu interrompu par l'utilisateur")
                done = True
                break
    
    # Si aucune action n'a été pressée, garder la même direction
    if action is None:
        action = env.direction.value
    
    # Effectuer l'action
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    
    total_reward += reward
    food_eaten = info.get('food_eaten', 0)
    steps += 1
    
    # Afficher les stats en temps réel
    if steps % 10 == 0:
        print(f"⏱️  Étapes: {steps:4d} | 🍎 Pommes: {food_eaten:2d} | ⭐ Score: {total_reward:6.1f}")

env.close()

print("\n" + "=" * 70)
print("✅ PARTIE TERMINÉE !")
print("=" * 70)
print(f"\n📊 STATISTIQUES FINALES :")
print(f"   ⏱️  Nombre d'étapes : {steps}")
print(f"   🍎 Pommes mangées : {food_eaten}")
print(f"   ⭐ Score total : {total_reward:.1f}")
print("=" * 70)
