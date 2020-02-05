# since there are some items that can not be picked regardless of the aframe is stocked.
# what is the maximum automation level that can possibly be reached?
# this assumes that the a-frame has an infinite storage space
import pandas as pd
import csv
import ast


def all_items_in_order_ok(order):
    for item in order:
        if item in not_ok_skus_list:
            return False
    return True


date_list = [
    "2019-11-01",
    "2019-11-02",
    "2019-11-03",
    "2019-11-04",
    "2019-11-05",
    "2019-11-06",
    "2019-11-07",
    "2019-11-08",
    "2019-11-09",
    "2019-11-10",
    "2019-11-11",
    "2019-11-12",
    "2019-11-13",
    "2019-11-14",
    "2019-11-15",
]

df_not_ok_skus = pd.read_csv("../generated_data/not_ok_skus.csv")
not_ok_skus_list = df_not_ok_skus["sku_id"].tolist()

df = pd.DataFrame(columns=["Date", "ok_order", "not_ok_order", "max_automation_level"])
index = 0
for date in date_list:
    df_orders = pd.read_csv("../generated_data/picks_per_date/" + date + ".csv")
    df_orders = df_orders["sku_id"]
    print("processing this date: " + date)
    dataset = df_orders.values.tolist()
    dataset_as_list = []
    for data in dataset:
        dataset_as_list.append(ast.literal_eval(data))
    print(dataset_as_list[:3])
    ok_order = 0
    not_ok_order = 0
    for order in dataset_as_list:
        if all_items_in_order_ok(order):
            ok_order += 1
        else:
            not_ok_order += 1

    max_automation_level = ok_order / (ok_order + not_ok_order)
    df.loc[index] = [date, ok_order, not_ok_order, max_automation_level]
    index += 1


df.sort_values(by="max_automation_level")
df.to_csv("../generated_data/max_automation_level_by_date.csv")
