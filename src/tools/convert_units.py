from agents import function_tool

CONVERSION_TABLE: dict[str, float] = {
    "km→miles": 0.621371,
    "miles→km": 1.60934,
    "kg→lbs": 2.20462,
    "lbs→kg": 0.453592,
    "meters→feet": 3.28084,
    "feet→meters": 0.3048,
    "liters→gallons": 0.264172,
    "gallons→liters": 3.78541,
}

@function_tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a numeric value from one unit to another.

    Use EXACTLY these unit strings (case-insensitive):
      km      ↔  miles
      kg      ↔  lbs
      meters  ↔  feet
      liters  ↔  gallons

    Examples:
      convert_units(120, "km", "miles")   -> "120 km = 74.5645 miles"
      convert_units(70,  "lbs", "kg")     -> "70 lbs = 31.7514 kg"
    """
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    factor = CONVERSION_TABLE.get(f"{from_unit}→{to_unit}")
    if factor is None:
        return f"Sorry, I don't know how to convert {from_unit} → {to_unit}."

    return f"{value} {from_unit} = {value * factor:.4f} {to_unit}"
