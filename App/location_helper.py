from sqlalchemy.orm import Session
from models.models import LocationLog

def save_location(db: Session, agent_id: int, order_id: int, lat: float, lng: float):
    loc = LocationLog(
        agent_id=agent_id,
        order_id=order_id,
        lat=lat,
        lng=lng
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


def get_location_history(db : Session,order_id : int):
    return(
        db.query(LocationLog)
        .filter(LocationLog.order_id == order_id)
        .order_by(LocationLog.timestamp.asc())
        .all()
    )

def get_last_location_for_order(db,order_id :int):
    return(
        db.query(LocationLog)
        .filter(LocationLog.order_id == order_id)
        .order_by(LocationLog.timestamp.desc())
        .first()
    )