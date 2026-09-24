"""Cash-flow scenario model using synthetic inputs."""
from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class Assumptions:
    starting_revenue: float = 1_000_000
    annual_growth: float = 0.12
    operating_margin: float = 0.18
    annual_investment: float = 45_000
    discount_rate: float = 0.11
    years: int = 5


SCENARIOS = {
    "downside": (-0.08, -0.05),
    "base": (0.00, 0.00),
    "upside": (0.05, 0.03),
}


def forecast(a: Assumptions, scenario: str) -> dict:
    if a.starting_revenue <= 0 or a.years < 1:
        raise ValueError("revenue and years must be positive")
    if not 0 <= a.operating_margin <= 1:
        raise ValueError("margin must be between zero and one")
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario}")

    growth_shift, margin_shift = SCENARIOS[scenario]
    revenue = a.starting_revenue
    rows = []
    present_value = 0.0
    for year in range(1, a.years + 1):
        revenue *= 1 + a.annual_growth + growth_shift
        profit = revenue * (a.operating_margin + margin_shift)
        cash_flow = profit - a.annual_investment
        discounted = cash_flow / ((1 + a.discount_rate) ** year)
        present_value += discounted
        rows.append({"year": year, "revenue": round(revenue, 2),
                     "cash_flow": round(cash_flow, 2),
                     "discounted_cash_flow": round(discounted, 2)})

    return {"scenario": scenario, "assumptions": asdict(a),
            "forecast": rows, "forecast_value": round(present_value, 2)}


def main() -> None:
    results = {name: forecast(Assumptions(), name) for name in SCENARIOS}
    values = [results[name]["forecast_value"] for name in SCENARIOS]
    assert values == sorted(values), "scenario ordering failed"
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
