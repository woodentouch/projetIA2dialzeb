# Réalisation du Projet RL : Contrôle & Jeux

## 📋 Vue d'ensemble du projet

**Objectif** : Apprendre à un agent à jouer à un jeu vidéo ou contrôler un système physique en utilisant le Reinforcement Learning.

**Librairies principales** :
- **Stable-Baselines3** : Implémentations modernes des algorithmes RL (PPO, DQN, SAC)
- **Gymnasium** : Environnements standardisés pour tester les agents RL

**Algorithmes à comparer** : PPO, DQN, SAC

---

## 🎯 Étapes de réalisation

### Étape 1 : Configuration de l'environnement

#### 1.1 Créer un environnement virtuel Python
```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
```

#### 1.2 Installer les dépendances requises
```bash
pip install stable-baselines3 gymnasium pygame numpy matplotlib tensorboard
```

**Explication des packages** :
- `stable-baselines3` : Les algos PPO, DQN, SAC
- `gymnasium` : Les environnements de jeu
- `pygame` : Pour visualiser les jeux
- `numpy` : Calculs numériques
- `matplotlib` : Visualisation des résultats
- `tensorboard` : Suivi de l'entraînement

---

### Étape 2 : Choisir l'environnement de test

#### Deux catégories possibles :

**Option A : Jeux vidéo (recommandé pour démarrer)**
- `CartPole-v1` ⭐ (PLUS SIMPLE - Commencer ici)
- `LunarLander-v2` (Niveau moyen)
- `Breakout-v4` (Niveau avancé - nécessite `stable-baselines3[atari]`)

**Option B : Systèmes physiques (plus complexes)**
- `Pendulum-v1` (Pendule inversé)
- `MountainCar-v0` (Voiture en montagne)

### ✅ Recommandation pour débuter :
**Commencer avec `CartPole-v1`** (simple, rapide, bon pour les tests)

---

### Étape 3 : Créer les scripts de base

Créer la structure suivante dans le dossier du projet :

```
GroupeRL/
├── scripts/
│   ├── train_ppo.py
│   ├── train_dqn.py
│   ├── train_sac.py
│   ├── test_agent.py
│   └── benchmark_algos.py
├── models/
│   ├── ppo_cartpole.zip
│   ├── dqn_cartpole.zip
│   └── sac_cartpole.zip
├── results/
│   └── comparaison_algos.png
└── REALISATION.md
```

---

### Étape 4 : Entraîner les trois algorithmes

#### 4.1 Script d'entraînement PPO

**Fichier** : `scripts/train_ppo.py`

```python
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback

# Créer l'environnement
env = gym.make("CartPole-v1")

# Créer le modèle PPO
model = PPO(
    "MlpPolicy",
    env,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    learning_rate=3e-4,
    verbose=1,
    device="cpu"  # ou "cuda" si GPU disponible
)

# Entraîner
model.learn(total_timesteps=50000)

# Sauvegarder
model.save("models/ppo_cartpole")

env.close()
print("✅ Entraînement PPO terminé !")
```

#### 4.2 Script d'entraînement DQN

**Fichier** : `scripts/train_dqn.py`

```python
import gymnasium as gym
from stable_baselines3 import DQN

# Créer l'environnement
env = gym.make("CartPole-v1")

# Créer le modèle DQN
model = DQN(
    "MlpPolicy",
    env,
    learning_rate=1e-3,
    buffer_size=10000,
    learning_starts=1000,
    target_update_interval=500,
    verbose=1,
    device="cpu"
)

# Entraîner
model.learn(total_timesteps=50000)

# Sauvegarder
model.save("models/dqn_cartpole")

env.close()
print("✅ Entraînement DQN terminé !")
```

#### 4.3 Script d'entraînement SAC

**Fichier** : `scripts/train_sac.py`

```python
import gymnasium as gym
from stable_baselines3 import SAC

# Créer l'environnement
env = gym.make("CartPole-v1")

# Créer le modèle SAC
model = SAC(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    buffer_size=10000,
    learning_starts=100,
    verbose=1,
    device="cpu"
)

# Entraîner
model.learn(total_timesteps=50000)

# Sauvegarder
model.save("models/sac_cartpole")

env.close()
print("✅ Entraînement SAC terminé !")
```

