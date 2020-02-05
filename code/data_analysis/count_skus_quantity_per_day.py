import pandas as pd
import csv
import ast


date_list = []
count_sku_dict = {}
with open("../../data/training_dates.csv") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)  # skip header:
    for row in csv_reader:
        date_list.append(row[0])

sku_max_dict = {}
count_sku_over_max_dict = {}
sku_quantity_per_day = {}

with open("../generated_data/maybe_ok_skus.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # skip header
    for row in csv_reader:
        sku_max_dict[row[0]] = 0
        count_sku_over_max_dict[row[0]] = 0
        sku_quantity_per_day[row[0]] = []


with open("../generated_data/articles_with_sku_max.csv") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)  # skip header:
    for row in csv_reader:
        if row[0] in sku_max_dict.keys():
            sku_max_dict[row[0]] = float(row[7])

df_orders = pd.read_csv(
    "../generated_data/sorted_orders_training_dates_with_ok_skus.csv"
)
df_orders["pick_start_time"] = pd.to_datetime(df_orders["pick_start_time"])
for date in date_list:
    df_date = df_orders.copy()
    df_date.set_index("pick_start_time", inplace=True)
    df_date = df_date.loc[date]
    df_date = df_date.reset_index()
    df_date = df_date.sort_values(by=["pick_start_time"])
    with open("../generated_data/maybe_ok_skus.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)  # skip header
        for row in csv_reader:
            count_sku_dict[row[0]] = 0

    df_date = df_date[["sku_id", "reserved_quantity"]]
    dataset = df_date.values.tolist()
    dataset_as_list = []
    for data in dataset:
        sku_list = ast.literal_eval(data[0])
        quantity_list = ast.literal_eval(data[1])
        for index, sku in enumerate(sku_list):
            count_sku_dict[str(sku)] += quantity_list[index]

    sku_count_list = []
    for key in count_sku_dict.keys():
        if count_sku_dict[key] > sku_max_dict[key]:
            count_sku_over_max_dict[key] += 1
        sku_quantity_per_day[key].append(count_sku_dict[key])

count_overflows = 0
total_skus = 0
skus_that_overflowed = []

for k, v in sorted(count_sku_over_max_dict.items(), key=lambda p: p[1], reverse=False):
    print([k, v])
    if v > 0:
        count_overflows += 1
        skus_that_overflowed.append(k)
    total_skus += 1
    print(k, sku_quantity_per_day[k])
print("number of skus that overflow their channel at least once:")
print(count_overflows)

print("percent skus that overflowed their channel for the training dates:")
print(count_overflows * 100 / total_skus)

# only checking the skus that had at least one overflow (the sku exceeded the channel capacity)
# If a sku never exceeded channel capacity during the training set then it is
# unlikely that it will exceed capacity on the test set.
# if it does it probably does so only by a small margin, unless something
# extraordinary happens. Since operators are still there it will never
# result in a stockout, just more workload for an operator.

with open(
    "../generated_data/quantity_skus_picked_per_day_that_overflowed.csv", "w"
) as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["sku", "quant_per_day"])
    for key in skus_that_overflowed:
        writer.writerow([key, sku_quantity_per_day[key]])
