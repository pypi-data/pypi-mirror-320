from fitdata.interfaces import UserDataEntry
from typing import Literal
from math import pow

class IMC:
    """
    Class for calculating the Body Mass Index (BMI) and determining the corresponding category.
    """

    def __init__(self, user: UserDataEntry) -> None:
        self.user_data = user
        self.__validate_inputs()
        self.__imc = self.__calc_imc()
        self.__category = self.__define_category()

    def __validate_inputs(self) -> None:
        weight = self.user_data['global_data']['weight']
        height = self.user_data['global_data']['height']
        if weight <= 0 or height <= 0:
            raise ValueError("Weight and height must be positive values.")

    def __calc_imc(self) -> float:
        weight = float(self.user_data['global_data']['weight'])
        height = float(self.user_data['global_data']
                       ['height']) / 100  # Convert cm to m
        return weight / pow(height, 2)

    def __define_category(self) -> Literal["underweight", "normal", "overweight", "obesity"]:
        if self.__imc < 18.5:
            return "underweight"
        elif 18.5 <= self.__imc < 25:
            return "normal"
        elif 25 <= self.__imc < 30:
            return "overweight"
        else:
            return "obesity"

    @property
    def imc(self) -> float:
        return self.__imc

    @property
    def category(self) -> Literal["underweight", "normal", "overweight", "obesity"]:
        return self.__category


class BMR:
    """
    Class for calculating the Basal Metabolic Rate (BMR).
    """
    def __init__(self, user: UserDataEntry):
        self.user_data = user
        self.__validate_inputs()
        self.__bmr = self.__calc_bmr()

    def __validate_inputs(self) -> None:
        weight = self.user_data["global_data"]["weight"]
        height = self.user_data["global_data"]["height"]
        age = self.user_data["global_data"]["age"]
        if weight <= 0 or height <= 0 or age <= 0:
            raise ValueError(
                "Weight, height, and age must be positive values.")

    def __calc_bmr(self) -> float:
        gender = self.user_data["global_data"]["gender"]
        weight = float(self.user_data["global_data"]["weight"])
        height = float(self.user_data["global_data"]["height"])
        age = float(self.user_data["global_data"]["age"])
        k = 161. if gender == "female" else 5.
        return (10. * weight) + (6.25 * height) - (5. * age) - k

    @property
    def bmr(self) -> float:
        return self.__bmr


class TDEE:
    """
    Class for calculating the Total Daily Energy Expenditure (TDEE).
    """
    def __init__(self, user: UserDataEntry) -> None:
        self.user_data = user
        self.bmr = BMR(self.user_data)
        self.__tdee = self.__calc_tdee()
        self.__adjusted_tdee = self.__adjust_tdee_for_habits()

    def __calc_tdee(self) -> float:
        frequency_physical = self.user_data["physical_data"]["frequency_physical_activity"]
        activity_factors = {
            "none": 1.2,
            "low": 1.375,
            "moderate": 1.55,
            "high": 1.725
        }
        return self.bmr.bmr * activity_factors.get(frequency_physical, 1.2)

    def __adjust_tdee_for_habits(self) -> float:
        habits = self.user_data["physical_data"]
        adjustment_factor = 1.0
        stress_level = habits.get("stress_level", "none")
        if stress_level == "moderate":
            adjustment_factor -= 0.05
        elif stress_level == "high":
            adjustment_factor -= 0.10
        sleep_quality = habits.get("quality_of_sleep", 8.0)
        if sleep_quality < 6:
            adjustment_factor -= 0.05
        consumption = habits.get("consumption_of_alcohol_or_tobacco", "none")
        if consumption == "alcohol":
            adjustment_factor -= 0.05
        elif consumption == "tobacco":
            adjustment_factor += 0.02
        elif consumption == "both":
            adjustment_factor -= 0.03
        return max(self.__tdee * adjustment_factor, 1200)

    @property
    def tdee(self) -> float:
        return self.__adjusted_tdee

    @property
    def base_tdee(self) -> float:
        return self.__tdee
