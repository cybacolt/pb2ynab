import os
import csv23
from jinja2 import Environment, FileSystemLoader

environment = Environment(loader = FileSystemLoader("templates/"))
template = environment.get_template("transactions.template")

if not os.path.exists('transactions'):
	os.mkdir('transactions')

def loadCSV(file, header = False):
	output = {} if not header else []
	with csv23.open_csv(file) as reader:
		for row in reader:
			if header:
				if reader.line_num == 1:
					h = row
					continue
				buffer = {}
				for v in h:
					buffer[v] = row[h.index(v)]
				output.append(buffer)
			else:
				output[row[0]] = row[1]
	return output

# get all the things
ynab_categories = loadCSV('ynab-categories.csv')
category_map = loadCSV('category-mapping.csv')
account_map = loadCSV('account-mapping.csv')
ynab_categories = loadCSV('ynab-categories.csv')
transactions_raw = loadCSV('pocketbook-export.csv', True)

# sort transactions into dates and map all the things
transactions_by_date = {}
for row in transactions_raw:
	day, month, year = row['date'].split('/')

	if not row['accountnumber']:
		row['accountnumber'] = next(iter(account_map))

	transaction = {
		"date": f"{year}-{month}-{day}",
		"description": row['description'],
		"category": ynab_categories[category_map[row['category']]],
		"amount": int(float(row['amount'].strip(' "'))*1000),
		"notes": row['notes'],
		"tags": row['tags'],
		"bank": row['bank'],
		"accountname": row['accountname'],
		"account": account_map[row['accountnumber']]
	}
	if transaction["date"] not in transactions_by_date:
		transactions_by_date[transaction["date"]] = []

	transactions_by_date[transaction["date"]].append(transaction)

# render template out to files
for date, transactions in transactions_by_date.items():
    filename = f"transactions/{date}.json"
    content = template.render({"transactions":transactions})
    with open(filename, mode = "w", encoding = "utf-8") as message:
        message.write(content)
    print(f"{filename}")

