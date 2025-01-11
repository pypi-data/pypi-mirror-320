from fitdata.basic_calc import BMR, TDEE, IMC
from fitdata.other_calc import CaloricAdjustment, DurationEstimator, Macros
from fitdata.weeklyprogression import WeeklyProgression
from fitdata.interfaces import UserDataEntry


class FitObjectiveData:
    """
    Class for managing and computing fitness-related objectives based on user data.

    This class integrates various calculations and validations to help users achieve
    their fitness goals, such as weight loss, weight gain, maintenance, or recomposition.
    It provides access to key metrics like BMR, TDEE, and macronutrient distributions, 
    and includes tools for caloric adjustment, duration estimation, and tracking weekly progression.

    Features:
        - Validates user data to ensure consistency and completeness.
        - Adjusts the target duration based on realistic weight goals.
        - Provides calculated properties for:
            - BMR (Basal Metabolic Rate)
            - IMC (Body Mass Index)
            - TDEE (Total Daily Energy Expenditure)
            - Caloric adjustments to achieve fitness goals.
            - Macronutrient distributions for meals.
            - Weekly progression tracking.
        - Encapsulates all fitness-related computations in a single class for simplicity.
    """

    def __init__(self, user: UserDataEntry) -> None:
        self.user = user
        self._validate_user_data()
        self.__adjust_target_duration()
        self._bmr_instance = None
        self._imc_instance = None
        self._tdee_instance = None
        self._caloric_adjustement_instance = None
        self._duration_estimator_instance = None
        self._macros_instance = None
        self._weekly_progression_instance = None

    def _validate_user_data(self) -> None:
        required_keys = ["global_data", "physical_data"]
        for key in required_keys:
            if key not in self.user:
                raise ValueError(f"User data must include '{key}'.")

    def __adjust_target_duration(self) -> None:
        global_data = self.user["global_data"]
        weight_current = global_data["weight"]
        weight_target = global_data["target_weight"]
        duration_target = global_data["target_duration"]
        objective = global_data["objective"]

        # Différence de poids (en kg)
        weight_diff = abs(weight_current - weight_target)

        # Durées minimales en fonction de l'objectif
        if objective == "weight gain":
            min_duration = int(weight_diff * 7)  # 1 kg/semaine
        elif objective == "weight loss":
            # Choix entre perte rapide (1 kg/semaine) ou modérée (0.5 kg/semaine)
            min_duration = int(weight_diff * 7)  # Pour perte rapide
            # Pour une perte modérée :
            # min_duration = int(weight_diff * 7 / 0.5)
        elif objective in ["maintenance", "recomposition"]:
            # Pas de contrainte stricte sur la durée
            min_duration = 0
        else:
            raise ValueError(f"Objectif non valide : {objective}")

        if duration_target < min_duration:
            global_data["target_duration"] = min_duration
            print(
                f"Target time adjusted to {
                    min_duration} days meet a realistic target of {weight_diff} kg."
            )

    @property
    def BMR(self) -> BMR:
        """
        Class for calculating the Basal Metabolic Rate (BMR).

        This class computes the minimum number of calories required to maintain
        basic physiological functions at rest, based on the user's age, gender,
        weight, and height.
        """
        if self._bmr_instance is None:
            self._bmr_instance = BMR(self.user)
        return self._bmr_instance

    @property
    def IMC(self) -> IMC:
        """
        Class for calculating the Body Mass Index (BMI) and determining the corresponding category.

        This class evaluates whether the user's weight is within a healthy range
        based on the BMI formula (weight divided by height squared).
        """
        if self._imc_instance is None:
            self._imc_instance = IMC(self.user)
        return self._imc_instance

    @property
    def TDEE(self) -> TDEE:
        """
        Class for calculating the Total Daily Energy Expenditure (TDEE).

        This class estimates the total number of calories burned per day, including
        both resting and activity-based energy expenditure.
        """
        if self._tdee_instance is None:
            self._tdee_instance = TDEE(self.user)
        return self._tdee_instance

    @property
    def CaloricAdjustment(self) -> CaloricAdjustment:
        """
        Class for calculating the daily caloric adjustment needed to achieve a fitness goal.

        This class computes the required daily caloric deficit or surplus based on
        the user's current weight, target weight, and target duration. It also calculates
        the target daily caloric intake to meet the specified fitness objective.
        """
        if self._caloric_adjustement_instance is None:
            self._caloric_adjustement_instance = CaloricAdjustment(self.user)
        return self._caloric_adjustement_instance

    @property
    def DurationEstimator(self) -> DurationEstimator:
        """
        Class for estimating the duration required to achieve a weight-related fitness goal.

        Based on the user's current weight, target weight, and daily caloric adjustment,
        this class calculates the estimated number of days needed to reach the specified goal.
        """
        if self._duration_estimator_instance is None:
            self._duration_estimator_instance = DurationEstimator(self.user)
        return self._duration_estimator_instance

    @property
    def Macros(self) -> Macros:
        """
        Class for calculating and distributing macronutrient requirements.

        This class computes the amount of protein, carbohydrates, fat, fibers, and sugars
        based on the user's caloric target and fitness objective. It also distributes these
        macronutrients across meals (breakfast, lunch, snack, dinner) according to predefined ratios.
        """
        if self._macros_instance is None:
            self._macros_instance = Macros(self.user)
        return self._macros_instance

    @property
    def WeeklyProgression(self) -> WeeklyProgression:
        """
        Class for calculating the user's weekly progression based on caloric adjustment.

        This class estimates how much weight the user is expected to gain or lose weekly
        based on their daily caloric adjustment. It provides warnings for unsafe progression rates.
        """
        if self._weekly_progression_instance is None:
            self._weekly_progression_instance = WeeklyProgression(self.user)
        return self._weekly_progression_instance
