
import pandas as pd
import us
from kerykeion import AstrologicalSubject

# Read in birthdays.
db = pd.read_csv("data/birthdays.all.csv")

# Read in location information.
locations = pd.read_csv("data/capitals.csv").set_index("STATE").to_dict(orient="index")
db["LAT"] = db["STATE"].apply(lambda s: locations[s]["LAT"])
db["LNG"] = db["STATE"].apply(lambda s: locations[s]["LNG"])

def tz(s):
	lookup = us.states.lookup(s)
	return lookup.capital_tz if lookup else "America/New_York"


db["TZ"] = db["STATE"].apply(tz)

def astrology(r):
	m, d, y = [int(t) for t in r["BORN"].split("/")]
	astro = AstrologicalSubject(f"{r['LAST']}, {r['FIRST']}", y, m, d, 0, 0, lat=r["LAT"], lng=r["LNG"], tz_str=r["TZ"], online=False)

	r["SUNSIGN"] = astro.sun.sign
	r["SUNELEMENT"] = astro.sun.element
	r["SUNHOUSE"] = astro.sun.house.replace("_", " ")
	r["SUNRETROGRADE"] = 0 if astro.sun.retrograde == "False" else 1

	r["MOONSIGN"] = astro.moon.sign
	r["MOONELEMENT"] = astro.moon.element
	r["MOONHOUSE"] = astro.moon.house.replace("_", " ")
	r["MOONRETROGRADE"] = 0 if astro.moon.retrograde == "False" else 1

	return r

db = db.apply(astrology, axis=1)
db = db.drop(["LOC", "CITY", "STATE", "LAT", "LNG", "TZ"], axis=1)
db.to_csv("data/astrological.csv", index=False)

