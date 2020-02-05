import numpy as np

# import matplotlib.pyplot as plt
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


df_orders = pd.read_csv("../generated_data/sorted_orders_training_dates.csv")
num_of_orders = len(df_orders.index)

df_orders = df_orders["sku_id"]
dataset = df_orders.values.tolist()
dataset_as_list = []
count_only_one_order = 0
support_sku_dict = sku_dict.copy()
# this only counts number of _orders_ that a sku is in. Not their quantity!
for data in dataset:
    data_as_list = ast.literal_eval(data)
    for sku in data_as_list:
        if (
            str(sku) in sku_dict.keys()
        ):  # only count skus that are ok. ignore skus that cant fit
            count_sku_dict[str(sku)] += 1


sku_count_list = []
for key, val in count_sku_dict.items():
    sku_count_list.append([key, val])

df_count = pd.DataFrame(sku_count_list, columns=["sku_id", "count"])
df_count = df_count.sort_values(by=["count"], ascending=False)

df_count.to_csv("../generated_data/quantity_per_all_skus.csv", index=False)
