import enum
from sqlalchemy import TIMESTAMP, Column, DateTime, Enum, Float, ForeignKey, Index, Integer, String, func, text
from database import Base
from sqlalchemy.orm import relationship

from enums import UserRole
from schemas import OrderStatus



class User(Base):

    __tablename__ = "users"

    id = Column(Integer,primary_key = True,nullable = False)
    name = Column(String,nullable = False)
    email = Column(String,nullable = False,unique = True)
    password = Column(String(250),nullable = False)
    role = Column(Enum(UserRole),nullable=False,server_default=UserRole.customer.value)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))

    location_logs = relationship("LocationLog", back_populates="agent")

class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer,primary_key = True,nullable = False)

    customer_id = Column(Integer,ForeignKey("users.id",ondelete='cascade'),nullable = False)
    agent_id = Column(Integer,ForeignKey("users.id",ondelete='cascade'),nullable = True)

    pickup_add = Column(String,nullable=False)
    pickup_lat = Column(Float,nullable = False)
    pickup_lng = Column(Float,nullable = False)

    drop_add = Column(String,nullable=False)
    drop_lat = Column(Float,nullable = False)
    drop_lng = Column(Float,nullable = False)

    status = Column(Enum(OrderStatus), default=OrderStatus.created, nullable=False)


    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("User", foreign_keys=[customer_id])
    agent = relationship("User", foreign_keys=[agent_id])

    location_logs = relationship("LocationLog", back_populates="order")


class LocationLog(Base):
    __tablename__ = "location_log"

    id = Column(Integer,primary_key=True,index= True)
    order_id = Column(Integer,ForeignKey("orders.id",ondelete='CASCADE'),index = True,nullable = False)
    agent_id = Column(Integer,ForeignKey("users.id",ondelete = 'SET NULL'),index = True,nullable=True)

    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="location_logs")
    agent = relationship("User", back_populates="location_logs")

    __table_args__ = (
        Index("idx_order_timestamp", "order_id", "timestamp"),
        Index("idx_agent_timestamp", "agent_id", "timestamp"),
    )