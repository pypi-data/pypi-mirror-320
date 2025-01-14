# src/parse_apple_health_data/utils.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class HealthRecord:
    """Base class for health records with common attributes."""
    type: str
    source_name: str
    source_version: str
    device: str
    creation_date: datetime
    start_date: datetime
    end_date: datetime

@dataclass
class QuantityRecord(HealthRecord):
    """Record type for quantitative measurements."""
    value: float
    unit: str

@dataclass
class CategoryRecord(HealthRecord):
    """Record type for categorical measurements."""
    value: str
