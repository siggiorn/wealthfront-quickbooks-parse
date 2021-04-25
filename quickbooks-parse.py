import sys
import xml.etree.ElementTree as ET


def load_quickbooks_xml(path):
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


def get_transactions(root, list_names, cusipToTicker):
	def iterate_children(element, tag_base, depth, output):
		text = element.text.strip()
		key = tag_base + "_" + element.tag if len(tag_base) > 0 else element.tag
		if len(text) > 0:
			output[key] = text
			if key.endswith("SECID_UNIQUEID"):
				if text in cusipToTicker:
					output["Security Ticker"] = cusipToTicker[text]["ticker"]
					output["Security Name"] = cusipToTicker[text]["name"]
				else:
					output["Security Ticker"] = "Not found"
					output["Security Name"] = "Not found"
			if key.endswith("SECID_UNIQUEIDTYPE"):
				assert text == "CUSIP"  # Currently only handle CUSIP
		next_tag_base = key if depth > 0 else ""
		for child in element:
			iterate_children(child, next_tag_base, depth + 1, output)

	transactions_by_type = {}

	for list_name in list_names:
		for list_to_use in root.iter(list_name):
			for transaction_el in list_to_use:
				transaction_type = transaction_el.tag
				key = list_name + "_" + transaction_type 
				if key not in transactions_by_type:
					transactions_by_type[key] = []
				transaction = {}
				transactions_by_type[key].append(transaction) 
				iterate_children(transaction_el, "", 0, transaction)
	return transactions_by_type


def print_transactions(transactions_by_type):
	for transaction_type in transactions_by_type:
		print("\nType: " + transaction_type)
		transaction_list = transactions_by_type[transaction_type]
		# Find all columns for this type
		columns = set()
		for transaction in transaction_list:
			for column in transaction:
				columns.add(column)
		columns = list(columns)
		columns.sort()

		print(",".join(columns))
		for transaction in transaction_list:
			line = []
			for column in columns:
				line.append(transaction.get(column, ""))
			print(",".join(line))


# Load the XML from the quickenbooks export, which must be provided as first argument.
(root, cusipToTicker) = load_quickbooks_xml(sys.argv[1])

# Get all transactions from 
transactions = get_transactions(root, ["INVPOSLIST", "INVTRANLIST"], cusipToTicker)

print_transactions(transactions)



