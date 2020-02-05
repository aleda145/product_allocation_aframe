# import matplotlib.pyplot as plt
import pandas as pd

df_articles = pd.read_csv("../generated_data/articles_with_sku_max.csv", sep=",")

df_aframe = pd.read_csv("../allocation/aframe_allocation.csv", sep=",")

df_merged_inner_join = pd.merge(
    left=df_aframe, right=df_articles, left_on="sku_id", right_on="sku_id", how="left"
)


df_merged_inner_join.to_csv(
    "../generated_data/new_aframe_allocation_with_dimensions.csv", index=False
)
