# src/parse_apple_health_data/parser.py
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from .utils import HealthRecord, QuantityRecord, CategoryRecord

class HealthDataParser:
    """Parser for Apple Health Export data."""
    
    def __init__(self, xml_path: str, debug: bool = False):
        self.xml_path = xml_path
        self.debug = debug
        self.tree = ET.parse(xml_path)
        self.root = self.tree.getroot()
        
        if self.debug:
            print(f"Root tag: {self.root.tag}")
            for child in list(self.root)[:2]:
                print(f"Child tag: {child.tag}")
                print(f"Child attributes: {child.attrib}")
        
        # Define record type categories
        self.quantity_types = {
            'HKQuantityTypeIdentifierHeight',
            'HKQuantityTypeIdentifierBodyMass',
            'HKQuantityTypeIdentifierStepCount',
            'HKQuantityTypeIdentifierDistanceWalkingRunning',
            'HKQuantityTypeIdentifierBasalEnergyBurned',
            'HKQuantityTypeIdentifierActiveEnergyBurned',
            'HKQuantityTypeIdentifierFlightsClimbed',
            'HKQuantityTypeIdentifierHeadphoneAudioExposure',
            'HKQuantityTypeIdentifierWalkingDoubleSupportPercentage',
            'HKQuantityTypeIdentifierWalkingSpeed',
            'HKQuantityTypeIdentifierWalkingStepLength',
            'HKQuantityTypeIdentifierWalkingAsymmetryPercentage',
            'HKQuantityTypeIdentifierAppleWalkingSteadiness'
        }
        
        self.category_types = {
            'HKCategoryTypeIdentifierSleepAnalysis',
            'HKCategoryTypeIdentifierHeadphoneAudioExposureEvent',
            'HKDataTypeSleepDurationGoal'
        }
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse Apple Health datetime format."""
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
    
    def _extract_record_type(self, element: ET.Element) -> Optional[str]:
        """Extract record type from element, handling different XML structures."""
        # Try different possible attribute names
        for attr in ['type', '@type', 'recordType']:
            if attr in element.attrib:
                return element.attrib[attr]
        
        # If type is not in attributes, check if it's in the tag name
        if element.tag in ['Record', 'record']:
            if 'type' in element.attrib:
                return element.attrib['type']
        
        # If the tag itself is a type
        if element.tag in self.quantity_types or element.tag in self.category_types:
            return element.tag
        
        if self.debug:
            print(f"Could not extract type from element: {element.tag}")
            print(f"Available attributes: {element.attrib}")
        
        return None
    
    def _create_record(self, element: ET.Element) -> Optional[HealthRecord]:
        """Create appropriate record type from XML element."""
        if self.debug:
            print(f"Processing element: {element.tag}")
            print(f"Attributes: {element.attrib}")
        
        try:
            attrs = element.attrib
            record_type = self._extract_record_type(element)
            
            if not record_type:
                if self.debug:
                    print("Skipping element due to missing record type")
                return None
            
            # Map attribute names (handle different possible XML structures)
            attr_mapping = {
                'sourceName': ['sourceName', 'source_name', 'source'],
                'sourceVersion': ['sourceVersion', 'source_version', 'version'],
                'device': ['device', 'deviceName', 'device_name'],
                'creationDate': ['creationDate', 'creation_date', 'created'],
                'startDate': ['startDate', 'start_date', 'start'],
                'endDate': ['endDate', 'end_date', 'end'],
                'value': ['value', 'val'],
                'unit': ['unit', 'units']
            }
            
            def get_attr(attr_names):
                for name in attr_names:
                    if name in attrs:
                        return attrs[name]
                if self.debug:
                    print(f"Missing attribute, tried: {attr_names}")
                return None
            
            base_args = {
                'type': record_type,
                'source_name': get_attr(attr_mapping['sourceName']) or 'unknown',
                'source_version': get_attr(attr_mapping['sourceVersion']) or 'unknown',
                'device': get_attr(attr_mapping['device']) or 'unknown',
                'creation_date': self._parse_datetime(get_attr(attr_mapping['creationDate'])),
                'start_date': self._parse_datetime(get_attr(attr_mapping['startDate'])),
                'end_date': self._parse_datetime(get_attr(attr_mapping['endDate']))
            }
            
            if record_type in self.quantity_types:
                value = get_attr(attr_mapping['value'])
                unit = get_attr(attr_mapping['unit'])
                if value is None or unit is None:
                    if self.debug:
                        print(f"Missing required quantity attributes for type {record_type}")
                    return None
                return QuantityRecord(
                    **base_args,
                    value=float(value),
                    unit=unit
                )
            elif record_type in self.category_types:
                value = get_attr(attr_mapping['value'])
                if value is None:
                    if self.debug:
                        print(f"Missing required category attributes for type {record_type}")
                    return None
                return CategoryRecord(
                    **base_args,
                    value=value
                )
            
            return None
            
        except Exception as e:
            if self.debug:
                print(f"Error processing record: {str(e)}")
            return None
    
    def get_records_by_type(self) -> Dict[str, List[HealthRecord]]:
        """Parse all records and organize them by type."""
        records = {}
        
        for element in self.root:
            record = self._create_record(element)
            if record:
                if record.type not in records:
                    records[record.type] = []
                records[record.type].append(record)
                
        return records
    
    def to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert records to pandas DataFrames by type."""
        records_by_type = self.get_records_by_type()
        dataframes = {}
        
        for record_type, records in records_by_type.items():
            records_dicts = [vars(record) for record in records]
            dataframes[record_type] = pd.DataFrame(records_dicts)
            
        return dataframes

def load_health_data(xml_path: str, debug: bool = False) -> HealthDataParser:
    """Convenience function to create parser instance."""
    return HealthDataParser(xml_path, debug=debug)
