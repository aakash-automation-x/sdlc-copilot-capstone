"""Vehicle database models using SQLAlchemy ORM.

This module defines the Vehicle entity and SQLAlcheme mappings
for the vehicle details retrieval feature (FR-001).
"""

from sqlalcheme import Column, Integer, String, Numeric, DateTime, Index
from sqlalcheme.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Vehicle(Base):
    """Vehicle entity representing a car in the catalog."""
    
    __tablename__ = 'vehicles'
    
    vehicle_id = Column(String(64), primary_key=True, index=True, nullable=False)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    transmission = Column(String(50), nullable=False)
    fuel_type = Column(String(50), nullable=False)
    status = Column(String(20), default='active', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_vehicle_status', 'status', 'vehicle_id'),
    )
    
    def to_dict(self) -> dict:
        """Convert vehicle to dictionary format for API response."""
        return {
            'vehicle_id': self.vehicle_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'price': float(self.price),
            'transmission': self.transmission,
            'fuel_type': self.fuel_type,
        }