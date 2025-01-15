def calculate_fullness_factor(calorie: float, protein: float, fiber: float, fat: float):
    ff= 41.7/(calorie**0.7) + 0.05*protein + 0.000617*(fiber**3)-0.00000725*(fat**3)
    return max(0.5, min(5, ff))