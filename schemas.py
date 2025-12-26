from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr

from enums import OrderStatus, UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.customer

class UserOut(BaseModel):
    id : int
    email : EmailStr
    role : str

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    pickup_add : str
    pickup_lat : float
    pickup_lng : float

    drop_add : str
    drop_lat : float
    drop_lng : float

class OrderAssign(BaseModel):
    agent_id : int

class OrderUpdateStatus(BaseModel):
    status : OrderStatus

class OrderResponse(BaseModel):
    id : int
    customer_id : int
    agent_id : int | None

    pickup_add : str
    pickup_lat : float
    pickup_lng : float

    drop_add : str
    drop_lat : float
    drop_lng : float

    status: OrderStatus

    class Config:
        from_attributes = True
    
class LocationUpdate(BaseModel):
    order_id : int
    lat : float
    lng : float

class LocationResponse(BaseModel):
    lat : float
    lng : float
    timestamp : str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    id : Optional[int] = None
    role : Optional[str] = None