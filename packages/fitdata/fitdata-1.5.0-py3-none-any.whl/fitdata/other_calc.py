
from fitdata.interfaces import UserDataEntry, MacrosData, MealMacros
from fitdata.basic_calc import TDEE
from typing import Dict


class CaloricAdjustment:
    """
    Class for calculating the daily caloric adjustment needed to achieve a fitness goal.

    This class computes the required daily caloric deficit or surplus based on
    the user's current weight, target weight, and target duration. It also calculates
    the target daily caloric intake to meet the specified fitness objective.
    """

    def __init__(self, user: UserDataEntry) -> None:
        self.user_data = user
        self.tdee = TDEE(self.user_data)
        self.__adjustment = self.__calc_adjustment()
        self.__target_calories = self.__calc_calories_target()

    def __calc_adjustment(self) -> float:
        global_data = self.user_data['global_data']
        weight_current = global_data['weight']
        weight_target = global_data["target_weight"]
        duration_target = global_data["target_duration"]
        if duration_target <= 0:
            raise ValueError("Target duration must be a positive integer.")
        # Différence de poids (en kg)
        weight_diff = abs(weight_current - weight_target)
        # Calories totales nécessaires (7700 kcal par kg)
        total_calories = weight_diff * 7700
        return total_calories / duration_target

    def __calc_calories_target(self) -> float:
        objective = self.user_data['global_data']['objective']

        if objective == "weight loss":
            return self.tdee.tdee - self.__adjustment
        elif objective == "weight gain":
            return self.tdee.tdee + self.__adjustment
        elif objective == "maintenance":
            return self.tdee.tdee
        elif objective == "recomposition":
            return self.tdee.tdee - 250  # Ajustement léger pour recomposition
        else:
            raise ValueError(
                f"Invalid objective '{
                    objective}'. Valid options are: ['weight loss', 'weight gain', 'maintenance', 'recomposition']"
            )

    @property
    def adjustment(self) -> float:
        return self.__adjustment

    @property
    def calories_target(self) -> float:
        return self.__target_calories

    @property
    def tdee_value(self) -> float:
        return self.tdee.tdee


class DurationEstimator:
    """
    Class for estimating the duration required to achieve a weight-related fitness goal.

    Based on the user's current weight, target weight, and daily caloric adjustment,
    this class calculates the estimated number of days needed to reach the specified goal.
    """

    def __init__(self, user: UserDataEntry) -> None:
        self.user_data = user
        self.caloric_adjustment = CaloricAdjustment(self.user_data)

    def __calc_duration(self) -> float:
        global_data = self.user_data["global_data"]

        if global_data["objective"] == "maintenance":
            raise ValueError(
                "Duration estimation is not applicable for maintenance objective.")

        weight_current = global_data["weight"]
        weight_target = global_data["target_weight"]

        # Différence de poids en kg
        weight_diff = abs(weight_current - weight_target)

        # Calories totales nécessaires (7700 kcal par kg)
        total_calories = weight_diff * 7700

        # Ajustement calorique quotidien
        adjustment_caloric = self.caloric_adjustment.adjustment

        if adjustment_caloric == 0:
            raise ValueError("Caloric adjustment cannot be zero")

        # Durée estimée en jours
        return total_calories / adjustment_caloric

    @property
    def duration(self) -> float:
        return self.__calc_duration()


