from pint import UnitRegistry, UndefinedUnitError

ureg = UnitRegistry()

# Kimya mühendisliğinde sık kullanılan birimler
UNIT_CATEGORIES = {
    "Uzunluk": [
        "meter", "centimeter", "millimeter", "kilometer", "inch", "foot", "yard", "mile", "nautical_mile", "angstrom", "micrometer", "nanometer"
    ],
    "Alan": [
        "meter**2", "centimeter**2", "millimeter**2", "kilometer**2", "inch**2", "foot**2", "yard**2", "mile**2", "acre", "hectare"
    ],
    "Hacim": [
        "meter**3", "liter", "milliliter", "microliter", "centimeter**3", "millimeter**3", "inch**3", "foot**3", "yard**3", "gallon", "quart", "pint", "cup"
    ],
    "Kütle": [
        "kilogram", "gram", "milligram", "microgram", "ton", "tonne", "pound", "ounce", "stone", "carat"
    ],
    "Sıcaklık": [
        "kelvin", "celsius", "fahrenheit", "rankine"
    ],
    "Basınç": [
        "pascal", "kilopascal", "megapascal", "bar", "psi", "atm", "torr", "mmHg"
    ],
    "Enerji": [
        "joule", "kilojoule", "calorie", "kilocalorie", "btu", "erg"
    ],
    "Güç": [
        "watt", "kilowatt", "megawatt", "horsepower"
    ],
    "Yoğunluk": [
        "kilogram/meter**3", "gram/centimeter**3", "pound/foot**3"
    ],
    "Hız": [
        "meter/second", "kilometer/hour", "foot/second", "mile/hour", "knot"
    ],
    "Viskozite (Dinamik)": [
        "pascal*second", "poise", "centipoise", "pound/(foot*second)"
    ],
}

# Arayüzdeki birimleri pint'in kısa adlarına eşleyen sözlük (tüm anahtarlar küçük harfli)
UNIT_ALIASES = {
    "meter": "m",
    "centimeter": "cm",
    "millimeter": "mm",
    "kilometer": "km",
    "micrometer": "um",
    "nanometer": "nm",
    "inch": "in",
    "foot": "ft",
    "yard": "yd",
    "mile": "mi",
    "nautical_mile": "nmi",
    "angstrom": "angstrom",
    "meter**2": "m**2",
    "centimeter**2": "cm**2",
    "millimeter**2": "mm**2",
    "kilometer**2": "km**2",
    "inch**2": "in**2",
    "foot**2": "ft**2",
    "yard**2": "yd**2",
    "mile**2": "mi**2",
    "acre": "acre",
    "hectare": "hectare",
    "meter**3": "m**3",
    "centimeter**3": "cm**3",
    "millimeter**3": "mm**3",
    "inch**3": "in**3",
    "foot**3": "ft**3",
    "yard**3": "yd**3",
    "liter": "L",
    "milliliter": "mL",
    "microliter": "uL",
    "gallon": "gal",
    "quart": "qt",
    "pint": "pt",
    "cup": "cup",
    "kilogram": "kg",
    "gram": "g",
    "milligram": "mg",
    "microgram": "ug",
    "ton": "ton",
    "tonne": "tonne",
    "pound": "lb",
    "ounce": "oz",
    "stone": "stone",
    "carat": "carat",
    "kelvin": "K",
    "celsius": "degC",
    "fahrenheit": "degF",
    "rankine": "degR",
    "pascal": "Pa",
    "kilopascal": "kPa",
    "megapascal": "MPa",
    "bar": "bar",
    "psi": "psi",
    "atm": "atm",
    "torr": "torr",
    "mmhg": "mmHg",
    "joule": "J",
    "kilojoule": "kJ",
    "calorie": "cal",
    "kilocalorie": "kcal",
    "btu": "BTU",
    "erg": "erg",
    "watt": "W",
    "kilowatt": "kW",
    "megawatt": "MW",
    "horsepower": "hp",
    "kilogram/meter**3": "kg/m**3",
    "gram/centimeter**3": "g/cm**3",
    "pound/foot**3": "lb/ft**3",
    "meter/second": "m/s",
    "kilometer/hour": "km/h",
    "foot/second": "ft/s",
    "mile/hour": "mi/h",
    "knot": "knot",
    "pascal*second": "Pa*s",
    "poise": "P",
    "centipoise": "cP",
    "pound/(foot*second)": "lb/(ft*s)",
}

def get_compatible_units(quantity_type):
    """Verilen nicelik türü için birim listesini döndürür."""
    return UNIT_CATEGORIES.get(quantity_type, [])

def convert_units(value, from_unit, to_unit):
    """Verilen değerleri birimler arasında çevirir."""
    from_unit_norm = from_unit.strip().lower()
    to_unit_norm = to_unit.strip().lower()
    from_unit_eng = UNIT_ALIASES.get(from_unit_norm, from_unit_norm)
    to_unit_eng = UNIT_ALIASES.get(to_unit_norm, to_unit_norm)
    print(f"[DEBUG] value: {value}, from_unit: '{from_unit}' -> '{from_unit_eng}', to_unit: '{to_unit}' -> '{to_unit_eng}'")
    try:
        val = value * ureg(from_unit_eng)
        result = val.to(to_unit_eng)
        return result.magnitude, None
    except Exception as e:
        # Daha detaylı bir hata mesajı döndür
        return None, f"Pint Kütüphanesi Hatası: {type(e).__name__} - {e}"
