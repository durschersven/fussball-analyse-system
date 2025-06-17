from typing import Optional
from sqlalchemy.orm import Session

from .models import Team, Match


def update_elos(session: Session, k: float = 20.0) -> None:
    """Update team Elo ratings based on chronological match results."""
    teams = session.query(Team).all()
    for team in teams:
        if team.elo is None:
            team.elo = 1000.0
    session.commit()

    matches = (
        session.query(Match)
        .filter(Match.home_goals != None)
        .order_by(Match.date)
        .all()
    )
    for m in matches:
        home: Optional[Team] = session.get(Team, m.home_team_id)
        away: Optional[Team] = session.get(Team, m.away_team_id)
        if not home or not away:
            continue
        # expected result probabilities
        expected_home = 1 / (1 + 10 ** ((away.elo - home.elo) / 400))
        expected_away = 1 - expected_home
        if m.home_goals > m.away_goals:
            score_home, score_away = 1, 0
        elif m.home_goals < m.away_goals:
            score_home, score_away = 0, 1
        else:
            score_home = score_away = 0.5
        home.elo += k * (score_home - expected_home)
        away.elo += k * (score_away - expected_away)
    session.commit()
