# Check-it! - Détecteur de Désinformation par RoBERTa

Ce projet implémente un système automatisé de détection de désinformation (fake news) utilisant un modèle **RoBERTa fine-tuné** sur des données multilingues. Le verdict de vérité est déterminé uniquement par le modèle ML (pas par agrégation de sources). Les sources web sont récupérées pour **transparence** et **analyse de manipulation** uniquement si l'affirmation est détectée comme fausse.

## Groupe 31

### Marilson SOUZA
### Brenda KOUNDJO
### Xiner GU

## Prérequis

- Python 3.8 ou supérieur
- Clés API OpenAI (requise)
- Clé API SerpAPI (optionnelle, pour recherche Google)

## Installation

1. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Sur Windows
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

### Fine-tuner RoBERTa sur vos données

Une fois le CSV prêt (`text`,`label` avec labels FAKE/REAL), lancez l'entraînement local :

```bash
python train_roberta_fakenews.py --data_path fake_news_dataset_multilang.csv \
  --model_name roberta-base \
  --output_dir models/roberta-fake-news \
  --max_length 256 \
  --batch_size 16 \
  --epochs 5 \
  --seed 42
```

- Le DataLoader est reshuffle à chaque epoch pour éviter les clusters par langue.
- Un split stratifié validation est appliqué (`test_size=0.15`).
- La meilleure checkpoint (selon `f1` sur FAKE) est sauvegardée dans `--output_dir`.

Pour utiliser le modèle fine-tuné dans l'app :

```bash
set FAKE_NEWS_MODEL_PATH=models/roberta-fake-news  # Windows
export FAKE_NEWS_MODEL_PATH=models/roberta-fake-news # macOS/Linux
```

Vous pouvez ajuster les seuils via `FAKE_NEWS_FAKE_THRESHOLD` et `FAKE_NEWS_REAL_THRESHOLD` (par défaut 0.6) ainsi que `FAKE_NEWS_MAX_LENGTH`.

3. Configurer les clés API :
   Éditer `.env` avec vos clés API :
   - `OPENAI_API_KEY` (requis)
   - `SERPAPI_API_KEY` (optionnel, utilise DuckDuckGo sinon)
   - `OPENAI_MODEL` (optionnel, défaut: `gpt-4o-mini`)

## Utilisation

### Interface web
1. Lancer l'application Flask :
   ```bash
   flask --app app run --debug
   ```
2. Ouvrir http://127.0.0.1:5000 dans votre navigateur
3. Coller une affirmation ou un texte contenant plusieurs affirmations
4. Cliquer sur "Vérifier" pour lancer l'analyse
 
### Fonctionnalités

#### Pipeline de vérification
1. **Verdict par RoBERTa fine-tuné** : Modèle RoBERTa entraîné sur données multilingues (FAKE/REAL) avec shuffle per epoch et stratification. Verdict unique et déterministe, seuils configurables (défaut 0.6). **Pas d'agrégation de sources** — le modèle décide seul.

