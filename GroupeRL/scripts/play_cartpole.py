"""
CartPole interactif - Jouez manuellement avec les flèches du clavier !
"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
script_dir = os.path.dirname(__file__)
project_dir = os.path.join(script_dir, '..')
sys.path.insert(0, project_dir)

import gymnasium as gym
import pygame

print("=" * 70)
print("🎮 CARTPOLE INTERACTIF")
print("=" * 70)
print("\n📋 CONTRÔLES :")
print("   ⬅️  Flèche GAUCHE   → Pousser le chariot à GAUCHE")
print("   ➡️  Flèche DROITE   → Pousser le chariot à DROITE")
print("   Q                  → Quitter le jeu")
print("=" * 70)
print("\n🚀 Démarrage du jeu...")
print("\n⚖️  OBJECTIF :")
print("   Gardez le bâton équilibré le plus longtemps possible !")
print("   Ne laissez pas le bâton tomber (angle > 12°)")
print("   Ne dépassez pas 2.4 unités de distance du centre")
print("-" * 70)
print()

# Créer l'environnement CartPole
env = gym.make("CartPole-v1", render_mode="human")

# État du jeu
obs, info = env.reset()
done = False
total_reward = 0
steps = 0

# Variable pour tracker l'action précédente (par défaut, pas de mouvement)
last_action = 0

# Boucle de jeu
while not done:
    # Rendu
    env.render()
    
    # Gestion des événements Pygame
    action = last_action  # Garder l'action précédente par défaut
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                action = 0  # Pousser à gauche
                last_action = 0
            elif event.key == pygame.K_RIGHT:
                action = 1  # Pousser à droite
                last_action = 1
            elif event.key == pygame.K_q:
                print("\n👋 Jeu interrompu par l'utilisateur")
                done = True
                break
    
    # Effectuer l'action
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    
    total_reward += reward
    steps += 1
    
    # Afficher les stats en temps réel
    if steps % 10 == 0:
        print(f"⏱️  Étapes: {steps:4d} | ⭐ Score: {total_reward:6.1f}")

env.close()

print("\n" + "=" * 70)
print("✅ PARTIE TERMINÉE !")
print("=" * 70)
print(f"\n📊 STATISTIQUES FINALES :")
print(f"   ⏱️  Nombre d'étapes : {steps}")
print(f"   ⭐ Score total : {total_reward:.1f}")
print(f"   🎯 Bâton équilibré pendant {steps} pas de temps")
print("=" * 70)
