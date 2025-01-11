from __future__ import annotations

__docformat__ = "restructuredtext"

__version__ = "1.0.0"

__doc__ = """
FitData Package
===============

FitData provides tools for analyzing and managing health-related data and fitness goals.
It includes core calculations such as BMI (Body Mass Index), BMR (Basal Metabolic Rate),
and TDEE (Total Daily Energy Expenditure). The package also supports advanced features
like caloric adjustments, macronutrient management, and weekly progression tracking.

Main Features:
- `FitData`: The main class for managing user data.
- `basic_calc`: Core calculations for BMI, BMR, and TDEE.
- `other_calc`: Advanced calculations for caloric adjustments, macros, and duration estimation.
- `weeklyprogression`: Tracks weekly progression and provides feedback.
- `interfaces`: Defines structured types for user input data.

Dependencies:
This package requires `numpy` and `pandas` to function properly.
"""

from fitdata.fitdata import FitData
import fitdata.basic_calc as calc
import fitdata.other_calc as advanced
import fitdata.interfaces as itf
import fitdata.errors as err
import fitdata.objective as obj
import fitdata.weeklyprogression as progress


def create_fitdata(user:itf.UserDataEntry):
    """
    Create a FitData instance with user input data.

    Args:
        global_data (dict): User's global data (weight, age, height, etc.).
        physical_data (dict, optional): Physical activity and lifestyle data.

    Returns:
        FitData: An instance of FitData initialized with the given data.
    """
    return FitData(**user)


TEST_VALUE:itf.UserDataEntry = {
    "global_data": {
        "age": 32,
        "gender": "male",
        "height": 186.0,
        "weight": 75,
        "objective": "weight gain",
        "target_duration": 60,
        "target_weight": 85,
    },
    "physical_data": {
        "activity_type": "musculation",
        "frequency_physical_activity": "low",
        "quality_of_sleep": 8.0,
        "stress_level": "low",
        "consumption_of_alcohol_or_tobacco": "none",
    },
}

__all__ = [
    'FitData',
    'calc',
    'advanced',
    'itf',
    'err',
    'obj',
    'progress',
    'create_fitdata',
    'TEST_VALUE'
]
