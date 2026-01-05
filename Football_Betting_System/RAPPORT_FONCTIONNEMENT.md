# Rapport de Fonctionnement Technique - Projet Football AI

## 1. Architecture Globale
Le projet repose sur une architecture moderne en **microservices conteneurisés** (Docker), composée de trois blocs principaux :
- **Frontend** : Interface utilisateur réactive (React + Vite).
- **Backend** : API performante et moteur d'IA (Python FastAPI).
- **Base de Données** : Persistance relationnelle (PostgreSQL) et cache (Redis).

## 2. Le Moteur d'IA (Backend)
Le cœur du système est le `BayesianFootballModel`, un modèle statistique hybride pour la prédiction des résultats de matchs.

### Fonctionnalités Clés :
*   **Modélisation Bayésienne :** Utilise des "priors" (croyances initiales) basés sur 15 matchs fictifs moyens pour éviter les fluctuations extrêmes dues à une faible taille d'échantillon.
*   **Statistiques Avancées :** Intègre les performances des joueurs, la forme récente des équipes, et l'historique des confrontations directes (H2H).
*   **Ajustement Dynamique (Dixon-Coles) :** Applique un facteur d'amortissement (`K-Factor`) pour lisser les probabilités et éviter les cotes irréalistes (ex: 17.00 pour Chelsea).
*   **TrueSkill Integration :** Utilise l'algorithme TrueSkill (similaire au ranking Xbox Live) pour évaluer la force intrinsèque des équipes.

### API Routes :
*   `/api/predict-match` : Calcule les probabilités de victoire (Team 1, Draw, Team 2) en utilisant une simulation de Monte Carlo (10,000 itérations).
*   `/api/events` : Récupère les matchs en direct et à venir avec leurs cotes calculées.

## 3. L'Interface Utilisateur (Frontend)
L'application est construite avec **React**, utilisant une architecture modulaire basée sur des composants UI personnalisés (`CustomComponents.jsx`).

### Points Techniques :
*   **Design System :** Utilisation de CSS natif (`CustomComponents.css` et `modern.css`) sans framework lourd (pas de Bootstrap/Tailwind complet), garantissant des performances maximales.
*   **Système de Layout :** Composants `Grid`, `Stack`, et `Group` gérant l'espacement via des propriétés `gap` dynamiques pour une mise en page fluide.
*   **Glassmorphism :** Style visuel moderne "Dark Mode" utilisant des effets de transparence (`backdrop-filter: blur`) pour une esthétique premium.

## 4. Flux de Données
1.  L'utilisateur ouvre le tableau de bord (`BettingDashboard`).
2.  Le Frontend appelle l'API Backend (`/api/events`).
3.  Le Backend interroge la base de données ou calcule les probabilités via le modèle Bayésien en temps réel.
4.  Les résultats (cotes, prédictions) sont renvoyés au Frontend et affichés sous forme de cartes interactives.
5.  Les paris sont stockés dans PostgreSQL via une transaction sécurisée.

## 5. État Actuel
Le système est **pleinement opérationnel**. Les problèmes d'affichage (espacement des composants) ont été résolus par l'implémentation de règles CSS strictes (`gap`), et le modèle mathématique a été stabilisé pour produire des cotes cohérentes avec le marché réel.