class Macros:
    """
    Class for calculating and distributing macronutrient requirements.

    This class computes the amount of protein, carbohydrates, fat, fibers, and sugars
    based on the user's caloric target and fitness objective. It also distributes these
    macronutrients across meals (breakfast, lunch, snack, dinner) according to predefined ratios.
    """

    def __init__(self, user: UserDataEntry) -> None:
        self.user_data = user
        self.caloric_adjustment = CaloricAdjustment(self.user_data)
        self.RATIOS: Dict[str, Dict[str, float]] = {
            "weight loss": {"protein": 0.35, "carbs": 0.35, "fat": 0.3, "fibers": 0.05, "sugars": 0.15},
            "weight gain": {"protein": 0.30, "carbs": 0.50, "fat": 0.20, "fibers": 0.04, "sugars": 0.20},
            "maintenance": {"protein": 0.30, "carbs": 0.40, "fat": 0.30, "fibers": 0.05, "sugars": 0.10},
            "recomposition": {"protein": 0.40, "carbs": 0.30, "fat": 0.30, "fibers": 0.05, "sugars": 0.10},
        }
        self.MEAL_RATIO: MealMacros = {
            "breakfast": 0.25,
            "lunch": 0.35,
            "snack": 0.15,
            "dinner": 0.25
        }
        self.__macros = self.__calc_macros()
        self.__meal_macros = self.__distribute_macros()

    def get_ratios(self) -> Dict[str, float]:
        objective = self.user_data["global_data"]["objective"]
        activity_type = self.user_data["physical_data"]["activity_type"]

        ratios = self.RATIOS.get(
            objective, {"protein": 0.30, "carbs": 0.40,
                        "fat": 0.30, "fibers": 0.05, "sugars": 0.10}
        )

        # Ajustements pour le type d'activité
        if activity_type == "musculation":
            ratios["protein"] += 0.05
            ratios["carbs"] -= 0.05
        elif activity_type == "cardio":
            ratios["carbs"] += 0.10
            ratios["fat"] -= 0.05

        # Validation pour éviter des ratios négatifs
        if any(value < 0 for value in ratios.values()):
            raise ValueError(
                "Ratios invalid: resulting ratios contain negative values.")

        # Assurer que les ratios (hors fibres et sucres) restent valides (somme == 1.0)
        total_ratio = sum(ratios[key] for key in ["protein", "carbs", "fat"])
        if abs(total_ratio - 1.0) > 1e-6:
            raise ValueError(
                "Ratios must sum to 1.0 for protein, carbs, and fat.")

        return ratios

    def __calc_macros(self) -> MacrosData:
        objective = self.user_data["global_data"]["objective"]

        if objective not in self.RATIOS:
            raise ValueError(f"Invalid objective '{objective}'")

        ratio = self.get_ratios()
        calories_target = self.caloric_adjustment.calories_target

        # Calcul des calories pour chaque macronutriment
        protein_calories = calories_target * ratio["protein"]
        carbs_calories = calories_target * ratio["carbs"]
        fat_calories = calories_target * ratio["fat"]

        # Conversion des calories en grammes
        protein_grams = protein_calories / 4
        carbs_grams = carbs_calories / 4
        fat_grams = fat_calories / 9

        # Ajout des fibres et sucres (en grammes, basés sur leur ratio sur les calories totales)
        # Fibers: 2 kcal/g
        fiber_grams = (calories_target * ratio["fibers"]) / 2
        # Sugars: 4 kcal/g
        sugar_grams = (calories_target * ratio["sugars"]) / 4

        return {
            "protein": round(protein_grams, 2),
            "carbs": round(carbs_grams, 2),
            "fat": round(fat_grams, 2),
            "fibers": round(fiber_grams, 2),
            "sugars": round(sugar_grams, 2)
        }

    def __distribute_macros(self) -> MealMacros:
        distributed_macros: MealMacros = {}
        for meal, ratio in self.MEAL_RATIO.items():
            distributed_macros[meal] = {
                "protein": round(self.__macros["protein"] * ratio, 2),
                "carbs": round(self.__macros["carbs"] * ratio, 2),
                "fat": round(self.__macros["fat"] * ratio, 2),
                "fibers": round(self.__macros["fibers"] * ratio, 2),
                "sugars": round(self.__macros["sugars"] * ratio, 2),
            }
        return distributed_macros

    @property
    def macros(self) -> MacrosData:
        return self.__macros

    @property
    def meal_macros(self) -> MealMacros:
        return self.__meal_macros
