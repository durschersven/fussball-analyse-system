from typing import Tuple

import pandas as pd
from sqlalchemy.orm import Session
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score

from .models import Match, Team


def prepare_training_data(session: Session) -> Tuple[pd.DataFrame, pd.Series]:
    matches = session.query(Match).filter(Match.home_goals != None).all()
    data = []
    targets = []
    for m in matches:
        home = session.get(Team, m.home_team_id)
        away = session.get(Team, m.away_team_id)
        home_elo = getattr(home, "elo", 1000.0) if home else 1000.0
        away_elo = getattr(away, "elo", 1000.0) if away else 1000.0
        data.append([
            m.home_team_id,
            m.away_team_id,
            home_elo - away_elo,
        ])
        if m.home_goals > m.away_goals:
            targets.append(1)
        elif m.home_goals < m.away_goals:
            targets.append(-1)
        else:
            targets.append(0)
    df = pd.DataFrame(data, columns=['home_team_id', 'away_team_id', 'elo_diff'])
    target_series = pd.Series(targets)
    return df, target_series


def train_model(X: pd.DataFrame, y: pd.Series) -> LogisticRegression:
    model = LogisticRegression()
    model.fit(X, y)
    return model


def evaluate_model(model: LogisticRegression, X: pd.DataFrame, y: pd.Series) -> float:
    preds = model.predict(X)
    return accuracy_score(y, preds)


def cross_validated_score(X: pd.DataFrame, y: pd.Series, folds: int = 5) -> float:
    """Return mean accuracy using cross-validation."""
    if len(y) < 2:
        return 0.0
    model = LogisticRegression()
    scores = cross_val_score(model, X, y, cv=min(folds, len(y)))
    return float(scores.mean())