**À FAIRE DANS CETTE ÉTAPE** :
1. Créer les fichiers `train_ppo.py`, `train_dqn.py`, `train_sac.py`
2. Exécuter chaque script :
   ```bash
   python scripts/train_ppo.py
   python scripts/train_dqn.py
   python scripts/train_sac.py
   ```
3. Attendre que les 3 entraînements se terminent (⏱️ 5-10 minutes au total)

---

### Étape 5 : Tester les agents entraînés

#### 5.1 Script de test simple

**Fichier** : `scripts/test_agent.py`

```python
import gymnasium as gym
from stable_baselines3 import PPO, DQN, SAC

# Créer l'environnement
env = gym.make("CartPole-v1", render_mode="human")

# Tester chaque modèle
models = {
    "PPO": PPO.load("models/ppo_cartpole", env=env),
    "DQN": DQN.load("models/dqn_cartpole", env=env),
    "SAC": SAC.load("models/sac_cartpole", env=env)
}

for algo_name, model in models.items():
    print(f"\n🎮 Test de {algo_name}...")
    
    # 5 épisodes de test
    for episode in range(5):
        obs, info = env.reset()
        done = False
        total_reward = 0
        steps = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
        
        print(f"  Episode {episode+1}: Score = {total_reward:.0f}, Étapes = {steps}")
    
    print(f"✅ Tests de {algo_name} terminés !")

env.close()
```

**À FAIRE** :
```bash
python scripts/test_agent.py
```

Vous verrez une **fenêtre de jeu** s'afficher avec le bâton qui essaie de rester équilibré. Les agents entraînés vont contrôler le mouvement du chariot.

---

### Étape 6 : Comparer les performances

#### 6.1 Benchmark des trois algorithmes

**Fichier** : `scripts/benchmark_algos.py`

```python
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO, DQN, SAC

def evaluate_agent(model, env, num_episodes=10):
    """Évalue un agent sur plusieurs épisodes"""
    scores = []
    
    for _ in range(num_episodes):
        obs, _ = env.reset()
        done = False
        episode_reward = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            episode_reward += reward
        
        scores.append(episode_reward)
    
    return scores

# Créer l'environnement
env = gym.make("CartPole-v1")

# Charger les modèles
models = {
    "PPO": PPO.load("models/ppo_cartpole"),
    "DQN": DQN.load("models/dqn_cartpole"),
    "SAC": SAC.load("models/sac_cartpole")
}

# Évaluer tous les modèles
results = {}
for algo_name, model in models.items():
    print(f"Évaluation de {algo_name}...")
    scores = evaluate_agent(model, env, num_episodes=20)
    results[algo_name] = scores
    print(f"  Moyenne: {np.mean(scores):.2f}")
    print(f"  Écart-type: {np.std(scores):.2f}")
    print(f"  Min/Max: {np.min(scores):.0f}/{np.max(scores):.0f}")

# Afficher les résultats
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Graphique 1 : Boîtes à moustaches
axes[0].boxplot([results[algo] for algo in results.keys()], 
                labels=list(results.keys()))
axes[0].set_ylabel("Score")
axes[0].set_title("Comparaison des scores (CartPole-v1)")
axes[0].grid(True, alpha=0.3)

# Graphique 2 : Moyenne et écart-type
means = [np.mean(results[algo]) for algo in results.keys()]
stds = [np.std(results[algo]) for algo in results.keys()]
x = np.arange(len(results))
axes[1].bar(x, means, yerr=stds, capsize=10, alpha=0.7)
axes[1].set_xticks(x)
axes[1].set_xticklabels(list(results.keys()))
axes[1].set_ylabel("Score moyen")
axes[1].set_title("Score moyen avec intervalle de confiance")
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("results/comparaison_algos.png", dpi=100)
print("\n📊 Graphique sauvegardé dans 'results/comparaison_algos.png'")
plt.show()

env.close()
```

**À FAIRE** :
```bash
python scripts/benchmark_algos.py
```

Cela générera un graphique comparant les trois algorithmes.

---

## 🎮 Guide complet pour tester avec des jeux

### Option 1 : Visualisation simple pendant l'entraînement

**Ajouter ceci à votre script d'entraînement** :

```python
import gymnasium as gym
from stable_baselines3 import PPO

# Avec render_mode="human" pour afficher le jeu
env = gym.make("CartPole-v1", render_mode="human")

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)

env.close()
```

### Option 2 : Test interactif avec ralentissement

**Fichier** : `scripts/play_game.py`

