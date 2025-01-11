from typing import TypedDict, Literal


class GlobalDataEntry(TypedDict):
    """
    Represents the global data for a user.

    Attributes:
        age (int): The user's age in years.
        gender (Literal["male", "female"]): The user's gender.
        height (float): The user's height in centimeters (high precision).
        weight (int): The user's current weight in kilograms.
        objective (Literal["weight gain", "weight loss", "maintenance", "recomposition"]): 
            The user's fitness objective.
        target_weight (int): The user's target weight in kilograms 
            (optional for "maintenance").
        target_duration (int): The target duration to reach the goal, in days 
            (optional for "maintenance").
    """
    age: int
    gender: Literal["male", "female"]
    height: float  # en cm (précision accrue)
    weight: int  # en kg
    objective: Literal["weight gain", "weight loss",
                       "maintenance", "recomposition"]
    target_weight: int  # en kg (facultatif pour "maintenance")
    # en nombre de jours (facultatif pour "maintenance")
    target_duration: int


class DailyPhysicalActivityData(TypedDict):
    """
    Represents the daily physical activity data for a user.

    Attributes:
        frequency_physical_activity (Literal["none", "low", "moderate", "high"]): 
            The frequency of physical activity.
        activity_type (Literal["cardio", "musculation", "yoga", "cycling", "swimming", "other"]): 
            The type of physical activity performed.
        quality_of_sleep (float): The quality of sleep, measured in hours per day.
        stress_level (Literal["none", "low", "moderate", "high"]): The user's stress level.
        consumption_of_alcohol_or_tobacco (Literal["none", "alcohol", "tobacco", "both"]): 
            The user's consumption of alcohol and/or tobacco.
    """
    frequency_physical_activity: Literal["none", "low", "moderate", "high"]
    activity_type: Literal[
        "cardio", "musculation", "yoga", "cycling", "swimming", "other"
    ]
    quality_of_sleep: float  # en heures/jour
    stress_level: Literal["none", "low", "moderate", "high"]
    consumption_of_alcohol_or_tobacco: Literal["none",
                                               "alcohol", "tobacco", "both"]


class UserDataEntry(TypedDict):
    """
    Combines the user's global data and daily physical activity data.

    Attributes:
        global_data (GlobalDataEntry): The user's global data (age, weight, etc.).
        physical_data (DailyPhysicalActivityData): The user's daily physical activity data.
    """
    global_data: GlobalDataEntry
    physical_data: DailyPhysicalActivityData


class MacrosData(TypedDict):
    """
    Represents the macronutrient breakdown for a user.

    Attributes:
        protein (float): Protein content in grams.
        carbs (float): Carbohydrates content in grams.
        fat (float): Fat content in grams.
        fibers (float): Fiber content in grams.
        sugars (float): Sugar content in grams.
    """
    protein: float
    carbs: float
    fat: float
    fibers: float
    sugars: float


class MealMacros(TypedDict):
    """
    Represents the macronutrient breakdown for each meal.

    Attributes:
        breakfast (MacrosData): Macronutrients for breakfast.
        lunch (MacrosData): Macronutrients for lunch.
        snack (MacrosData): Macronutrients for snacks.
        dinner (MacrosData): Macronutrients for dinner.
    """
    breakfast: MacrosData
    lunch: MacrosData
    snack: MacrosData
    dinner: MacrosData
