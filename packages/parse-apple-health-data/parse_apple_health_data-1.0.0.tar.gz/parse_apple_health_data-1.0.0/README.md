# Apple Health Parser

https://pypi.org/project/parse-apple-health-data/1.0.0/

A Python package for parsing and analyzing Apple Health Export data.

## Installation

```bash
pip install parse-apple-health-data
```

## Usage

```python
from parse_apple_health_data import load_health_data

# Create parser instance
parser = load_health_data('export.xml')

# Get data as pandas DataFrames
dataframes = parser.to_dataframes()

# Physical Measurements:
height_df = dataframes['HKQuantityTypeIdentifierHeight']
body_mass_df = dataframes['HKQuantityTypeIdentifierBodyMass']

# Activity Tracking:
steps_df = dataframes['HKQuantityTypeIdentifierStepCount']
distance_walking_running_df = dataframes['HKQuantityTypeIdentifierDistanceWalkingRunning']
flights_climbed_df = dataframes['HKQuantityTypeIdentifierFlightsClimbed']

# Energy Expenditure:
basal_energy_burned_df = dataframes['HKQuantityTypeIdentifierBasalEnergyBurned']
active_energy_burned_df = dataframes['HKQuantityTypeIdentifierActiveEnergyBurned']

# Audio Exposure:
headphone_audio_exposure_df = dataframes['HKQuantityTypeIdentifierHeadphoneAudioExposure']
audio_exposure_event_df = dataframes['HKCategoryTypeIdentifierHeadphoneAudioExposureEvent']

# Walking Metrics:
walking_double_support_percentage_df = dataframes['HKQuantityTypeIdentifierWalkingDoubleSupportPercentage']
walking_speed_df = dataframes['HKQuantityTypeIdentifierWalkingSpeed']
walking_step_length_df = dataframes['HKQuantityTypeIdentifierWalkingStepLength']
walking_asymmetry_percentage_df = dataframes['HKQuantityTypeIdentifierWalkingAsymmetryPercentage']
walking_steadiness_df = dataframes['HKQuantityTypeIdentifierAppleWalkingSteadiness']

# Sleep Metrics:
sleep_analysis_df = dataframes['HKCategoryTypeIdentifierSleepAnalysis']
sleep_duration_goal_df = dataframes['HKDataTypeSleepDurationGoal']
```

## Features

- Parse Apple Health Export XML files
- Convert health data to pandas DataFrames
- Separate handling for quantity and category measurements
- Preserve all metadata from original export
- Type hints and documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.
