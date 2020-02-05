import csv
import ast
new_rules_csv = []
with open('rules_before_conf.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader)
    new_rules_csv.append(['support','itemsets'])
    for row in csv_reader:
        cleanitemset = row[1].replace("frozenset({", '[')
        cleanitemset = cleanitemset.replace("})", ']')
        #cleanitemset = cleanitemset.replace("', '",',')
        print(cleanitemset)

        new_row = [row[0], cleanitemset]
        new_rules_csv.append(new_row)

with open('cleaned_frequent_itemsets.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',')
    for row in new_rules_csv:
        csv_writer.writerow(row)