import pandas as pd
import csv
import ast


sku_dict = {}
count_sku_dict = {}
with open("../generated_data/maybe_ok_skus.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # skip header
    for row in csv_reader:
        sku_dict[row[0]] = 0.0
        count_sku_dict[row[0]] = 0


df_orders = pd.read_csv(
    "../generated_data/sorted_orders_training_dates_with_ok_skus.csv"
)

num_of_orders = len(df_orders.index)


df_orders = df_orders["sku_id"]
dataset = df_orders.values.tolist()
dataset_as_list = []
count_only_one_order = 0
support_sku_dict = sku_dict.copy()
# This only counts number of _orders_ that a sku is in. Not their quantity!
for data in dataset:
    data_as_list = ast.literal_eval(data)
    if len(data_as_list) == 1:
        # this means there is only one SKU in the order:
        sku_dict[str(data_as_list[0])] += 1.0
        count_only_one_order += 1
    for sku in data_as_list:
        count_sku_dict[str(sku)] += 1


with open("../generated_data/num_orders_for_single_sku_orders.csv", "w") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["sku_id", "num_orders"])
    for key, val in sku_dict.items():
        writer.writerow([key, val])

sku_support_list = []
for key, val in sku_dict.items():
    support = val / num_of_orders
    sku_support_list.append([key, support])

sku_count_list = []
for key, val in count_sku_dict.items():
    sku_count_list.append([key, val])

df_support_for_single_sku = pd.DataFrame(
    sku_support_list, columns=["sku_id", "support"]
)
df_support_for_single_sku = df_support_for_single_sku.sort_values(
    by=["support"], ascending=False
)
df_support_for_single_sku.to_csv(
    "../generated_data/support_for_single_sku_orders.csv", index=False
)

df_count = pd.DataFrame(sku_count_list, columns=["sku_id", "count"])
df_count = df_count.sort_values(by=["count"], ascending=False)

df_count.to_csv("../generated_data/quantity_per_ok_sku.csv", index=False)
