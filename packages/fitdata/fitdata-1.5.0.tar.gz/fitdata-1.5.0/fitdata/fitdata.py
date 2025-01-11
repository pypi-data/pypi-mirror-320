from fitdata.interfaces import UserDataEntry, GlobalDataEntry, DailyPhysicalActivityData, MacrosData
from fitdata.errors import InvalidGlobalDataException
from fitdata.objective import FitObjectiveData
from typing import Optional, overload, Literal, Union, Tuple


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

    This class extends `FitObjectiveData` and manages the initialization and validation 
    of global user data and physical activity data. It ensures that the data is consistent, 
    complete, and correctly formatted before being processed by the parent class to compute 
    fitness metrics.

    Features:
        - Validates global data (`global_data`), such as age, weight, height, and objectives.
        - Validates physical activity data (`physical_activity_data`), including activity type, 
          sleep quality, and stress levels.
        - Provides default values for optional physical activity data if not supplied.
        - Adds a method to retrieve fitness metrics using the indexing operator (`__getitem__`).

    `__getitem__` Method:
        - Enables access to specific data via predefined keys:
            - "BMR": Basal Metabolic Rate (float).
            - "IMC": Body Mass Index (float).
            - "TDEE": Total Daily Energy Expenditure (float).
            - "CaloricAdjustment": Caloric Adjustment (float).
            - "DurationEstimator": Estimated time to achieve objectives (float).
            - "Macros": Macronutrient data (MacrosData).
            - "WeeklyProgression": Weekly progression (Tuple[str, float]).

    Args:
        global_data (GlobalDataEntry): User's global data, including weight, age, 
            height, and fitness objectives.
        physical_activity_data (Optional[DailyPhysicalActivityData]): User's physical activity 
            and lifestyle data. If not provided, default values are used.

    Raises:
        ValueError: If `global_data` or `physical_activity_data` contains invalid 
            or inconsistent values.
        KeyError: If an invalid key is used with the `__getitem__` method.
    """

    def __init__(
        self,
        global_data: GlobalDataEntry,
        physical_data: Optional[DailyPhysicalActivityData] = None
    ) -> None:
        check_value_global(global_data)
        check_physical_activity_data(physical_data)
        user_data: UserDataEntry = {
            "global_data": global_data,
            "physical_data": get_default_value(physical_data)
        }
        super().__init__(user_data)

    @overload
    def __getitem__(self, key: Literal["BMR", "IMC", "TDEE",
                    "CaloricAdjustment", "DurationEstimator"]) -> float: ...

    @overload
    def __getitem__(self, key: Literal["Macros"]) -> MacrosData: ...

    @overload
    def __getitem__(
        self, key: Literal["WeeklyProgression"]) -> Tuple[str, float]: ...

    def __getitem__(
        self,
        key: Literal["BMR", "IMC", "TDEE", "CaloricAdjustment",
                     "DurationEstimator", "Macros", "WeeklyProgression"]
    ) -> Union[float, MacrosData, Tuple[str, float]]:
        return self.__get_item(key)

    def __get_item(self, key: Literal["BMR", "IMC", "TDEE", "CaloricAdjustment",
                                      "DurationEstimator", "Macros", "WeeklyProgression"]) -> Union[float, MacrosData, Tuple[str, float]]:
        match key:
            case 'BMR':
                return self.BMR.bmr
            case 'IMC':
                return self.IMC.imc
            case 'TDEE':
                return self.TDEE.tdee
            case 'CaloricAdjustment':
                return self.CaloricAdjustment.adjustment
            case 'DurationEstimator':
                return self.DurationEstimator.duration
            case 'Macros':
                return self.Macros.macros
            case 'WeeklyProgression':
                return self.WeeklyProgression.progression
