# pb2ynab
Pocketbook to YNAB Converter

This converts pocketbook exports to You Need A Budget (YNAB) transactions.

## Requirements
- Python 3.9

For extraction:
- ynab.sh + send-transactions.sh (https://github.com/cybacolt/ynab)
- jq
- csvkit
- sed

## Setup

Install the required python packages:
```
pip install -r requirements.txt
apt-get install csvkit jq sed
```

## Conversion Process
1. Place `pocketbook-export.csv` in the same folder as `pn2ynab.py`

2. Extract pocketbook categories from your export file: (memos and tags columns removed to facilitate parsing)
```
csvcut -C 5,6 pocketbook-export.csv > pocketbook-export-clean.csv
cat pocketbook-export-clean.csv | cut -d',' -f3 | sort | uniq 
```

3. Extract pocketbook accounts from your export file: 
```
cat pocketbook-export-clean.csv | cut -d',' -f7 | sort | uniq 
```

4. Get categories and sub-categories from the YNAB API to `ynab-categories.csv`:
```
./ynab.sh last-used categories | jq '.data.category_groups[] | "\(.name)##\(.id)"' | sed -e 's/##/","/' > ynab-categories.csv
./ynab.sh last-used categories | jq '.data.category_groups[].categories[] | "\(.name)##\(.id)"' | sed -e 's/##/","/' >> ynab-categories.csv
```

5. Get accounts from the YNAB API:
```
./ynab.sh last-used accounts | jq '.data.accounts[] | "\(.name) \(.id)"'
```

6. Use a spreadsheet to map pocketbook categories and accounts to YNAB categories (by name) and accounts (PB account number to YNAB account uuid)

7. Save the category CSV to `category-mapping.csv`

8. Save the accounts CSV to `acccount-mapping.csv`

9. The following required CSV files should now exist:
```
pocketbook-export.csv
ynab-categories.csv
category-mapping.csv
acccount-mapping.csv
```

10. Transactions can now be generated in `transactions/` by running:
```
python pb2ynab.py
```

11. Once transactions are created, iterate through `transactions/*.json`, and post them to the YNAB API:
```
./send-transactions.sh
```

12. Sent transactions are then moved to `proceessed/`. Logs can be viewed in `transactions.log`.

## Notes

- Examples of all CSV files can be found in the `examples/` folder
- For pocketbook transactions with no account set, the first row in the `acccount-mapping.csv` is used