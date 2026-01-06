"""
Benchmark et comparaison des 3 algorithmes sur Snake
"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO, DQN, A2C
from envs.snake_env import SnakeEnv

os.makedirs("results", exist_ok=True)

print("=" * 70)
print("📊 BENCHMARK SNAKE : PPO vs DQN vs A2C")
print("=" * 70)

def evaluate_agent(model, env, num_episodes=20):
    """Évalue un agent sur plusieurs épisodes"""
    scores = []
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        done = False
        food_eaten = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            food_eaten = info.get('food_eaten', 0)
        
        scores.append(food_eaten)
    
    return scores

# Créer l'environnement
env = SnakeEnv(grid_size=10, render_mode=None)

# Définir le chemin vers le dossier des modèles
models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')

# Charger les modèles
models = {
    "PPO": PPO.load(os.path.join(models_dir, "ppo_snake")),
    "DQN": DQN.load(os.path.join(models_dir, "dqn_snake")),
    "A2C": A2C.load(os.path.join(models_dir, "a2c_snake")),
}

# Évaluer tous les modèles
print("\n📈 Évaluation des 3 algorithmes...")
print("-" * 70)

results = {}
for algo_name, model in models.items():
    print(f"\n🔄 Évaluation de {algo_name} (20 épisodes)...")
    scores = evaluate_agent(model, env, num_episodes=20)
    results[algo_name] = scores
    
    print(f"   ✅ Résultats {algo_name} :")
    print(f"      - Pommes moyennes : {np.mean(scores):.2f}")
    print(f"      - Écart-type      : {np.std(scores):.2f}")
    print(f"      - Min/Max         : {np.min(scores):.0f}/{np.max(scores):.0f}")

env.close()

# Créer les graphiques
print(f"\n📊 Génération des graphiques...")
print("-" * 70)

fig = plt.figure(figsize=(16, 10))

# Graphique 1 : Boxplot
ax1 = plt.subplot(2, 3, 1)
ax1.boxplot([results[algo] for algo in results.keys()],
            labels=list(results.keys()))
ax1.set_ylabel("Pommes mangées", fontsize=11, fontweight='bold')
ax1.set_title("Snake: Distribution des scores\n(Boxplot)", fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Graphique 2 : Barplot
ax2 = plt.subplot(2, 3, 2)
means = [np.mean(results[algo]) for algo in results.keys()]
stds = [np.std(results[algo]) for algo in results.keys()]
x = np.arange(len(results))
bars = ax2.bar(x, means, yerr=stds, capsize=10, alpha=0.7, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax2.set_xticks(x)
ax2.set_xticklabels(list(results.keys()), fontweight='bold')
ax2.set_ylabel("Pommes moyennes", fontsize=11, fontweight='bold')
ax2.set_title("Snake: Score moyen ± écart-type\n(Plus haut = Mieux)", fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

for bar, mean in zip(bars, means):
    ax2.text(bar.get_x() + bar.get_width()/2, mean + 0.2, f'{mean:.1f}',
             ha='center', va='bottom', fontweight='bold')

# Graphique 3 : Violin plot
ax3 = plt.subplot(2, 3, 3)
parts = ax3.violinplot([results[algo] for algo in results.keys()],
                        positions=range(len(results)),
                        showmeans=True, showmedians=True)
ax3.set_xticks(range(len(results)))
ax3.set_xticklabels(list(results.keys()), fontweight='bold')
ax3.set_ylabel("Pommes mangées", fontsize=11, fontweight='bold')
ax3.set_title("Snake: Distribution détaillée\n(Violin plot)", fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# Graphique 4 : Histogramme comparé
ax4 = plt.subplot(2, 3, 4)
for algo, scores in results.items():
    ax4.hist(scores, bins=8, alpha=0.5, label=algo)
ax4.set_xlabel("Pommes mangées", fontsize=11, fontweight='bold')
ax4.set_ylabel("Fréquence", fontsize=11, fontweight='bold')
ax4.set_title("Snake: Distribution des scores (Histogramme superposé)", fontsize=12, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')

# Graphique 5 : Comparaison radar
ax5 = plt.subplot(2, 3, 5)
metrics = ['Moyenne', 'Stabilité (1/σ)', 'Consistency']
def get_consistency(scores):
    mean_score = np.mean(scores)
    if mean_score > 0:
        return (np.max(scores) - np.min(scores)) / mean_score
    return 0

ppo_metrics = [
    np.mean(results['PPO']),
    1 / (np.std(results['PPO']) + 0.01),
    get_consistency(results['PPO'])
]
dqn_metrics = [
    np.mean(results['DQN']),
    1 / (np.std(results['DQN']) + 0.01),
    get_consistency(results['DQN'])
]
a2c_metrics = [
    np.mean(results['A2C']),
    1 / (np.std(results['A2C']) + 0.01),
    get_consistency(results['A2C'])
]

x_pos = np.arange(len(metrics))
width = 0.25

ax5.bar(x_pos - width, ppo_metrics, width, label='PPO', alpha=0.7)
ax5.bar(x_pos, dqn_metrics, width, label='DQN', alpha=0.7)
ax5.bar(x_pos + width, a2c_metrics, width, label='A2C', alpha=0.7)

ax5.set_ylabel('Score normalisé', fontsize=11, fontweight='bold')
ax5.set_title('Snake: Comparaison multi-critères', fontsize=12, fontweight='bold')
ax5.set_xticks(x_pos)
ax5.set_xticklabels(metrics, fontsize=10)
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3, axis='y')

# Graphique 6 : Tableau résumé
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')

tableau_data = []
tableau_data.append(['Algorithme', 'Pommes moy', 'Écart-type', 'Min/Max', 'Variance'])
tableau_data.append(['-'*12, '-'*12, '-'*12, '-'*12, '-'*12])

for algo in results.keys():
    scores = results[algo]
    variance = (np.max(scores) - np.min(scores)) / np.mean(scores) if np.mean(scores) > 0 else 0
    tableau_data.append([
        algo,
        f'{np.mean(scores):.1f}',
        f'{np.std(scores):.2f}',
        f'{np.min(scores):.0f}/{np.max(scores):.0f}',
        f'{variance:.2f}'
    ])

table = ax6.table(cellText=tableau_data, cellLoc='center', loc='center',
                  colWidths=[0.15, 0.15, 0.15, 0.15, 0.15])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.5)

for i in range(5):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

ax6.set_title('Tableau résumé', fontsize=12, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig("results/comparaison_snake.png", dpi=150, bbox_inches='tight')
print(f"✅ Graphique sauvegardé : results/comparaison_snake.png")

plt.show()

# Résumé final
print("\n" + "=" * 70)
print("✅ BENCHMARK SNAKE TERMINÉ !")
print("=" * 70)

print("\n🏆 RÉSULTATS FINAUX :")
print("-" * 70)

for algo in results.keys():
    scores = results[algo]
    print(f"\n   {algo}:")
    print(f"      • Pommes moyennes : {np.mean(scores):>6.1f}")
    print(f"      • Écart-type      : {np.std(scores):>6.2f}")
    print(f"      • Record          : {np.max(scores):>6.0f}")
    print(f"      • Pire partie     : {np.min(scores):>6.0f}")

best_algo = max(results.keys(), key=lambda x: np.mean(results[x]))
print(f"\n🏅 MEILLEUR ALGORITHME : {best_algo}")
print(f"   Pommes mangées en moyenne : {np.mean(results[best_algo]):.1f}")

print("\n" + "=" * 70)
print("📁 Résultats sauvegardés dans 'results/comparaison_snake.png'")
print("=" * 70)
