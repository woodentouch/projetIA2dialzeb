"""
Pendulum interactif - Jouez manuellement avec les flèches du clavier !
Version ralentie pour plus de facilité
"""

import sys
import os
import time

# Ajouter le répertoire parent au chemin Python
script_dir = os.path.dirname(__file__)
project_dir = os.path.join(script_dir, '..')
sys.path.insert(0, project_dir)

import gymnasium as gym
import pygame

print("=" * 70)
print("🎮 PENDULUM INTERACTIF (VERSION RALENTIE)")
print("=" * 70)
print("\n📋 CONTRÔLES :")
print("   ⬅️  Flèche GAUCHE   → Appliquer un couple NÉGATIF (gauche)")
print("   ➡️  Flèche DROITE   → Appliquer un couple POSITIF (droite)")
print("   ESPACE             → Pas d'action (couple = 0)")
print("   Q                  → Quitter le jeu")
print("=" * 70)
print("\n🚀 Démarrage du jeu...")
print("\n⚖️  OBJECTIF :")
print("   Équilibrez le pendule en position VERTICALE (angle = 0)")
print("   Utilisez les couples pour contrôler le mouvement")
print("   ⏱️  Version ralentie pour faciliter le jeu humain")
print("-" * 70)
print()

# Créer l'environnement Pendulum avec vitesse réduite
env = gym.make("Pendulum-v1", render_mode="human")

# État du jeu
obs, info = env.reset()
done = False
total_reward = 0
steps = 0

# Variable pour tracker l'action précédente
last_action = None
frame_delay = 0.1  # 100ms entre chaque frame = ralentissement

# Boucle de jeu
while not done:
    # Ralentissement du jeu
    time.sleep(frame_delay)
    
    # Rendu
    env.render()
    
    # Gestion des événements Pygame
    action = 0  # Pas d'action par défaut
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                action = -2.0  # Couple négatif (gauche)
            elif event.key == pygame.K_RIGHT:
                action = 2.0  # Couple positif (droite)
            elif event.key == pygame.K_SPACE:
                action = 0.0  # Pas d'action
            elif event.key == pygame.K_q:
                print("\n👋 Jeu interrompu par l'utilisateur")
                done = True
                break
    
    # Effectuer l'action
    obs, reward, terminated, truncated, info = env.step([action])
    done = terminated or truncated
    
    total_reward += reward
    steps += 1
    
    # Afficher les stats en temps réel
    if steps % 5 == 0:
        angle = obs[0]  # Premier élément de l'observation
        angle_vitesse = obs[1]
        print(f"⏱️  Étapes: {steps:4d} | 📐 Angle: {angle:7.3f} rad | 🔄 Vitesse: {angle_vitesse:7.3f} rad/s | ⭐ Score: {total_reward:7.1f}")

env.close()

print("\n" + "=" * 70)
print("✅ PARTIE TERMINÉE !")
print("=" * 70)
print(f"\n📊 STATISTIQUES FINALES :")
print(f"   ⏱️  Nombre d'étapes : {steps}")
print(f"   ⭐ Score total : {total_reward:.1f}")
print(f"   ⏪ Jeu ralenti pour faciliter le contrôle humain")
print("=" * 70)
