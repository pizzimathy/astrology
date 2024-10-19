
import string
import xmltodict
import datefinder
import pandas as pd
from selenium import webdriver


# Create URLs.
root = "https://bioguideretro.congress.gov/Static_Files/data/"
sources = {
	letter: [
		root + f"{letter}/{letter}" + f"{n}".zfill(6) + ".xml"
		for n in range(1, 10000)
	]
	for letter in string.ascii_uppercase
}

for letter, urls in list(sources.items()):
	# Keep track of how many times we attempt to access ascending URLs; once we
	# pass some ceiling, we stop trying (i.e. assume there are no records with
	# greater numerical identifiers).
	tries = 0
	ceiling = 20
	timeout = 20
	old = None

	# Create the Selenium driver to access webpages.
	options = webdriver.FirefoxOptions()
	options.add_argument("-headless")
	options.page_load_strategy = "eager"

	dr = webdriver.Firefox(options=options)
	dr.set_page_load_timeout(timeout)

	# Re-set records.
	records = {}
	
	for url in urls:
		uid = url[-11:-4]

		# The first layer is to check whether there's an issue with Selenium. If
		# we can't parse the page's XML, we've either been detected as a robot
		# OR the page doesn't exist.
		try:
			dr.get(url)
			info = xmltodict.parse(dr.page_source)
		except:
			# If we've been detected as a robot, Cloudflare issues a "challenge"
			# to prove we're human. To detect this, we check whether the phrase
			# "challenge" appears in the page source (this assumes it does not
			# appear anywhere in the biographical text) and re-instantiate the
			# web driver. Once we pass the "challenge," we try parsing again;
			# if we can't parse, then the info from the last functional URL persists
			# in `info`.
			while "challenge" in dr.page_source:
				dr.quit()
				dr = webdriver.Firefox(options=options)
				dr.set_page_load_timeout(timeout)
				dr.get(url)

				try: info = xmltodict.parse(dr.page_source)
				except: continue

		# If we have accessed some number of URLs without an update to the
		# biographical information, we break and start on the next letter.
		if old == info:
			tries += 1

			if tries > ceiling: break
			else: continue
		
		# Print the URL just because; mostly for debugging, but also cool to see
		# the windows fly by.
		print(url)

		# Extract "personal information."
		personal = info["uscongress-bio"]["personal-info"]

		# Another series of awful try-excepts, this time designed to catch the
		# idiosyncrasies in the formatting of personal information. For whatever
		# reason, the data is stored in the DB as JSON (?) so anything in a rich
		# text format shows up as a dictionary.
		try:
			# Try to split on semicolons (since the entries are formatted to
			# separate important biographical facts by semicolon instead of a
			# list), and access the second element, which contains the birthday
			# information (replacing newlines with spaces).
			localToBirthday = info["uscongress-bio"]["biography"].split(";")[1].replace("\n"," ")
		except:
			try:
				# If that doesn't work, we look for an HTML paragraph marker.
				localToBirthday = info["uscongress-bio"]["biography"]["p"].split(";")[1].replace("\n"," ")
			except:
				try:
					# If THAT doesn't work, we look for a "#text" HTML identifier.
					localToBirthday = info["uscongress-bio"]["biography"]["#text"].split(";")[1].replace("\n"," ")
				except:
					# If none of the above work, we just move on; there are too
					# many cases for us to deal with effectively.
					continue

		try: loc = localToBirthday.split(",")[-3].replace(".","").strip()[:2].upper()
		except: loc = None
		
		# Use a handy-dandy library to detect dates within the strings we find.
		# If there are no matches, move on.
		matches = datefinder.find_dates(localToBirthday)

		try: bd = list(matches)[0]
		except: continue

		# Get the name of the Congressperson and the Congresses in which they
		# served; this is formatted differently depending on whether they served
		# one or more terms. BE CONSISTENT, PEOPLE!
		last, first = personal["name"]["lastname"].lower().capitalize(), personal["name"]["firstnames"]
		name = f"{last}, {first}"
		congresses = [t["congress-number"] for t in personal["term"]] if type(personal["term"]) is list else [personal["term"]["congress-number"]]
		
		# Get their party.
		if type(personal["term"]) is list: tp = personal["term"][-1]["term-party"]
		else: tp = personal["term"]["term-party"]
		party = tp[0] if tp else "I"

		# Construct a database record.
		record = {
			"UID": uid,
			"FIRST": first,
			"LAST": last,
			"BORN": bd.strftime('%m/%d/%Y'),
			"CONGRESSES": "-".join(congresses),
			"PARTY": party,
			"LOC": loc
		}

		# Add the record as a UID (so we don't accidentally get multiple copies
		# of someone) and reassign info.
		records[uid] = record
		old = info
	
	# Kill the driver and be done.
	dr.quit()

	# Write to file. Split up the job so we know when things fail (if they do).
	listified = list(records.values())
	pd.DataFrame() \
		.from_records(listified) \
		.drop_duplicates() \
		.to_csv(f"data/alphabet/{letter}.csv", index=False)
