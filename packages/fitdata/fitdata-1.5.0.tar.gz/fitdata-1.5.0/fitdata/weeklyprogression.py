from fitdata.other_calc import CaloricAdjustment
from fitdata.interfaces import UserDataEntry
from typing import Tuple


class WeeklyProgression:
    """
    Class for calculating and evaluating weekly weight progression.

    This class calculates the user's expected weekly weight progression 
    (gain or loss) based on their daily caloric adjustment. It evaluates 
    whether the weekly progression is within a healthy range and provides 
    a warning if it exceeds ±2 kg per week.

    Features:
        - Computes weekly caloric adjustment based on daily caloric deficit or surplus.
        - Converts weekly calories into kilograms (7700 kcal per kg).
        - Warns if the progression exceeds ±2 kg per week.
        - Provides a message and the calculated progression value.

    Args:
        user (UserDataEntry): The user's data, including global information 
            (e.g., age, weight, height, target objectives) and physical activity data 
            (e.g., activity type, sleep quality, stress level).

    Attributes:
        user_data (UserDataEntry): The user's data passed during initialization.
        caloric_adjustment (CaloricAdjustment): An instance of `CaloricAdjustment` 
            used to calculate the daily caloric adjustment.
        __progression (Tuple[str, float]): A tuple containing a message about the weekly progression 
            and the numerical progression value.

    Methods:
        __calc_weekly_progression() -> Tuple[str, float]:
            Computes the weekly progression and checks if it is within the healthy range.

    Properties:
        progression (Tuple[str, float]): Returns the message and the weekly progression value.
    """

    def __init__(self, user: UserDataEntry) -> None:
        self.user_data = user
        self.caloric_adjustment = CaloricAdjustment(self.user_data)
        self.__progression = self.__calc_weekly_progression()

    def __calc_weekly_progression(self) -> Tuple[str, float]:
        daily_adjustment = self.caloric_adjustment.adjustment
        weekly_calories = daily_adjustment * 7
        weekly_progression = weekly_calories / 7700

        if abs(weekly_progression) > 2:
            return (
                "Attention : Progression hebdomadaire trop rapide (plus de 2 kg par semaine)",
                weekly_progression,
            )

        return "Progression hebdomadaire dans les limites normales.", weekly_progression

    @property
    def progression(self) -> Tuple[str, float]:
        return self.__progression
