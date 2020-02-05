import pandas as pd
import csv

df_orders = pd.read_csv("../generated_data/sorted_orders_all_dates.csv")
date_list = []
with open("../../data/pick_dates.csv") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)  # skip header:
    for row in csv_reader:
        date_list.append(row[0])

df_orders["pick_start_time"] = pd.to_datetime(df_orders["pick_start_time"])

for date in date_list:
    df_date = df_orders.copy()
    df_date.set_index("pick_start_time", inplace=True)
    df_date = df_date.loc[date]
    df_date = df_date.reset_index()
    df_date = df_date.sort_values(by=["pick_start_time"])

    df_date = df_date[["pick_start_time", "box_id", "sku_id", "reserved_quantity"]]
    df_date.to_csv("../generated_data/picks_per_date/" + date + ".csv", index=False)
