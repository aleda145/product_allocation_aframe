import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from mlxtend.frequent_patterns import fpgrowth
import ast


df_orders = pd.read_csv(
    "../generated_data/sorted_orders_training_dates_with_ok_skus.csv"
)
df_orders = df_orders["sku_id"]
dataset = df_orders.values.tolist()
dataset_as_list = []
print("Transform data into a matrix...")
for data in dataset:
    dataset_as_list.append(ast.literal_eval(data))
te = TransactionEncoder()

oht_ary = te.fit(dataset_as_list).transform(dataset_as_list, sparse=True)
sparse_df = pd.SparseDataFrame(oht_ary, columns=te.columns_, default_fill_value=False)
sparse_df.columns = [str(i) for i in sparse_df.columns]
print(sparse_df)
print("Generated correct dataframe, now performing FP-growth...")
frequent_itemsets_fpgrowth = fpgrowth(
    sparse_df, min_support=0.0000025, use_colnames=True, verbose=1, max_len=2
)

frequent_itemsets_fpgrowth.to_csv("rules_before_conf.csv", index=False)
associations = association_rules(
    frequent_itemsets_fpgrowth, metric="confidence", min_threshold=0.0
)
associations.to_csv("rules.csv", index=False)
