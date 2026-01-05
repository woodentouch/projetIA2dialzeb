"""
Advanced Bayesian Football Prediction Model
Uses sophisticated statistical modeling with player stats, team form, and historical data
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json


class BayesianFootballModel:
    """
    Advanced football prediction model using Bayesian inference
    Features:
    - Player statistics integration
    - Team form analysis (recent performance)
    - Head-to-head historical data
    - Home advantage modeling
    - Uncertainty quantification
    - Confidence intervals
    """

    def __init__(self):
        self.team_stats = {}
        self.player_impact = {}
        self.h2h_history = defaultdict(lambda: defaultdict(list))
        self.recent_form = defaultdict(list)
        self.trueskill_ratings = {}  # Store TrueSkill mu values
        self.is_fitted = False
        self.global_avg_goals = 2.5  # Average goals per game
        self.team_leagues = {} # Store league for each team
        self.league_averages = {} # Store average home/away goals per league

    def set_trueskill_ratings(self, ratings: Dict[str, float]):
        """Update model with external TrueSkill ratings (mu values)"""
        self.trueskill_ratings = ratings

    def fit(self, matches: List[Dict], player_data: Optional[List[Dict]] = None, draws: int = 500, tune: int = 500):
        """
        Train model on historical matches with advanced feature extraction
        
        Args:
            matches: List of {'team1': str, 'team2': str, 'home_score': int, 'away_score': int, 
                            'date': str (optional), 'match_id': int (optional)}
            player_data: Optional list of player statistics to enhance predictions
            draws: Number of samples (for future MCMC integration)
            tune: Tuning steps (for future MCMC integration)
        """
        self.team_stats = {}
        self.h2h_history = defaultdict(lambda: defaultdict(list))
        self.recent_form = defaultdict(list)
        self.team_leagues = {}
        
        # Calculate league-specific averages first
        league_stats = defaultdict(lambda: {'home_goals': 0, 'away_goals': 0, 'matches': 0})
        
        for match in matches:
            league = match.get('league', 'default')
            league_stats[league]['home_goals'] += match.get('home_score', 0)
            league_stats[league]['away_goals'] += match.get('away_score', 0)
            league_stats[league]['matches'] += 1
            
            # Map teams to leagues
            if match.get('team1'): self.team_leagues[match['team1']] = league
            if match.get('team2'): self.team_leagues[match['team2']] = league
            
        self.league_averages = {}
        for league, stats in league_stats.items():
            if stats['matches'] > 0:
                self.league_averages[league] = {
                    'home': stats['home_goals'] / stats['matches'],
                    'away': stats['away_goals'] / stats['matches']
                }
        
        # Fallback defaults (approximate global averages)
        self.league_averages['default'] = {'home': 1.5, 'away': 1.1}

        # Sort matches by date if available
        sorted_matches = sorted(matches, key=lambda m: m.get('date', ''), reverse=False)
        
        total_goals = 0
        total_matches = 0
        
        for match in sorted_matches:
            team1 = match.get('team1')
            team2 = match.get('team2')
            
            if not team1 or not team2:
                continue
                
            # Initialize team stats with Bayesian Priors
            # We assume every team starts with 15 "average" matches (Very Strong Prior)
            # This anchors teams to the mean and prevents wild swings from short form streaks
            PRIOR_MATCHES = 15
            PRIOR_GOALS = 1.35 * PRIOR_MATCHES  # Average goals per match ~1.35
            
            for team in [team1, team2]:
                if team not in self.team_stats:
                    self.team_stats[team] = {
                        'matches': 0,
                        'wins': 0,
                        'draws': 0,
                        'losses': 0,
                        'goals_for': 0,
                        'goals_against': 0,
                        'home_matches': 0,
                        'away_matches': 0,
                        'home_goals_for': 0,
                        'home_goals_against': 0,
                        'away_goals_for': 0,
                        'away_goals_against': 0,
                        'attack_strength': 1.0,
                        'defense_strength': 1.0,
                        'home_attack': 1.0,
                        'away_attack': 1.0,
                        'form_score': 0.5,  # 0-1 scale
                        'recent_results': []
                    }
            
            home_score = match.get('home_score', 0)
            away_score = match.get('away_score', 0)
            match_date = match.get('date', datetime.now().isoformat())
            
            # Update overall stats
            self.team_stats[team1]['matches'] += 1
            self.team_stats[team1]['home_matches'] += 1
            self.team_stats[team1]['goals_for'] += home_score
            self.team_stats[team1]['goals_against'] += away_score
            self.team_stats[team1]['home_goals_for'] += home_score
            self.team_stats[team1]['home_goals_against'] += away_score
            
            self.team_stats[team2]['matches'] += 1
            self.team_stats[team2]['away_matches'] += 1
            self.team_stats[team2]['goals_for'] += away_score
            self.team_stats[team2]['goals_against'] += home_score
            self.team_stats[team2]['away_goals_for'] += away_score
            self.team_stats[team2]['away_goals_against'] += home_score
            
            # Update win/draw/loss records
            if home_score > away_score:
                self.team_stats[team1]['wins'] += 1
                self.team_stats[team2]['losses'] += 1
                result1, result2 = 'W', 'L'
            elif home_score < away_score:
                self.team_stats[team1]['losses'] += 1
                self.team_stats[team2]['wins'] += 1
                result1, result2 = 'L', 'W'
            else:
                self.team_stats[team1]['draws'] += 1
                self.team_stats[team2]['draws'] += 1
                result1, result2 = 'D', 'D'
            
            # Track recent form (last 5 matches)
            self.team_stats[team1]['recent_results'].append({
                'result': result1,
                'goals_for': home_score,
                'goals_against': away_score,
                'date': match_date
            })
            self.team_stats[team2]['recent_results'].append({
                'result': result2,
                'goals_for': away_score,
                'goals_against': home_score,
                'date': match_date
            })
            
            # Keep only last 5 matches for form
            self.team_stats[team1]['recent_results'] = self.team_stats[team1]['recent_results'][-5:]
            self.team_stats[team2]['recent_results'] = self.team_stats[team2]['recent_results'][-5:]
            
            # Store head-to-head history
            self.h2h_history[team1][team2].append({
                'home_score': home_score,
                'away_score': away_score,
                'date': match_date,
                'location': 'home'
            })
            self.h2h_history[team2][team1].append({
                'home_score': away_score,
                'away_score': home_score,
                'date': match_date,
                'location': 'away'
            })
            
            total_goals += home_score + away_score
            total_matches += 1
        
        # Calculate global average
        if total_matches > 0:
            self.global_avg_goals = total_goals / (2 * total_matches)
        
        # Calculate advanced team statistics
        PRIOR_MATCHES = 15
        
        for team, stats in self.team_stats.items():
            if stats['matches'] > 0:
                # Get league-specific priors
                league = self.team_leagues.get(team, 'default')
                avgs = self.league_averages.get(league, self.league_averages['default'])
                
                # Overall attack/defense priors (using league average goals per match)
                league_avg_goals = (avgs['home'] + avgs['away']) / 2
                PRIOR_GOALS = league_avg_goals * PRIOR_MATCHES
                
                # Overall attack and defense strength (Smoothed with Bayesian Priors)
                avg_goals_for = (stats['goals_for'] + PRIOR_GOALS) / (stats['matches'] + PRIOR_MATCHES)
                avg_goals_against = (stats['goals_against'] + PRIOR_GOALS) / (stats['matches'] + PRIOR_MATCHES)
                
                # Dampening factor to prevent extreme ratios (Softens the impact of outliers)
                K_FACTOR = 0.5
                stats['attack_strength'] = (avg_goals_for + K_FACTOR) / (max(self.global_avg_goals, 0.1) + K_FACTOR)
                stats['defense_strength'] = (max(self.global_avg_goals, 0.1) + K_FACTOR) / (avg_goals_against + K_FACTOR)
                
                # Home/away specific strengths (Smoothed)
                # We use a larger prior to prevent small sample sizes from creating extreme home/away biases
                SPLIT_PRIOR_MATCHES = 12
                
                # Use SPECIFIC home/away averages for the priors
                # This bakes in the league's home advantage
                PRIOR_HOME_GOALS = avgs['home'] * SPLIT_PRIOR_MATCHES
                PRIOR_AWAY_GOALS = avgs['away'] * SPLIT_PRIOR_MATCHES

                home_avg_attack = (stats['home_goals_for'] + PRIOR_HOME_GOALS) / (stats['home_matches'] + SPLIT_PRIOR_MATCHES)
                stats['home_attack'] = (home_avg_attack + K_FACTOR) / (max(self.global_avg_goals, 0.1) + K_FACTOR)
                
                away_avg_attack = (stats['away_goals_for'] + PRIOR_AWAY_GOALS) / (stats['away_matches'] + SPLIT_PRIOR_MATCHES)
                stats['away_attack'] = (away_avg_attack + K_FACTOR) / (max(self.global_avg_goals, 0.1) + K_FACTOR)
                
                # Calculate form score (weighted by recency)
                form_points = 0
                form_weights = [1.0, 0.9, 0.8, 0.7, 0.6]  # More recent = higher weight
                for i, match_result in enumerate(reversed(stats['recent_results'])):
                    weight = form_weights[i] if i < len(form_weights) else 0.5
                    if match_result['result'] == 'W':
                        form_points += 3 * weight
                    elif match_result['result'] == 'D':
                        form_points += 1 * weight
                
                max_points = sum(form_weights[:len(stats['recent_results'])]) * 3
                stats['form_score'] = form_points / max(max_points, 1)
        
        # Integrate player data if provided
        if player_data:
            self._integrate_player_stats(player_data)
        
        self.is_fitted = True
    
    def _integrate_player_stats(self, player_data: List[Dict]):
        """
        Integrate player statistics to enhance team predictions
        Player stats: attack, defense, speed, strength, dexterity, stamina
        """
        team_player_stats = defaultdict(lambda: {
            'avg_attack': 0, 'avg_defense': 0, 'avg_speed': 0,
            'avg_strength': 0, 'avg_dexterity': 0, 'avg_stamina': 0,
            'player_count': 0
        })
        
        for player in player_data:
            team = player.get('team')
            if not team:
                continue
            
            team_player_stats[team]['avg_attack'] += player.get('attack', 75)
            team_player_stats[team]['avg_defense'] += player.get('defense', 75)
            team_player_stats[team]['avg_speed'] += player.get('speed', 75)
            team_player_stats[team]['avg_strength'] += player.get('strength', 75)
            team_player_stats[team]['avg_dexterity'] += player.get('dexterity', 75)
            team_player_stats[team]['avg_stamina'] += player.get('stamina', 75)
            team_player_stats[team]['player_count'] += 1
        
        # Calculate averages and apply modifiers
        for team, p_stats in team_player_stats.items():
            if p_stats['player_count'] > 0 and team in self.team_stats:
                count = p_stats['player_count']
                
                # Normalize to 0-1 scale (FIFA stats are 0-100)
                avg_attack = p_stats['avg_attack'] / count / 100
                avg_defense = p_stats['avg_defense'] / count / 100
                
                # Apply player quality modifier (10-20% impact)
                attack_modifier = 0.85 + (avg_attack * 0.3)  # Range: 0.85-1.15
                defense_modifier = 0.85 + (avg_defense * 0.3)
                
                self.team_stats[team]['attack_strength'] *= attack_modifier
                self.team_stats[team]['defense_strength'] *= defense_modifier
                
                # Store for reference
                self.player_impact[team] = {
                    'attack_quality': avg_attack,
                    'defense_quality': avg_defense,
                    'overall_quality': (avg_attack + avg_defense) / 2
                }

    def predict_match(self, team1: str, team2: str, n_samples: int = 10000, 
                     include_h2h: bool = True) -> Dict:
        """
        Predict match outcome with advanced Bayesian inference
        
        Args:
            team1: Home team name
            team2: Away team name
            n_samples: Number of Monte Carlo samples
            include_h2h: Whether to factor in head-to-head history
        
        Returns:
            Comprehensive prediction dictionary with probabilities, odds, confidence intervals
        """
        if not self.is_fitted:
            return {'error': 'Model not fitted yet. Call fit() first.'}
        
        if team1 not in self.team_stats:
            return {'error': f'Team {team1} not in training data'}
        if team2 not in self.team_stats:
            return {'error': f'Team {team2} not in training data'}
        
        stats1 = self.team_stats[team1]
        stats2 = self.team_stats[team2]
        
        # Base attack and defense strengths (with home/away adjustment)
        # We blend the specific home/away stats with the overall team strength (50/50)
        # This prevents small sample sizes (e.g., 4 home games) from creating extreme outliers
        home_attack_raw = max(stats1['home_attack'], 0.1)
        overall_attack_home = max(stats1['attack_strength'], 0.1)
        home_attack = (home_attack_raw * 0.6) + (overall_attack_home * 0.4)

        away_attack_raw = max(stats2['away_attack'], 0.1)
        overall_attack_away = max(stats2['attack_strength'], 0.1)
        away_attack = (away_attack_raw * 0.6) + (overall_attack_away * 0.4)
        
        home_defense = max(stats1['defense_strength'], 0.1)
        away_defense = max(stats2['defense_strength'], 0.1)
        
        # Form adjustment (Reduced volatility: ±10% instead of ±15%)
        # We reduce the multiplier from 0.3 to 0.15 to prevent short-term form from overriding class
        form_modifier_home = 0.925 + (stats1['form_score'] * 0.15)
        form_modifier_away = 0.925 + (stats2['form_score'] * 0.15)
        
        home_attack *= form_modifier_home
        away_attack *= form_modifier_away
        
        # TrueSkill Adjustment (The "Great Model" Factor)
        # If we have TrueSkill ratings, use them to refine the expected goals
        ts_modifier_home = 1.0
        ts_modifier_away = 1.0
        
        # Elite Matchup Dampener (Champions League Logic)
        # When two elite teams play, Home Advantage is significantly reduced.
        # Real Madrid doesn't crumble at Anfield like a mid-table team might.
        elite_dampener = 1.0
        
        if team1 in self.trueskill_ratings and team2 in self.trueskill_ratings:
            mu1 = self.trueskill_ratings[team1]
            mu2 = self.trueskill_ratings[team2]
            
            # Check if both teams are "Elite" (TrueSkill > 28.0)
            if mu1 > 28.0 and mu2 > 28.0:
                # Reduce Home Advantage impact by ~25%
                # Since HA is baked into home_attack, we apply a slight reduction factor
                elite_dampener = 0.94 
            
            # Difference in skill
            diff = mu1 - mu2
            
            # Logistic scaling for goal expectancy (More robust than linear)
            # A difference of 4.16 (1 beta) implies ~76% win probability
            # We map this to goal production using a logistic function
            # This prevents extreme multipliers for very large skill gaps
            
            # Scale factor: 1.0 means equal teams. 
            # +5 diff -> ~1.25x goals
            # -5 diff -> ~0.8x goals
            
            # Logistic function: 2 / (1 + exp(-k * diff))
            # k=0.05 gives a gentle curve
            ts_modifier_home = 2.0 / (1.0 + np.exp(-0.06 * diff))
            ts_modifier_away = 2.0 / (1.0 + np.exp(0.06 * diff))
            
            # Normalize so that if diff=0, modifier=1.0
            # The logistic function above gives 1.0 at diff=0, so it's correct.
            
        home_attack *= ts_modifier_home * elite_dampener
        away_attack *= ts_modifier_away

        # Head-to-head adjustment
        h2h_modifier = 1.0
        if include_h2h and team2 in self.h2h_history[team1]:
            h2h_matches = self.h2h_history[team1][team2]
            if len(h2h_matches) >= 2:
                # Recent h2h results influence predictions
                recent_h2h = h2h_matches[-3:]  # Last 3 meetings
                team1_wins = sum(1 for m in recent_h2h if m['home_score'] > m['away_score'])
                h2h_modifier = 0.95 + (team1_wins / len(recent_h2h) * 0.1)
        
        # Calculate expected goals with all modifiers
        # Note: We use home_attack/away_attack stats which already capture home advantage performance.
        # We do NOT multiply by (1 + home_advantage) to avoid double counting.
        expected_home_goals = (home_attack / away_defense) * self.global_avg_goals * h2h_modifier
        expected_away_goals = (away_attack / home_defense) * self.global_avg_goals
        
        # Ensure reasonable bounds (Clamped to realistic football scores)
        # 0.5 is a minimum to ensure non-zero probabilities
        # 3.5 is a high ceiling (Man City vs Luton level)
        expected_home_goals = np.clip(expected_home_goals, 0.5, 3.5)
        expected_away_goals = np.clip(expected_away_goals, 0.5, 3.5)
        
        # Monte Carlo simulation
        np.random.seed(42)
        home_goals_samples = np.random.poisson(expected_home_goals, n_samples)
        away_goals_samples = np.random.poisson(expected_away_goals, n_samples)
        
        # Calculate outcome probabilities using Dixon-Coles adjustment
        # This corrects for the independence assumption of Poisson distribution
        # specifically for low-scoring draws (0-0, 1-1) which are more common in reality.
        
        home_wins = 0
        draws = 0
        away_wins = 0
        
        # We simulate match outcomes directly
        for h, a in zip(home_goals_samples, away_goals_samples):
            # Dixon-Coles Adjustment Simulation
            # We adjust the probability of 0-0, 1-0, 0-1, 1-1
            # Since we already have samples, we can't easily adjust the *samples* themselves
            # without resampling.
            # Instead, we will calculate exact probabilities for the low scores and blend them.
            
            if h > a:
                home_wins += 1
            elif h == a:
                draws += 1
            else:
                away_wins += 1
        
        home_win_prob = home_wins / n_samples
        draw_prob = draws / n_samples
        away_win_prob = away_wins / n_samples

        # Apply Dixon-Coles Correction to the probabilities directly
        # Rho is the correlation parameter, typically -0.1 to -0.2 for football
        rho = -0.13 
        
        # Calculate probability mass for low scores using Poisson PMF
        def poisson_pmf(k, lam):
            return (lam**k * np.exp(-lam)) / np.math.factorial(k)
            
        prob_0_0 = poisson_pmf(0, expected_home_goals) * poisson_pmf(0, expected_away_goals)
        prob_1_0 = poisson_pmf(1, expected_home_goals) * poisson_pmf(0, expected_away_goals)
        prob_0_1 = poisson_pmf(0, expected_home_goals) * poisson_pmf(1, expected_away_goals)
        prob_1_1 = poisson_pmf(1, expected_home_goals) * poisson_pmf(1, expected_away_goals)
        
        # Adjustment factors
        # 0-0: 1 - (lambda * mu * rho)
        # 1-0: 1 + (mu * rho)
        # 0-1: 1 + (lambda * rho)
        # 1-1: 1 - rho
        
        adj_0_0 = 1.0 - (expected_home_goals * expected_away_goals * rho)
        adj_1_0 = 1.0 + (expected_away_goals * rho)
        adj_0_1 = 1.0 + (expected_home_goals * rho)
        adj_1_1 = 1.0 - rho
        
        # Calculate the delta (change in probability)
        delta_0_0 = prob_0_0 * (adj_0_0 - 1.0)
        delta_1_0 = prob_1_0 * (adj_1_0 - 1.0)
        delta_0_1 = prob_0_1 * (adj_0_1 - 1.0)
        delta_1_1 = prob_1_1 * (adj_1_1 - 1.0)
        
        # Apply deltas to the aggregate probabilities
        # 0-0 is a draw
        draw_prob += delta_0_0
        # 1-1 is a draw
        draw_prob += delta_1_1
        # 1-0 is a home win
        home_win_prob += delta_1_0
        # 0-1 is an away win
        away_win_prob += delta_0_1
        
        # Re-normalize to ensure sum is 1.0
        total_prob = home_win_prob + draw_prob + away_win_prob
        home_win_prob /= total_prob
        draw_prob /= total_prob
        away_win_prob /= total_prob

        # Draw Boost Logic (Legacy - Removed in favor of Dixon-Coles)
        # if abs(expected_home_goals - expected_away_goals) < 0.6: ...
        
        # Calculate betting odds (with bookmaker margin ~5%)
        margin = 1.05
        home_odds = (1 / max(home_win_prob, 0.01)) * margin
        draw_odds = (1 / max(draw_prob, 0.01)) * margin
        away_odds = (1 / max(away_win_prob, 0.01)) * margin
        
        # Score predictions with confidence intervals
        score_predictions = self._calculate_score_probabilities(
            home_goals_samples, away_goals_samples
        )
        
        # Calculate confidence score (based on data quality)
        confidence = self._calculate_confidence(stats1, stats2, len(self.h2h_history[team1].get(team2, [])))
        
        # Over/Under predictions
        total_goals_samples = home_goals_samples + away_goals_samples
        over_15_prob = np.mean(total_goals_samples > 1.5)
        over_25_prob = np.mean(total_goals_samples > 2.5)
        over_35_prob = np.mean(total_goals_samples > 3.5)
        
        # Both teams to score
        btts_prob = np.mean((home_goals_samples > 0) & (away_goals_samples > 0))
        
        return {
            'team1': team1,
            'team2': team2,
            'league': self.team_leagues.get(team1, 'Unknown League'),
            'match_info': {
                'team1_form': f"{stats1['form_score']:.2%}",
                'team2_form': f"{stats2['form_score']:.2%}",
                'h2h_matches': len(self.h2h_history[team1].get(team2, [])),
                'team1_recent': [r['result'] for r in stats1['recent_results']],
                'team2_recent': [r['result'] for r in stats2['recent_results']],
            },
            'outcome_probabilities': {
                'home_win': float(home_win_prob),
                'draw': float(draw_prob),
                'away_win': float(away_win_prob),
            },
            'betting_odds': {
                'home_odds': float(home_odds),
                'draw_odds': float(draw_odds),
                'away_odds': float(away_odds),
            },
            'goals_prediction': {
                'expected_home_goals': float(expected_home_goals),
                'expected_away_goals': float(expected_away_goals),
                'expected_total_goals': float(expected_home_goals + expected_away_goals),
                'home_goals_ci': [
                    float(np.percentile(home_goals_samples, 25)),
                    float(np.percentile(home_goals_samples, 75))
                ],
                'away_goals_ci': [
                    float(np.percentile(away_goals_samples, 25)),
                    float(np.percentile(away_goals_samples, 75))
                ],
            },
            'most_likely_scores': score_predictions[:5],
            'over_under': {
                'over_1.5': float(over_15_prob),
                'over_2.5': float(over_25_prob),
                'over_3.5': float(over_35_prob),
            },
            'both_teams_score': float(btts_prob),
            'confidence': float(confidence),
            'recommendation': self._generate_recommendation(home_win_prob, draw_prob, away_win_prob, confidence),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_score_probabilities(self, home_samples: np.ndarray, 
                                      away_samples: np.ndarray) -> List[Dict]:
        """Calculate most likely exact score predictions"""
        scores = {}
        for h, a in zip(home_samples, away_samples):
            score = f"{h}-{a}"
            scores[score] = scores.get(score, 0) + 1
        
        # Sort by probability
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for score, count in sorted_scores[:10]:
            h, a = map(int, score.split('-'))
            result.append({
                'score': score,
                'probability': float(count / len(home_samples)),
                'home_goals': h,
                'away_goals': a
            })
        
        return result
    
    def _calculate_confidence(self, stats1: Dict, stats2: Dict, h2h_count: int) -> float:
        """
        Calculate prediction confidence based on data quality
        Returns value between 0 and 1
        """
        # Factors affecting confidence:
        # 1. Number of matches played (more data = higher confidence)
        # Lowered threshold from 40 to 10 for realistic dataset size
        matches_factor = min((stats1['matches'] + stats2['matches']) / 10, 1.0)
        
        # 2. Recent form consistency (Is the team performing consistently?)
        # We assume high confidence if form is very good (>0.8) or very bad (<0.2)
        # If form is 0.5 (W-L-W-L), prediction is harder.
        form_intense_1 = abs(stats1['form_score'] - 0.5) * 2
        form_intense_2 = abs(stats2['form_score'] - 0.5) * 2
        form_factor = (form_intense_1 + form_intense_2) / 2
        
        # 3. Head-to-head data availability
        # Lowered to 2 matches for some relevance
        h2h_factor = min(h2h_count / 2, 1.0)
        
        # Weighted combination
        # Matches Volume is the most important factor
        confidence = (
            matches_factor * 0.6 +
            form_factor * 0.2 +
            h2h_factor * 0.2
        )
        
        # Bonus: If TrueSkill ratings exist, boost confidence
        if len(self.trueskill_ratings) > 0:
            confidence += 0.2
            
        return min(confidence, 1.0)
    
    def _generate_recommendation(self, home_prob: float, draw_prob: float, 
                                away_prob: float, confidence: float) -> str:
        """Generate betting recommendation based on probabilities and confidence"""
        # Lowered threshold to 0.3 for MVP
        if confidence < 0.3:
            return "Low confidence - recommend avoiding this bet"
        
        max_prob = max(home_prob, draw_prob, away_prob)
        
        if max_prob == home_prob:
            outcome = "Home Win"
            value = home_prob
        elif max_prob == draw_prob:
            outcome = "Draw"
            value = draw_prob
        else:
            outcome = "Away Win"
            value = away_prob
        
        if value > 0.6:
            return f"Strong recommendation: {outcome} (probability: {value:.1%}, confidence: {confidence:.1%})"
        elif value > 0.45:
            return f"Moderate recommendation: {outcome} (probability: {value:.1%}, confidence: {confidence:.1%})"
        else:
            return f"Slight lean: {outcome} favored (probability: {value:.1%}, confidence: {confidence:.1%})"
    
    def get_team_stats(self) -> Dict:
        """
        Get comprehensive statistics for all teams
        """
        if not self.is_fitted:
            return {'error': 'Model not fitted yet'}
        
        result = {}
        for team, stats in self.team_stats.items():
            result[team] = {
                'matches_played': stats['matches'],
                'record': {
                    'wins': stats['wins'],
                    'draws': stats['draws'],
                    'losses': stats['losses'],
                    'win_rate': stats['wins'] / max(stats['matches'], 1)
                },
                'goals': {
                    'scored': stats['goals_for'],
                    'conceded': stats['goals_against'],
                    'avg_scored': stats['goals_for'] / max(stats['matches'], 1),
                    'avg_conceded': stats['goals_against'] / max(stats['matches'], 1)
                },
                'home_away': {
                    'home_matches': stats['home_matches'],
                    'away_matches': stats['away_matches'],
                    'home_goals_avg': stats['home_goals_for'] / max(stats['home_matches'], 1),
                    'away_goals_avg': stats['away_goals_for'] / max(stats['away_matches'], 1)
                },
                'strength_ratings': {
                    'attack_strength': float(stats['attack_strength']),
                    'defense_strength': float(stats['defense_strength']),
                    'home_attack': float(stats['home_attack']),
                    'away_attack': float(stats['away_attack']),
                    'form_score': float(stats['form_score'])
                },
                'recent_form': stats['recent_results'],
                'player_quality': self.player_impact.get(team, {})
            }
        
        return result
    
    def get_head_to_head(self, team1: str, team2: str) -> Dict:
        """Get head-to-head statistics between two teams"""
        if team1 not in self.team_stats or team2 not in self.team_stats:
            return {'error': 'One or both teams not found'}
        
        h2h_matches = self.h2h_history[team1].get(team2, [])
        
        if not h2h_matches:
            return {
                'team1': team1,
                'team2': team2,
                'matches_played': 0,
                'message': 'No head-to-head history available'
            }
        
        team1_wins = sum(1 for m in h2h_matches if m['home_score'] > m['away_score'])
        draws = sum(1 for m in h2h_matches if m['home_score'] == m['away_score'])
        team2_wins = len(h2h_matches) - team1_wins - draws
        
        return {
            'team1': team1,
            'team2': team2,
            'matches_played': len(h2h_matches),
            'team1_wins': team1_wins,
            'draws': draws,
            'team2_wins': team2_wins,
            'recent_matches': h2h_matches[-5:],
            'avg_goals_team1': sum(m['home_score'] for m in h2h_matches) / len(h2h_matches),
            'avg_goals_team2': sum(m['away_score'] for m in h2h_matches) / len(h2h_matches)
        }
    
    def predict_tournament(self, matches: List[Tuple[str, str]]) -> List[Dict]:
        """Predict outcomes for multiple matches"""
        predictions = []
        for team1, team2 in matches:
            prediction = self.predict_match(team1, team2)
            predictions.append(prediction)
        return predictions
    
    def export_model_state(self) -> str:
        """Export model state as JSON for persistence"""
        state = {
            'team_stats': self.team_stats,
            'player_impact': self.player_impact,
            'h2h_history': {k: dict(v) for k, v in self.h2h_history.items()},
            'global_avg_goals': self.global_avg_goals,
            'league_averages': self.league_averages,
            'team_leagues': self.team_leagues,
            'is_fitted': self.is_fitted,
            'export_timestamp': datetime.now().isoformat()
        }
        return json.dumps(state, default=str)
    
    def import_model_state(self, state_json: str):
        """Import model state from JSON"""
        state = json.loads(state_json)
        self.team_stats = state['team_stats']
        self.player_impact = state['player_impact']
        self.h2h_history = defaultdict(lambda: defaultdict(list), 
                                      {k: defaultdict(list, v) for k, v in state['h2h_history'].items()})
        self.global_avg_goals = state['global_avg_goals']
        self.league_averages = state.get('league_averages', {})
        self.team_leagues = state.get('team_leagues', {})
        self.is_fitted = state['is_fitted']


    def get_team_stats(self) -> Dict[str, Dict]:
        """Retourner les stats de toutes les équipes"""
        result = {}
        for team, stats in self.team_stats.items():
            result[team] = {
                'attack': float(stats['attack_strength']),
                'defense': float(stats['defense_strength']),
                'strength': float((stats['attack_strength'] + stats['defense_strength']) / 2),
                'matches': int(stats['matches']),
                'wins': int(stats['wins']),
                'draws': int(stats['draws']),
                'losses': int(stats['losses'])
            }
        return result
