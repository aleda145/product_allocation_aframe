from scipy import stats
import csv
import ast

sku_dict = {}
sku_hypothesis = {}
with open(
    "../generated_data/quantity_skus_picked_per_day_that_overflowed.csv"
) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # skip header
    for row in csv_reader:
        sku_dict[row[0]] = ast.literal_eval(row[1])
        sku_hypothesis[row[0]] = "Unknown"
# the null hypothesis is that the sku demand is normally distributed.
# if p is less than alpha then then the null hypothesis can be rejected.

alpha = 0.05  # alpha for which the null hypothesis can be rejected
count_rejections = 0
count_not_rejections = 0
count_total = 0
for key, value in sku_dict.items():
    print("testing normality for: " + key)
    print("with data: ")
    print(value)
    k2, p = stats.normaltest(value)
    count_total += 1
    if p < alpha:
        # Null hypothesis can be rejected
        sku_hypothesis[key] = "Rejected"
        count_rejections += 1
    else:
        # Null hypothesis can not be rejected
        sku_hypothesis[key] = "Not rejected"
        count_not_rejections += 1

print(sku_hypothesis)
print("rejections: " + str(count_rejections))
print("not rejections: " + str(count_not_rejections))
print("percent rejections: " + str(count_rejections / count_total))
print("percent not rejections: " + str(count_not_rejections / count_total))
