# tests/test_parser.py
from parse_apple_health_data import HealthDataParser, HealthRecord, QuantityRecord, CategoryRecord
from datetime import datetime
import xml.etree.ElementTree as ET

def test_parse_datetime():
    parser = HealthDataParser("dummy.xml")
    date_str = "2023-10-05 14:22:07 -0500"
    result = parser._parse_datetime(date_str)
    assert isinstance(result, datetime)
