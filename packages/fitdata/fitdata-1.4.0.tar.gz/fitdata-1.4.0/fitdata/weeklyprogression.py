from fitdata.other_calc import CaloricAdjustment
from fitdata.interfaces import UserDataEntry
from typing import Tuple


class WeeklyProgression:
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

