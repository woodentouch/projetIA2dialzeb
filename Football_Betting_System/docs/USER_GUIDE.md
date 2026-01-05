# 🎮 Guide d'Utilisation - Football Betting Platform

## 📋 Table des Matières
1. [Installation](#installation)
2. [Première Utilisation](#première-utilisation)
3. [Guide des Onglets](#guide-des-onglets)
4. [Placer un Pari](#placer-un-pari)
5. [Consulter l'Historique](#consulter-lhistorique)
6. [Affichage des Joueurs](#affichage-des-joueurs)
7. [FAQ](#faq)

---

## 🚀 Installation

### Option 1: Docker Compose (Recommandé)

```bash
cd c:\Users\alifa\Desktop\projetIA2dialzeb

# 1. Démarrer tous les services
docker-compose up -d

# 2. Attendre ~30 secondes pour que tout soit prêt
docker-compose logs backend

# 3. Initialiser les données
curl -X POST http://localhost:8000/api/seed-data

# 4. Accéder à l'application
# Frontend: http://localhost:5173
```

### Option 2: Installation Locale

```bash
# Frontend
cd frontend
npm install
npm run dev
# Accès: http://localhost:5173

# Backend (dans un autre terminal)
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
# Accès: http://localhost:8000
```

---

## 💡 Première Utilisation

### 1. Accéder à l'Application
Ouvrir un navigateur et aller à: **http://localhost:5173**

### 2. Voir l'Interface Principale
Vous verrez 3 onglets:
- 🎯 **Événements** - Liste des matchs
- 💰 **Parier** - Interface de paris
- 📊 **Mes Paris** - Historique

### 3. Charger les Données de Test
Les données sont créées automatiquement quand on appelle `/api/seed-data`

---

## 📑 Guide des Onglets

### Onglet 1️⃣: ÉVÉNEMENTS

#### Affichage
- **Nom du match**: "PSG vs Lyon", "Manchester United vs Liverpool", etc.
- **Date et Heure**: En format français
- **Statut**: Badge vert = "Actif", Gris = "Inactif"
- **Cotes**: 
  - Cote 1 = Victoire de la première équipe
  - Cote Draw = Match nul
  - Cote 2 = Victoire de la deuxième équipe

#### Exemple
```
PSG vs Lyon
📅 samedi 6 janvier 2024
🕐 19:00

Cote 1: 1.45 | Cote Draw: 3.8 | Cote 2: 2.7
[Voir les Joueurs] bouton
```

#### Actions
- Voir les détails de chaque match
- Cliquer sur "Voir les Joueurs" pour plus d'infos

---

### Onglet 2️⃣: PARIER

Cet onglet a 2 sections:

#### Section Gauche: Sélection d'Événement
- Liste de tous les événements
- Cliquer pour sélectionner un match
- L'événement sélectionné est mis en évidence en bleu

#### Section Droite: Détails et Cotes
Après sélection d'un événement:

**Tab "Cotes"**
- 3 cartes avec les cotes
- Chaque cote a un bouton "Parier"
- Clique sur "Parier" pour ouvrir le formulaire

**Tab "Joueurs"**
- Affiche tous les joueurs du match
- Photo du joueur
- Numéro du maillot + Position
- 6 critères de jeu (voir section suivante)
- Bouton "Parier sur ce joueur"

**Tab "Statistiques"**
- À venir (section en développement)

---

## 💸 Placer un Pari

### Étape 1: Sélectionner l'Événement
1. Aller à l'onglet "Parier"
2. Cliquer sur un événement dans la liste de gauche
3. L'événement est maintenant sélectionné

### Étape 2: Choisir le Type de Pari
1. Aller à l'onglet "Cotes"
2. Voir les 3 options:
   - Victoire Équipe 1 (ex: PSG)
   - Match Nul
   - Victoire Équipe 2 (ex: Lyon)
3. Cliquer sur "Parier" pour l'option désirée

### Étape 3: Remplir le Formulaire
Une fenêtre (modal) s'ouvre:

```
Placer un pari - [Type Sélectionné]

Cote: 1.45

Montant du pari (€): [_______________]

[Annuler] [Confirmer le pari]
```

1. Entrer le montant en euros
2. Le gain potentiel s'affiche automatiquement
3. Cliquer "Confirmer le pari"

### Exemple Concret
```
Je parie 10€ sur la victoire du PSG à cote 1.45
Gain potentiel = 10 × 1.45 = 14.50€
Si le PSG gagne → Je gagne 14.50€
Si PSG ne gagne pas → Je perde 10€
```

---

## 📊 Affichage des Joueurs

### Information Affichée par Joueur

```
[PHOTO]           ← Photo du joueur

Nom du Joueur
#7 • FW (Position)

Attaque:    [████████████░░░░░░░░░░░░] 94/100
Défense:    [█████░░░░░░░░░░░░░░░░░░░░] 38/100
Vitesse:    [███████████████░░░░░░░░░░░] 96/100
Force:      [███████████░░░░░░░░░░░░░░░] 76/100
Dextérité:  [██████████████░░░░░░░░░░░░] 87/100
Endurance:  [███████████████░░░░░░░░░░░] 89/100

[Parier sur ce joueur]
```

### Légende des Critères (Style FIFA)

| Critère | Signification | Exemple |
|---------|---------------|---------|
| 🎯 Attaque | Capacité à marquer | Delanteros (FW) = haut |
| 🛡️ Défense | Capacité à défendre | Défenseurs (DF) = haut |
| ⚡ Vitesse | Rapidité de déplacement | Ailiers = haut |
| 💪 Force | Puissance physique | Attaquants = haut |
| 🎨 Dextérité | Contrôle du ballon | Milieux = haut |
| 🏃 Endurance | Résistance à la fatigue | Gardiens = bas |

### Codes Couleur des Barres
- 🟢 **Vert**: Excellent (> 70)
- 🟡 **Orange**: Bon (50-70)
- 🔴 **Rouge**: Modéré (< 50)

---

## 📈 Consulter l'Historique

### Onglet 3️⃣: MES PARIS

#### Statistiques en Haut
4 cartes affichent:
1. **Total Misé**: Somme de tous vos paris
2. **Gains Potentiels**: Montant que vous pouvez gagner
3. **Nombre de Paris**: Combien de paris vous avez placés
4. **Taux de Réussite**: Pourcentage de paris gagnés

#### Tableau de l'Historique
```
| Événement | Type | Montant | Cote | Gain | Statut | Date | Actions |
|-----------|------|---------|------|------|--------|------|---------|
| PSG vs Lyon | team1 | 10€ | 1.45 | 14.50€ | En attente | 06/01/2024 | Détails |
| ...       | ...  | ...   | ... | ...  | ...    | ...  | ... |
```

#### Statuts Possibles
- 🟡 **En attente**: Le match n'a pas eu lieu
- 🟢 **Gagné**: Votre pari était correct
- 🔴 **Perdu**: Votre pari était incorrect
- ⚪ **Annulé**: Le pari a été annulé

#### Voir les Détails
1. Cliquer sur "Détails" dans la ligne du pari
2. Une fenêtre (modal) s'ouvre avec:
   - Événement complet
   - Type de pari placé
   - Montant initial
   - Cote
   - Gain potentiel
   - Statut du pari
   - Date et heure

---

## 🎯 Exemples Concrets

### Exemple 1: Parier sur un Match
```
1. Aller à "Parier"
2. Sélectionner "PSG vs Lyon"
3. Aller à l'onglet "Cotes"
4. Cliquer "Parier" sur "Victoire PSG" (cote 1.45)
5. Entrer montant: 20€
6. Gain potentiel = 20 × 1.45 = 29€
7. Cliquer "Confirmer"
```

### Exemple 2: Consulter Historique
```
1. Aller à "Mes Paris"
2. Voir le tableau avec tous les paris
3. Total misé = 50€
4. Gains potentiels = 95€
5. Taux de réussite = 60%
6. Cliquer "Détails" pour voir un pari spécifique
```

### Exemple 3: Voir les Joueurs
```
1. Aller à "Parier"
2. Sélectionner un événement
3. Aller à l'onglet "Joueurs"
4. Voir la grille avec tous les joueurs
5. Chaque joueur affiche sa photo et ses stats
```

---

## ❓ FAQ

### Q: Comment augmenter mon montant?
A: Il n'y a pas de montant maximum, vous pouvez parier autant que vous voulez.

### Q: Peut-on parier après le début du match?
A: Non, seuls les événements "actifs" permettent les paris.

### Q: Comment sont calculés les gains?
A: Gain = Montant × Cote
Exemple: 10€ × 1.5 = 15€ (dont 10€ remboursé + 5€ de profit)

### Q: Les cotes changent-elles?
A: Les cotes affichées sont fixes au moment du pari. Vous verrez la cote au moment où vous avez parié.

### Q: Peut-on annuler un pari?
A: Non, une fois placé, le pari ne peut pas être annulé.

### Q: Que signifient les codes FIFA?
A: Ce sont des critères de performance football:
- FW = Forward (Attaquant)
- MF = Midfielder (Milieu)
- DF = Defender (Défenseur)
- GK = Goalkeeper (Gardien)

### Q: Pourquoi certains joueurs ont des stats basses?
A: C'est réaliste! Les gardiens ont une vitesse/attaque basse car ce ne sont pas leurs fonctions.

### Q: Peut-on parier sur un joueur?
A: Oui, il y a un bouton "Parier sur ce joueur" mais c'est pour développement futur.

### Q: Où voir la documentation API?
A: http://localhost:8000/docs (interface Swagger)

### Q: Comment récupérer les données de test?
A: Appeler: `curl -X POST http://localhost:8000/api/seed-data`

---

## 🆘 Problèmes Courants

### L'application ne charge pas
```
Vérifications:
- Docker est-il lancé? docker-compose ps
- Le backend s'exécute-t-il? curl http://localhost:8000/health
- Le frontend s'exécute-t-il? Vérifier le terminal
```

### Les événements ne s'affichent pas
```
Étapes:
1. Appeler: curl -X POST http://localhost:8000/api/seed-data
2. Rafraîchir la page (F5)
3. Vérifier que le statut est "active"
```

### Erreur CORS
```
Cause: Le frontend et backend ne communiquent pas
Solution:
- Vérifier que backend s'exécute sur port 8000
- Vérifier que frontend s'exécute sur port 5173
- Consulter QUICK_START.md
```

### Base de données vide
```
Réinitialisation:
1. docker-compose down -v
2. docker-compose up -d
3. curl -X POST http://localhost:8000/api/seed-data
```

---

## 📞 Support

Pour plus d'aide:
1. Consulter [QUICK_START.md](./QUICK_START.md)
2. Consulter [FOOTBALL_BETTING_README.md](./FOOTBALL_BETTING_README.md)
3. Vérifier la documentation API: http://localhost:8000/docs

---

**Bon Paris! ⚽💰**