```python
import gymnasium as gym
from stable_baselines3 import PPO
import time

env = gym.make("CartPole-v1", render_mode="human")
model = PPO.load("models/ppo_cartpole")

obs, _ = env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, _ = env.step(action)
    done = terminated or truncated
    
    time.sleep(0.05)  # Ralentir pour mieux voir

env.close()
```

### Option 3 : Enregistrer une vidéo

**Fichier** : `scripts/record_video.py`

```python
import gymnasium as gym
from gymnasium.wrappers import RecordVideo
from stable_baselines3 import PPO

env = gym.make("CartPole-v1")
env = RecordVideo(env, video_folder="videos/")

model = PPO.load("models/ppo_cartpole")

obs, _ = env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, _ = env.step(action)
    done = terminated or truncated

env.close()
print("✅ Vidéo enregistrée dans 'videos/'")
```

### Option 4 : Tester sur plusieurs environnements différents

**Autres environnements simples à tester** :

```python
# Essayer LunarLander (alunissage)
env = gym.make("LunarLander-v2", render_mode="human")

# Ou MountainCar (voiture en montagne)
env = gym.make("MountainCar-v0", render_mode="human")

# Ou Pendulum (pendule inversé - continu)
env = gym.make("Pendulum-v1", render_mode="human")
```

---

## 📊 Résumé des étapes d'exécution

```
1. ✅ Installer Python et dépendances (5 min)
   → pip install stable-baselines3 gymnasium pygame numpy matplotlib

2. ✅ Entraîner PPO (2-3 min)
   → python scripts/train_ppo.py

3. ✅ Entraîner DQN (2-3 min)
   → python scripts/train_dqn.py

4. ✅ Entraîner SAC (2-3 min)
   → python scripts/train_sac.py

5. ✅ Tester les agents (1 min)
   → python scripts/test_agent.py

6. ✅ Comparer les résultats (1-2 min)
   → python scripts/benchmark_algos.py
   → Générera "results/comparaison_algos.png"

⏱️ Temps total : 15-20 minutes
```

---

## 🔍 Interprétation des résultats

### CartPole-v1
- **Objectif** : Garder un bâton en équilibre sur un chariot mobile
- **Score maximal** : 500 (réussite complète)
- **Score acceptable** : > 400

### Comment interpréter les courbes :
1. **Moyenne** : Performance globale (plus haut = mieux)
2. **Écart-type** : Stabilité (plus bas = plus stable)
3. **Min/Max** : Consistency (Min proche de la Moyenne = bon)

### Résultats typiques :
- **PPO** : Stable, performant (environ 450-500)
- **DQN** : Peut être instable avec peu de données
- **SAC** : Bon équilibre, mais peut converger moins vite

---

## 🚀 Extensions possibles

1. **Changez d'environnement** : LunarLander, MountainCar, etc.
2. **Hyperparamètres** : Ajustez `learning_rate`, `n_steps`, etc.
3. **Entraînement plus long** : Augmentez `total_timesteps`
4. **Atari games** : Installez `stable-baselines3[atari]` pour des jeux plus complexes
5. **Analyse** : Créez d'autres graphiques (courbes d'apprentissage, etc.)

---

## ⚠️ Dépannage

| Problème | Solution |
|----------|----------|
| ImportError pour gymnasium | `pip install gymnasium` |
| ImportError pour stable-baselines3 | `pip install stable-baselines3` |
| La fenêtre de jeu ne s'affiche pas | Vérifiez que pygame est installé : `pip install pygame` |
| Entraînement très lent | Réduisez `total_timesteps` pour les tests rapides |
| Erreur GPU | Remplacez `device="cuda"` par `device="cpu"` |

---

## 📝 Fichiers de référence

