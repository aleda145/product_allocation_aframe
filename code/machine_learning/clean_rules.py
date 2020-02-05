import csv
# since the rules are saved with frozensets this small script removes them and saves it as a cleaned rules
new_rules_csv = []
with open("rules.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    new_rules_csv.append(next(csv_reader))
    for row in csv_reader:
        clean_antecedent = row[0].replace("frozenset({", "[")
        clean_antecedent = clean_antecedent.replace("})", "]")
        clean_consequent = row[1].replace("frozenset({", "[")
        clean_consequent = clean_consequent.replace("})", "]")
        new_row = [
            clean_antecedent,
            clean_consequent,
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
        ]
        new_rules_csv.append(new_row)

with open("cleaned_rules.csv", "w") as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=",")
    for row in new_rules_csv:
        csv_writer.writerow(row)
