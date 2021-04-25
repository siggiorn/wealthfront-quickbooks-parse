import sys
import xml.etree.ElementTree as ET

def load_quicken_xml(path):
	with open(path, 'r') as file:
		data = file.readlines()
		# Assuming the XML starts at line 11
		text = "".join(data[10:])
		root = ET.fromstring(text)

		# Map CUSIP id to ticker
		cusipToTicker = {}
		for secinfo in root.iter("SECINFO"):	
			uniqueid = secinfo.findall("SECID/UNIQUEID")[0].text
			uniqueid_type = secinfo.findall("SECID/UNIQUEIDTYPE")[0].text
			assert uniqueid_type == "CUSIP"
			cusipToTicker[uniqueid] = { 
				"name": secinfo.findall("SECNAME")[0].text, 
				"ticker": secinfo.findall("TICKER")[0].text
			}
		return (root, cusipToTicker)

# Get all current holdings
def get_holdings(root, cusipToTicker):
	holdings = []
	for posstock in root.iter("POSSTOCK"):	
		uniqueid = posstock.findall("INVPOS/SECID/UNIQUEID")[0].text
		uniqueid_type = posstock.findall("INVPOS/SECID/UNIQUEIDTYPE")[0].text
		assert uniqueid_type == "CUSIP"
		ticker = cusipToTicker[uniqueid]["ticker"]
		name = cusipToTicker[uniqueid]["name"]
		units = posstock.findall("INVPOS/UNITS")[0].text
		unitprice = posstock.findall("INVPOS/UNITPRICE")[0].text
		holdings.append({ "name": name, "ticker": ticker, "units": units, "unitprice": unitprice })
	return holdings

def print_holdings_csv(holdings):
	print("name, ticker, units, unitprice")
	for holding in holdings:
		print(holding["name"], ", ", holding["ticker"], ", ", holding["units"], ", ", holding["unitprice"])

# Load the XML from the quickenbooks export, which must be provided as first argument.
(root, cusipToTicker) = load_quicken_xml(sys.argv[1])

# Find the holdings
holdings = get_holdings(root, cusipToTicker)

# Print the holdings as CSV
print_holdings_csv(holdings)




