"""
Environnement Snake personnalisé avec Pygame
Compatible avec Gymnasium et Stable-Baselines3
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from enum import Enum
from collections import deque

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class SnakeEnv(gym.Env):
    """
    Environnement Snake avec visuel Pygame
    
    Actions : 0=Haut, 1=Droite, 2=Bas, 3=Gauche
    Observation : Position de la tête, position de la pomme, direction
    """
    
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 10}
    
    def __init__(self, grid_size=10, render_mode=None):
        """
        grid_size : Taille de la grille (10x10, 15x15, etc.)
        render_mode : 'human' pour afficher, None pour pas d'affichage
        """
        super().__init__()
        
        self.grid_size = grid_size
        self.render_mode = render_mode
        
        # Espaces d'action et d'observation
        self.action_space = spaces.Discrete(4)  # 4 directions
        
        # Observation : [head_x, head_y, food_x, food_y, direction, body_length]
        self.observation_space = spaces.Box(
            low=0, high=grid_size,
            shape=(6,), dtype=np.float32
        )
        
        # Pygame
        self.screen = None
        self.clock = None
        self.cell_size = 30
        
        # Réinitialiser l'environnement
        self.reset()
    
    def reset(self, seed=None):
        """Réinitialise le jeu"""
        super().reset(seed=seed)
        
        # Initialiser le serpent au centre
        center = self.grid_size // 2
        self.snake = deque([(center, center)])
        
        # Direction initiale
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Générer une pomme aléatoire
        self._spawn_food()
        
        # Compteurs
        self.steps = 0
        self.max_steps = 500
        self.food_eaten = 0
        
        return self._get_observation(), {}
    
    def _spawn_food(self):
        """Génère une pomme aléatoire"""
        while True:
            self.food = (
                self.np_random.integers(0, self.grid_size),
                self.np_random.integers(0, self.grid_size)
            )
            if self.food not in self.snake:
                break
    
    def step(self, action):
        """Effectue une action"""
        self.steps += 1
        
        # Mettre à jour la direction
        # Empêcher le serpent de faire demi-tour
        if action == 0 and self.direction != Direction.DOWN:  # UP
            self.direction = Direction.UP
        elif action == 1 and self.direction != Direction.LEFT:  # RIGHT
            self.direction = Direction.RIGHT
        elif action == 2 and self.direction != Direction.UP:  # DOWN
            self.direction = Direction.DOWN
        elif action == 3 and self.direction != Direction.RIGHT:  # LEFT
            self.direction = Direction.LEFT
        
        # Bouger le serpent
        head_x, head_y = self.snake[0]
        
        if self.direction == Direction.UP:
            head_y -= 1
        elif self.direction == Direction.RIGHT:
            head_x += 1
        elif self.direction == Direction.DOWN:
            head_y += 1
        elif self.direction == Direction.LEFT:
            head_x -= 1
        
        new_head = (head_x, head_y)
        
        # Vérifier les collisions
        reward = 0
        terminated = False
        
        # Collision avec les murs
        if (head_x < 0 or head_x >= self.grid_size or
            head_y < 0 or head_y >= self.grid_size):
            terminated = True
            reward = -10
        
        # Collision avec le corps
        elif new_head in self.snake:
            terminated = True
            reward = -10
        
        # Manger une pomme
        elif new_head == self.food:
            self.snake.appendleft(new_head)
            self.food_eaten += 1
            reward = 10
            self._spawn_food()
        
        # Mouvement normal
        else:
            self.snake.appendleft(new_head)
            self.snake.pop()
            reward = 0.1  # Petite récompense pour chaque step
        
        # Limiter le nombre de steps
        truncated = self.steps >= self.max_steps
        
        obs = self._get_observation()
        info = {'food_eaten': self.food_eaten}
        
        return obs, reward, terminated, truncated, info
    
    def _get_observation(self):
        """Retourne l'observation normalisée"""
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        obs = np.array([
            head_x / self.grid_size,
            head_y / self.grid_size,
            food_x / self.grid_size,
            food_y / self.grid_size,
            self.direction.value / 3,
            min(len(self.snake) / 10, 1.0)
        ], dtype=np.float32)
        
        return obs
    
    def render(self):
        """Affiche le jeu avec Pygame"""
        if self.render_mode != 'human':
            return
        
        # Initialiser Pygame au premier rendu
        if self.screen is None:
            pygame.init()
            width = height = self.grid_size * self.cell_size
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Snake RL 🐍")
            self.clock = pygame.time.Clock()
        
        # Fond noir
        self.screen.fill((0, 0, 0))
        
        # Dessiner la grille (optionnel)
        for i in range(self.grid_size + 1):
            pygame.draw.line(
                self.screen, (40, 40, 40),
                (i * self.cell_size, 0),
                (i * self.cell_size, self.grid_size * self.cell_size)
            )
            pygame.draw.line(
                self.screen, (40, 40, 40),
                (0, i * self.cell_size),
                (self.grid_size * self.cell_size, i * self.cell_size)
            )
        
        # Dessiner la pomme
        food_x, food_y = self.food
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),  # Rouge
            pygame.Rect(
                food_x * self.cell_size + 2,
                food_y * self.cell_size + 2,
                self.cell_size - 4,
                self.cell_size - 4
            )
        )
        
        # Dessiner le serpent
        for i, (x, y) in enumerate(self.snake):
            # Tête en vert clair
            color = (0, 255, 0) if i == 0 else (0, 200, 0)
            
            pygame.draw.rect(
                self.screen,
                color,
                pygame.Rect(
                    x * self.cell_size + 1,
                    y * self.cell_size + 1,
                    self.cell_size - 2,
                    self.cell_size - 2
                )
            )
        
        # Afficher les infos
        font = pygame.font.Font(None, 24)
        
        score_text = font.render(f'Score: {self.food_eaten}', True, (255, 255, 255))
        length_text = font.render(f'Length: {len(self.snake)}', True, (255, 255, 255))
        steps_text = font.render(f'Steps: {self.steps}', True, (255, 255, 255))
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(length_text, (10, 35))
        self.screen.blit(steps_text, (10, 60))
        
        pygame.display.flip()
        self.clock.tick(self.metadata['render_fps'])
    
    def close(self):
        """Ferme Pygame"""
        if self.screen is not None:
            pygame.quit()
            self.screen = None
            self.clock = None

# Enregistrer l'environnement
gym.register(
    id='Snake-v0',
    entry_point='envs.snake_env:SnakeEnv',
    max_episode_steps=500,
    kwargs={'grid_size': 10}
)

gym.register(
    id='Snake-v1',
    entry_point='envs.snake_env:SnakeEnv',
    max_episode_steps=1000,
    kwargs={'grid_size': 15}
)
