import pandas as pd


df_transactions = pd.read_csv("../../data/transactions.csv")
df_transactions_in_batch = pd.read_csv("../../data/transactions_in_batch.csv")
df_batches = pd.read_csv("../../data/batches.csv")


df_merged_inner_join = pd.merge(
    left=df_batches,
    right=df_transactions_in_batch,
    left_on="sort_id",
    right_on="sort_id",
)

df_merged_inner_join["pick_start_time"] = pd.to_datetime(
    df_merged_inner_join["pick_start_time"]
)


df_orders = pd.merge(
    left=df_merged_inner_join,
    right=df_transactions,
    left_on="box_id",
    right_on="box_id",
)

df_orders_clean = df_orders[
    ["pick_start_time", "box_id", "sku_id", "reserved_quantity"]
]

df_bad_data = pd.read_csv("../data/bad_orders.csv")

df_orders_clean_box_and_sku = df_orders_clean[["box_id", "sku_id"]]
df_orders_clean_box_and_sku = df_orders_clean_box_and_sku.sort_values(by="box_id")
df_orders_clean_box_and_sku.to_csv("../generated_data/box_and_sku_id.csv", index=False)

df_orders_clean = df_orders_clean[
    ~df_orders_clean["box_id"].isin(df_bad_data["box_id"])
]

df_not_ok = pd.read_csv("../data/not_ok_skus.csv") # this is given

df_bad_box_ids = df_orders_clean[df_orders_clean["sku_id"].isin(df_not_ok["sku_id"])][
    "box_id"
]


before_rows = df_orders_clean.count()
df_orders_clean_ok_skus = df_orders_clean[
    ~df_orders_clean["box_id"].isin(df_bad_box_ids)
]
after_rows = df_orders_clean_ok_skus.count()
print("removed: " + str(before_rows - after_rows) + " rows")


threshold = 25
df_count_skus = df_orders_clean_ok_skus["sku_id"].value_counts()
df_count_skus_less_than_threshold = df_count_skus[df_count_skus.le(threshold)]


df_bad_box_ids_less_than_threshold = df_orders_clean_ok_skus[
    df_orders_clean_ok_skus["sku_id"].isin(df_count_skus_less_than_threshold.index)
]["box_id"]


df_orders_clean_ok_skus_with_minimum = df_orders_clean_ok_skus[
    ~df_orders_clean_ok_skus["box_id"].isin(df_bad_box_ids_less_than_threshold)
]

df_ok_skus = df_orders_clean_ok_skus_with_minimum.groupby(
    ["box_id", "pick_start_time"]
)["sku_id", "reserved_quantity"].agg(lambda x: list(x))


df_clean = df_orders_clean.groupby(["box_id", "pick_start_time"])[
    "sku_id", "reserved_quantity"
].agg(lambda x: list(x))


df_ok_skus.to_csv("../generated_data/sorted_orders_all_dates_with_ok_skus.csv")
df_clean.to_csv("../generated_data/sorted_orders_all_dates.csv")


df_training_dates = df_ok_skus.copy()
df_training_dates = df_training_dates.reset_index()
df_training_dates.set_index("pick_start_time", inplace=True)
df_training_dates = df_training_dates.loc["2019-08-15":"2019-10-31"]
df_training_dates = df_training_dates.reset_index()
df_training_dates.to_csv(
    "../generated_data/sorted_orders_training_dates_with_ok_skus.csv"
)

df_training_dates = df_clean.copy()
df_training_dates = df_training_dates.reset_index()
df_training_dates.set_index("pick_start_time", inplace=True)
df_training_dates = df_training_dates.loc["2019-08-15":"2019-10-31"]
df_training_dates = df_training_dates.reset_index()
df_training_dates.to_csv("../generated_data/sorted_orders_training_dates.csv")
