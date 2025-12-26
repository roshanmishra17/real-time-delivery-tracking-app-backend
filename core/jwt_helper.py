from jose import JWTError, jwt
from config import settings
from database import SessionLocal
import models.models as models
def get_user_from_token(token : str):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORIGTHM])
    except JWTError:
        return None

    print("TOKEN PAYLOAD:", payload)

    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user
    finally:
        db.close()

