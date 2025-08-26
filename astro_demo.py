# astro_demo.py
# Minimal VedAstro demo (Spyder/IDLE friendly)

import json
from vedastro import GeoLocation, Time, Calculate, PlanetName, HouseName, ZodiacName

def compute_bundle(datetime_str, tz_offset, place_name, longitude_deg, latitude_deg):
    """Compute planet, house, and zodiac data using VedAstro."""

    # Build time & location
    geo = GeoLocation(place_name, float(longitude_deg), float(latitude_deg))
    t = Time(f"{datetime_str} {tz_offset}", geo)

    # --- Planet data ---
    planet_list = [
        PlanetName.Sun, PlanetName.Moon, PlanetName.Mars, PlanetName.Mercury,
        PlanetName.Jupiter, PlanetName.Venus, PlanetName.Saturn,
        PlanetName.Rahu, PlanetName.Ketu
    ]
    planets = {str(p): Calculate.AllPlanetData(p, t) for p in planet_list}

    # --- Houses ---
    house_list = [
        HouseName.House1, HouseName.House2, HouseName.House3, HouseName.House4,
        HouseName.House5, HouseName.House6, HouseName.House7, HouseName.House8,
        HouseName.House9, HouseName.House10, HouseName.House11, HouseName.House12
    ]
    houses = {str(h): Calculate.AllHouseData(h, t) for h in house_list}

    # --- Zodiacs ---
    zodiac_list = [
        ZodiacName.Aries, ZodiacName.Taurus, ZodiacName.Gemini, ZodiacName.Cancer,
        ZodiacName.Leo, ZodiacName.Virgo, ZodiacName.Libra, ZodiacName.Scorpio,
        ZodiacName.Sagittarius, ZodiacName.Capricorn, ZodiacName.Aquarius, ZodiacName.Pisces
    ]
    zodiacs = {str(z): Calculate.AllZodiacSignData(z, t) for z in zodiac_list}

    return {
        "input": {
            "datetime_local": f"{datetime_str} {tz_offset}",
            "place": place_name,
            "longitude": longitude_deg,
            "latitude": latitude_deg,
        },
        "planets": planets,
        "houses": houses,
        "zodiacs": zodiacs,
    }

# --------------------------
# ✨ Edit these values ✨
datetime_str = "19:15 15/08/2001"   # time & date
tz_offset = "+05:30"                # timezone
place_name = "New Delhi, India"     # location
longitude_deg = 77.2090
latitude_deg = 28.6139
# --------------------------

# Run computation
bundle = compute_bundle(datetime_str, tz_offset, place_name, longitude_deg, latitude_deg)

# Pretty print JSON
print(json.dumps(bundle, indent=2))
