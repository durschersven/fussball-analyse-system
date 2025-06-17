from sqlalchemy.orm import Session

from .models import Match, Prediction, TrainingRun

from .predict import predict_upcoming
from .train import (
    prepare_training_data,
    train_model,
    evaluate_model,
    cross_validated_score,
)
from .elo import update_elos


def update_prediction_results(session: Session) -> None:
    """Match stored predictions with actual results once available."""
    preds = session.query(Prediction).filter(Prediction.actual_result == None).all()
    for p in preds:
        match = session.get(Match, p.match_id)
        if match and match.home_goals is not None and match.away_goals is not None:
            if match.home_goals > match.away_goals:
                p.actual_result = 1
            elif match.home_goals < match.away_goals:
                p.actual_result = -1
            else:
                p.actual_result = 0
    session.commit()


def evaluate_predictions(session: Session) -> float:
    """Return accuracy for predictions with known results."""
    preds = session.query(Prediction).filter(Prediction.actual_result != None).all()
    if not preds:
        return 0.0
    correct = sum(1 for p in preds if p.actual_result == p.predicted_result)
    return correct / len(preds)


def self_improve(session: Session):
    update_prediction_results(session)
    update_elos(session)
    X, y = prepare_training_data(session)
    if X.empty:
        print("Not enough data to train.")
        return
    cv_score = cross_validated_score(X, y)
    if cv_score:
        print(f"Cross-validated accuracy: {cv_score:.2f}")
    model = train_model(X, y)
    accuracy = evaluate_model(model, X, y)
    print(f"Training accuracy: {accuracy:.2f}")

    # Predict upcoming matches
    preds = predict_upcoming(model, session)
    if preds.empty:
        print("No upcoming matches to predict.")
    else:
        print(preds)

    pred_acc = evaluate_predictions(session)
    if pred_acc:
        print(f"Prediction accuracy so far: {pred_acc:.2f}")

    run = TrainingRun(
        training_size=len(y),
        accuracy=float(accuracy),
        cv_accuracy=float(cv_score),
    )
    session.add(run)
    session.commit()
