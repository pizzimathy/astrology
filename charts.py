
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gerrytools.plotting import latex

congress = "42"

db = pd.read_csv("data/astrological.csv")
current = db[db["CONGRESSES"].str.contains(congress)]

R = current[current["PARTY"] == "R"]
D = current[current["PARTY"] == "D"]

# Create sign-based bar chart.
def signsByPercentage(columns=["SUNSIGN", "MOONSIGN"]):
	for column in columns:
		_, axes = plt.subplots(2, layout="tight")
		r, d = axes
		
		normalR = (R.value_counts(column)/len(R)).sort_index()
		normalD = (D.value_counts(column)/len(D)).sort_index()

		# Get the max of the normalized values to effectively compare.
		tallest = max(list(normalR) + list(normalD))

		normalR.plot.bar(ax=r, facecolor=latex["Boston University Red"])
		normalD.plot.bar(ax=d, facecolor=latex["Brandeis blue"])

		for ax in axes:
			ticks = list(np.linspace(0, tallest, 4))
			ax.set_ylim(0, round(tallest+0.005, 3))

			ax.set_yticks(ticks)
			ax.set_yticklabels([rf"{int(t*100)}%" for t in ticks])

			ax.set_ylabel(r"% of delegation")
			ax.set_xlabel("")

		plt.savefig(f"figures/{congress}-{column}-delegation%.jpeg", dpi=300, bbox_inches="tight")


# Create sign-based bar chart.
def signsByVolume(columns=["SUNSIGN", "MOONSIGN"]):
	for column in columns:
		_, axes = plt.subplots(2, layout="tight")
		r, d = axes

		normalR = (R.value_counts(column)).sort_index()
		normalD = (D.value_counts(column)).sort_index()

		# Get the max of the normalized values to effectively compare.
		tallest = max(list(normalR) + list(normalD))

		normalR.plot.bar(ax=r, facecolor=latex["Boston University Red"])
		normalD.plot.bar(ax=d, facecolor=latex["Brandeis blue"])

		for ax in axes:
			ax.set_ylim(0,(round(tallest/10)+1)*10)
			ax.set_ylabel(r"# of delegates")
			ax.set_xlabel("")

		plt.savefig(f"figures/{congress}-{column}-delegation#.jpeg", dpi=300, bbox_inches="tight")


# Create sign-based bar chart.
def pie(columns=["SUNSIGN", "MOONSIGN"]):
	for column in columns:
		_, axes = plt.subplots(2, layout="tight")
		r, d = axes

		normalR = (R.value_counts(column)).sort_index()
		normalD = (D.value_counts(column)).sort_index()

		normalR.plot.pie(ax=r)
		normalD.plot.pie(ax=d)

		r.set_ylabel("R")
		d.set_ylabel("D")

		plt.savefig(f"figures/{column}-pie-delegation#.jpeg", dpi=300, bbox_inches="tight")

signsByPercentage()
signsByVolume()
pie()
