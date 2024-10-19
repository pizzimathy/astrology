
import string
import pandas as pd
import us

# Read in all the CSVs of names/birthdays by letter.
names = [f"data/alphabet/{l}.csv" for l in string.ascii_uppercase]
files = [pd.read_csv(f) for f in names]

# Concatenate the tables, dropping duplicates (if necessary; though this seems to
# have mixed effects). Match location names to capitals, if possible. Write to
# file.
db = pd.concat(files).drop_duplicates()

bad = {
	"N ": "ND",
	"NI": "SC",
	"TE": "TN",
	"(N": "VA",
}

bad.update({str(state.abbr): str(state.abbr) for state in us.states.STATES})

db["STATE"] = db["LOC"].map(bad)
db["CITY"] = db["STATE"].map({state.abbr: state.capital for state in us.states.STATES})

db["STATE"] = db["STATE"].fillna("DC")
db["CITY"] = db["CITY"].fillna("Washington")

db.to_csv("data/birthdays.all.csv", index=False)
