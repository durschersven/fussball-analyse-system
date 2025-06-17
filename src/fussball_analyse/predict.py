import pandas as pd
from sqlalchemy.orm import Session
from sklearn.linear_model import LogisticRegression

from .models import Match, Prediction, Team


def predict_upcoming(model: LogisticRegression, session: Session) -> pd.DataFrame:
    """Predict results for matches without scores and store them."""
    upcoming = session.query(Match).filter(Match.home_goals == None).all()
    data = []
    ids = []
    for m in upcoming:
        home = session.get(Team, m.home_team_id)
        away = session.get(Team, m.away_team_id)
        home_elo = getattr(home, "elo", 1000.0) if home else 1000.0
        away_elo = getattr(away, "elo", 1000.0) if away else 1000.0
        data.append([m.home_team_id, m.away_team_id, home_elo - away_elo])
        ids.append(m.id)
    X = pd.DataFrame(data, columns=['home_team_id', 'away_team_id', 'elo_diff'])
    if X.empty:
        return pd.DataFrame()
    predictions = model.predict(X)
    # store predictions in DB
    for match_id, pred in zip(ids, predictions):
        p = Prediction(match_id=match_id, predicted_result=int(pred))
        session.add(p)
    session.commit()
    return pd.DataFrame({'match_id': ids, 'prediction': predictions})
