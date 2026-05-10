def estimate_salary(salary: dict, seniority_score: float) -> dict:
    min_salary = salary["min"]
    max_salary = salary["max"]
    salary_range = max_salary - min_salary

    position_in_range = seniority_score / 100
    estimated = min_salary + (salary_range * position_in_range)

    estimated_min = round(estimated * 0.9 / 1000) * 1000
    estimated_max = round(estimated * 1.1 / 1000) * 1000

    return {
        "estimated_min": estimated_min,
        "estimated_max": estimated_max,
        "currency": salary["currency"],
        "market_min": min_salary,
        "market_max": max_salary,
    }