2. **Sources pour transparence** : Recherche web (SerpAPI ou DuckDuckGo) avec récupération du contenu des pages (jusqu'à 6 sources). Filtrage des domaines bloqués (Reddit, Medium, Quora, etc.). Sources triées par crédibilité, affichées uniquement au clic "🔍 Localiser les sources".

3. **Sources filtrées par verdict** :
  - Si RoBERTa dit **FAKE** → affiche uniquement sources qui *contredisent*
  - Si RoBERTa dit **REAL** → affiche uniquement sources qui *supportent*

4. **Analyse de manipulation** (si FAKE détecté) : Identification de la narrative, audience cible, vecteurs de propagation, ressorts psychologiques, conseils pratiques via "En savoir plus" → modal.

5. **Évaluation de crédibilité des sources** (pour transparence uniquement) :
  - Scoring par LLM avec mise en cache persistante
  - Priors manuels (Reuters, AFP, fact-checkers, .gov, .edu)
  - Plafonnement pour réseaux sociaux (max 30%)

#### Interface utilisateur
- **Barre de progression animée** pendant l'analyse
- **RoBERTa block** : Verdict (FAKE/REAL/INCONCLUSIVE) avec probabilités fake/real et confiance
- **Bouton "🔍 Localiser les sources"** : Affiche sources *pertinentes* au verdict (contrediction si FAKE, support si REAL)
- **Résultats colorés** selon le verdict :
  - Vert = affirmation supportée
  - Rouge = affirmation contredite
  - Jaune = inconclusif
- **Animation progressive** : affirmations et sources apparaissent une par une
- **Bouton "En savoir plus"** sur affirmations fausses → modal d'analyse de désinformation (narrative, audience, vecteurs, protection)
- **Détection de propos haineux** (filtrage automatique)

### Remarques d'exploitation

- OpenAI API requis pour **analyse de manipulation** uniquement (si FAKE détecté)
- RoBERTa fine-tuné exécuté localement (transformers) : téléchargement du modèle entraîné (~500 MB) ou utilisation du checkpoint fourni
- Entraînement du modèle : `train_roberta_fakenews.py` avec stratification, shuffle per epoch, validation split 15%
- Cache de crédibilité sauvegardé dans `cred_cache.json` pour éviter appels API redondants
- SerpAPI recommandé pour meilleurs résultats de recherche (limite gratuite: 100 recherches/mois)
- BeautifulSoup utilisé pour extraction de contenu web propre (évite snippets tronqués)

## Structure du projet

- `app.py` : Application Flask principale (RoBERTa detection, evidence retrieval, manipulation analysis)
- `train_roberta_fakenews.py` : Script de fine-tuning RoBERTa sur données CSV (labels FAKE/REAL)
- `templates/index.html` : Interface web avec animations, modal, filtrage sources par verdict
- `requirements.txt` : Dépendances Python (transformers, torch, pandas, scikit-learn, accelerate, etc.)
- `models/roberta-fake-news/` : Checkpoint du modèle fine-tuné (généré après entraînement)
- `.env.example` : Template de configuration (clés API, chemin modèle, seuils)
- `fake_news_dataset_multilang.csv` : Données d'entraînement multilingues (text, label)
- `cred_cache.json` : Cache de crédibilité des domaines (généré automatiquement)

## Configuration avancée

### Constantes clés dans `app.py`
- `TRUSTED_DOMAIN_PRIORS` : Liste des domaines de confiance avec scores manuels
- `DEFAULT_NEUTRAL_PRIOR = 0.45` : Score par défaut pour domaines inconnus
- `MIN_CREDIBILITY_INCLUDE = 0.6` : Seuil pour inclusion dans verdict
- `MIN_RELEVANCE = 0.35` : Seuil de pertinence
- `MAX_RESULTS = 6` : Nombre max de sources par affirmation
- `BLOCKED_DOMAINS` : Liste noire (Reddit, Medium, etc.)
- `UGC_DOMAINS` : Réseaux sociaux (plafonnés à 30%)
- `MAX_CRED_FOR_UGC = 0.3` : Plafond pour contenu généré par utilisateurs

## Endpoints API

### `POST /api/verify`
Analyse une ou plusieurs affirmations.

**Corps de requête :**
```json
{ "text": "Le vaccin COVID réduit les hospitalisations de 60%" }
```

**Réponse :**
```json
{
  "claims": [
    {
      "claim": "Le vaccin COVID réduit les hospitalisations de 60%",
      "verdict": "support",
      "stance_scores": {
        "support": 0.85,
        "contradict": 0.10,
        "inconclusive": 0.05
      },
      "evidence": [
        {
          "source": "who.int",
          "url": "https://...",
          "snippet": "...",
          "stance": "support",
          "credibility": 0.9,
          "confidence": 0.85,
          "relevance": 0.92,
          "used_in_score": true
        }
      ],
      "updated_at": "2026-01-03T19:45:00Z",
      "manipulation_analysis": null
    }
  ]
}
```

### `GET /`
Interface web simple avec textarea et bouton de vérification.
