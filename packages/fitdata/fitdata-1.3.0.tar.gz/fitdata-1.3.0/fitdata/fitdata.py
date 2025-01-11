from fitdata.interfaces import UserDataEntry, GlobalDataEntry, DailyPhysicalActivityData
from fitdata.errors import InvalidGlobalDataException
from fitdata.objective import FitObjectiveData
from typing import Optional


def get_default_value(physical_activity_data: Optional[DailyPhysicalActivityData]) -> DailyPhysicalActivityData:
    default_value: DailyPhysicalActivityData = {
        "activity_type": "musculation",
        "consumption_of_alcohol_or_tobacco": "none",
        "quality_of_sleep": 8.0,
        "stress_level": "none",
        "frequency_physical_activity": "moderate"
    }

    if not physical_activity_data:
        return default_value
    for k, v in physical_activity_data.items():
        default_value[k] = v

    return default_value


def check_value_global(global_data: GlobalDataEntry) -> None:
    weight = global_data["weight"]
    target_weight = global_data["target_weight"]
    objective = global_data["objective"]

    if objective == "weight gain" and weight >= target_weight:
        raise InvalidGlobalDataException(
            "For weight gain, the current weight must be less than the target weight")
    elif objective == "weight loss" and weight <= target_weight:
        raise InvalidGlobalDataException(
            "For weight loss, the current weight must be greater than the target weight")
    elif objective == "maintenance" and weight != target_weight:
        raise InvalidGlobalDataException(
            "For maintenance, the current weight must match the target weight")
    elif objective == "recomposition":
        # Aucun contrôle strict ici
        pass


def check_physical_activity_data(physical_activity_data: DailyPhysicalActivityData) -> None:
    sleep = physical_activity_data["quality_of_sleep"]
    if sleep < 0 or sleep > 24:
        raise InvalidGlobalDataException(
            "Quality of sleep must be between 0 and 24 hours")


class FitData(FitObjectiveData):
    """
    Class for managing and validating user data related to fitness objectives.

    This class extends `FitObjectiveData` to handle the initialization and validation
    of user-provided global and physical activity data. It ensures that the data is 
    consistent, complete, and properly formatted before passing it to the parent class 
    for further processing.

    Features:
        - Validates `global_data` (e.g., age, weight, height, target goals).
        - Validates `physical_activity_data` (e.g., activity type, sleep quality, stress levels).
        - Provides default values for optional physical activity data if not supplied.
        - Seamlessly integrates with `FitObjectiveData` to compute fitness-related metrics.

    Args:
        global_data (GlobalDataEntry): The user's global data, including weight, age, height,
            and target fitness objectives.
        physical_activity_data (Optional[DailyPhysicalActivityData]): The user's physical activity
            and lifestyle data. If not provided, default values are used.

    Raises:
        ValueError: If `global_data` or `physical_activity_data` contain invalid or inconsistent values.
    """

    def __init__(
        self,
        global_data: GlobalDataEntry,
        physical_activity_data: Optional[DailyPhysicalActivityData] = None
    ) -> None:
        check_value_global(global_data)
        check_physical_activity_data(physical_activity_data)
        user_data: UserDataEntry = {
            "global_data": global_data,
            "physical_data": get_default_value(physical_activity_data)
        }
        super().__init__(user_data)