- [Stable-Baselines3 Docs](https://stable-baselines3.readthedocs.io/)
- [Gymnasium Documentation](https://gymnasium.farama.org/)
- [PPO Paper](https://arxiv.org/abs/1707.06347)
- [DQN Paper](https://arxiv.org/abs/1312.5602)
- [SAC Paper](https://arxiv.org/abs/1801.01290)

---

---

## 🐍 BONUS : Entraîner les agents sur Snake !

Nous avons créé un **environnement Snake personnalisé avec Pygame** pour un visuel vraiment beau ! 🎨

### Étape 0 : Structure créée

```
GroupeRL/
├── envs/
│   ├── __init__.py
│   └── snake_env.py          ← Environnement Snake personnalisé
├── scripts/
│   ├── train_ppo_snake.py
│   ├── train_dqn_snake.py
│   ├── train_sac_snake.py
│   ├── test_snake.py         ← Voir les serpents jouer
│   └── benchmark_snake.py    ← Comparer les algos sur Snake
├── models/
│   └── ppo/dqn/sac_snake.zip
└── results/
    └── comparaison_snake.png
```

### Étape 1 : Entraîner les agents sur Snake

#### 1.1 Entraîner PPO (3-5 min)
```bash
python scripts/train_ppo_snake.py
```

#### 1.2 Entraîner DQN (3-5 min)
```bash
python scripts/train_dqn_snake.py
```

#### 1.3 Entraîner SAC (3-5 min)
```bash
python scripts/train_sac_snake.py
```

**Temps total** : ~15 minutes

### Étape 2 : Voir les serpents jouer avec Pygame 🐍

```bash
python scripts/test_snake.py
```

**Vous verrez** :
- ✅ Une fenêtre avec une grille 10x10
- 🐍 Un serpent vert qui se déplace
- 🍎 Une pomme rouge à manger
- 📊 Le score (pommes mangées) en haut
- 🎮 3 épisodes par algorithme

**Visuel** :
```
┌─────────────────────┐
│ 🐍🐍🐍             │
│       🍎            │  ← Actions : 0=Haut, 1=Droite
│                     │    2=Bas, 3=Gauche
│                     │
└─────────────────────┘
Score: 5  Length: 4  Steps: 127
```

### Étape 3 : Comparer les performances (2 min)

```bash
python scripts/benchmark_snake.py
```

**Génère** :
- 6 graphiques comparant PPO vs DQN vs SAC
- Tableau récapitulatif des résultats
- Quel algo est le meilleur pour Snake ? 🏆
- Fichier : `results/comparaison_snake.png`

---

### 🎮 Comment fonctionne Snake-v0 ?

**Objectif** : Manger le plus de pommes possible

**Actions** : 4 directions
- 0 = Haut ⬆️
- 1 = Droite ➡️
- 2 = Bas ⬇️
- 3 = Gauche ⬅️

**Observation** : 6 variables (normalisées entre 0 et 1)
1. Position X de la tête
2. Position Y de la tête
3. Position X de la pomme
4. Position Y de la pomme
5. Direction courante (0-3)
6. Longueur du serpent (0-1)

**Récompense** :
- +10 : Manger une pomme 🍎
- +0.1 : Chaque step (encourager le mouvement)
- -10 : Collision avec mur ou corps

**Fin du jeu** :
- Collision avec mur ou le corps du serpent
- Ou 500 steps (dépassement du temps limite)

---

### 📊 Résumé Snake vs CartPole

| Aspect | CartPole | Snake |
|--------|----------|-------|
| **Complexité** | Très simple | Moyenne |
| **Environnement** | Gymnasium standard | Personnalisé avec Pygame |
| **Visuel** | Basique (texte) | Beau (Pygame) |
| **Actions** | 2 (gauche/droite) | 4 (4 directions) |
| **Observations** | 4 variables | 6 variables |
| **Score max** | 500 | Illimité |
| **Entraînement** | 50k steps | 100k steps |
| **Temps** | 2-3 min | 3-5 min |

---

### 🚀 Commandes rapides Snake

```powershell
# Entraîner les 3 algos (15 min total)
python scripts/train_ppo_snake.py
python scripts/train_dqn_snake.py
python scripts/train_sac_snake.py

# Voir les agents jouer
python scripts/test_snake.py

# Comparer les résultats
python scripts/benchmark_snake.py
```

---

### 💡 Remarques importantes

1. **Pygame est nécessaire** : Installé avec `pip install pygame` au début ✅

2. **Entraînement plus long** : Snake est plus complexe que CartPole
   - 100k steps vs 50k pour CartPole
   - Mais toujours rapide (~3-5 min par algo)

3. **Résultats prévisibles** :
   - PPO : Bon et stable ✅
   - DQN : Peut être moins stable sur Snake
   - SAC : Adapté à continuo, mais fonctionne aussi ici

4. **Améliorations possibles** :
   - Augmenter la grille (15x15, 20x20)
   - Ajouter des obstacles
   - Changer les récompenses
   - Entraîner plus longtemps

---

✨ **Bon apprentissage avec Snake !** 🐍🍎
