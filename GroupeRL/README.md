# Projet d'Apprentissage par Renforcement : Snake & CartPole

Ce projet explore l'implémentation et la comparaison de plusieurs algorithmes d'apprentissage par renforcement (RL) sur des environnements de complexité variable. Il s'inscrit dans le cadre du cours "IA probabiliste, théorie de jeux et machine learning" (MSMIN5IN43).

L'objectif est de comparer les performances des algorithmes **PPO**, **DQN** et **A2C** sur :
1.  L'environnement classique `CartPole-v1` de Gymnasium.
2.  Un environnement de **Snake** personnalisé, créé avec Pygame pour une visualisation plus riche.

## 1. Architecture du Projet

Le code est organisé de manière modulaire pour séparer les environnements, les modèles entraînés, les scripts et les résultats.

```
.
├── GroupeRL/
│   ├── envs/
│   │   └── snake_env.py        # Définition de l'environnement Snake personnalisé
│   ├── models/
│   │   ├── ..._snake.zip       # Modèles (PPO, DQN, A2C) entraînés sur Snake
│   │   └── ..._cartpole.zip    # Modèles entraînés sur CartPole
│   ├── results/
│   │   ├── comparaison_snake.png # Graphiques de performance pour Snake
│   │   └── comparaison_algos.png # Graphiques de performance pour CartPole
│   ├── scripts/
│   │   ├── train_*.py          # Scripts pour entraîner les modèles
│   │   ├── play_*.py           # Scripts pour visualiser les agents
│   │   └── benchmark_*.py      # Scripts pour évaluer et comparer les agents
│   ├── Consigne.md
│   ├── REALISATION.md          # Guide de développement initial
|   └── requirements.txt            # Dépendances du projet
│
├── venv/                       # Environnement virtuel Python
├── .gitignore
├── LICENSE
└── README.md                   # README principal du cours

```

## 2. Technologies Utilisées

- **Python 3.11+** : Langage de programmation principal.
- **Gymnasium** : La boîte à outils de référence pour créer et interagir avec des environnements d'apprentissage par renforcement.
- **Stable-Baselines3** : Une bibliothèque d'implémentations fiables et de haute qualité des algorithmes RL les plus populaires (PPO, DQN, A2C, SAC, etc.).
- **Pygame** : Utilisé pour créer l'interface graphique et la logique de notre environnement de jeu Snake personnalisé.
- **NumPy** : Pour la manipulation efficace des données numériques (observations, etc.).
- **Matplotlib** : Pour la visualisation des données et la génération des graphiques de comparaison de performance.
- **TensorBoard** : Outil de visualisation pour suivre les métriques d'entraînement en temps réel (non intégré dans les scripts finaux mais utilisé pour le développement).

## 3. Installation et Configuration

Pour exécuter ce projet, suivez ces étapes :

**1. Cloner le dépôt (si ce n'est pas déjà fait)**
```bash
git clone <URL_DU_DEPOT>
cd 2025-MSMIN5IN43-Probas-ML-Min1
```

**2. Créer et activer un environnement virtuel**
```bash
# Créer l'environnement
python -m venv venv

# Activer sur Windows
.\venv\Scripts\activate

# Activer sur macOS/Linux
source venv/bin/activate
```

**3. Installer les dépendances**
Le fichier `requirements.txt` à la racine du projet contient toutes les bibliothèques nécessaires.
```bash
pip install -r requirements.txt
```

## 4. Guide d'Utilisation

Tous les scripts doivent être lancés depuis la **racine du projet**.

### Entraîner les Modèles

Vous pouvez entraîner chaque algorithme sur l'environnement Snake. Les modèles seront sauvegardés dans le dossier `GroupeRL/models/`.

```bash
# Entraîner PPO sur Snake (environ 3-5 minutes)
python GroupeRL/scripts/train_ppo_snake.py

# Entraîner DQN sur Snake (environ 3-5 minutes)
python GroupeRL/scripts/train_dqn_snake.py

# Entraîner A2C sur Snake (environ 3-5 minutes)
# Note: Le script train_sac_snake.py peut être adapté pour A2C si besoin.
python GroupeRL/scripts/train_a2c_snake.py
```

### Visualiser un Agent

Regardez un agent entraîné jouer au jeu de votre choix. Le mode `human` de Gymnasium ouvrira une fenêtre Pygame.

```bash
# Voir les différents agents jouer à Snake
python GroupeRL/scripts/play_snake.py

# Voir les agents jouer à CartPole
python GroupeRL/scripts/play_cartpole.py
```

### Lancer le Benchmark

Exécutez les scripts de benchmark pour évaluer et comparer les performances des différents algorithmes sur 20 épisodes. Un graphique des résultats sera généré et sauvegardé dans `GroupeRL/results/`.

```bash
# Lancer la comparaison sur l'environnement Snake
python GroupeRL/scripts/benchmark_snake.py

# Lancer la comparaison sur l'environnement CartPole
python GroupeRL/scripts/benchmark_algos.py
```

## 5. Description des Environnements

### `Snake-v0` (Personnalisé)

Un environnement personnalisé où l'agent contrôle un serpent qui doit manger des pommes pour grandir.

- **Objectif** : Manger un maximum de pommes sans heurter les murs ou son propre corps.
- **Espace d'Actions (Discret)** : 4 actions possibles (Haut, Bas, Gauche, Droite).
- **Espace d'Observations** : Un vecteur de 6 valeurs normalisées représentant la position de la tête du serpent, la position de la pomme, la direction actuelle et la longueur du serpent.
- **Système de Récompense** :
    - `+10` pour chaque pomme mangée.
    - `-10` pour une collision (fin de l'épisode).
    - Une petite récompense positive à chaque pas pour encourager l'exploration.
- **Fin d'épisode** : L'épisode se termine si le serpent entre en collision avec un mur ou lui-même, ou après 500 pas.

### `CartPole-v1` (Gymnasium)

Un environnement classique utilisé comme "Hello World" de l'apprentissage par renforcement.

- **Objectif** : Équilibrer un poteau sur un chariot qui se déplace le long d'un rail.
- **Espace d'Actions (Discret)** : 2 actions (pousser le chariot à gauche ou à droite).
- **Espace d'Observations** : Un vecteur de 4 valeurs (position et vélocité du chariot, angle et vélocité du poteau).
- **Système de Récompense** : `+1` pour chaque pas où le poteau reste en équilibre.
- **Fin d'épisode** : L'épisode se termine si le poteau s'incline de plus de 12 degrés ou si le chariot sort de l'écran. L'objectif est d'atteindre 500 pas.

## 6. Auteurs

LO NEGRO Dorian,
MAUGEAIS Thomas,
THEPAUT Julien.
