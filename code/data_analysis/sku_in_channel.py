"""
This program reads the article data, finds which articles have valid data
(dimensions greater than 0), then calculates how it should be placed
in an A-frame channel.
This is done by assuming that each item should be placed so it creates the most
amount of stock in the channel as possible. The limiting factor is the height
of a dispensing channel, which was measured to roughly 1700 millimeters.
Thus if a sku is rotated so it is stacked with the lowest y_value it will result
in as many products as possible in a channel.
The x_value for a rotation is also saved to make an analysis if a allocation can
fit in an A-frame module.
For skus that dont have any dimensions their maximum sku height is set to
the mean of all the items that had dimensions.
"""

import numpy as np
import pandas as pd

df_articles = pd.read_csv("../../data/products.csv", sep=",")

print(df_articles)
df_articles = df_articles[["sku_id", "weight", "width", "length", "height"]]

MAX_CHANNEL_HEIGHT = 1700  # after fuzzy measuring

# find articles that have ok data
df_articles_with_ok_dimensions = df_articles[
    (df_articles["length"] > 0)
    & (df_articles["width"] > 0)
    & (df_articles["height"] > 0)
]

df_articles_with_unknown_dimensions = df_articles[
    (df_articles["length"] <= 0)
    | (df_articles["width"] <= 0)
    | (df_articles["height"] <= 0)
]

print(df_articles_with_ok_dimensions)
# 45% of products have ok data.

# making a copy to make sure there is no overwriting errors, setting with copy errors
df_articles_with_ok_dimensions_new = df_articles_with_ok_dimensions.copy()

df_articles_with_ok_dimensions_new["y_value"] = df_articles_with_ok_dimensions[
    ["width", "length", "height"]
].min(axis=1)

df_articles_with_ok_dimensions_new["x_value"] = df_articles_with_ok_dimensions[
    ["width", "length", "height"]
].apply(lambda row: row.nsmallest(2).values[-1], axis=1)

print(df_articles_with_ok_dimensions_new)

df_articles_with_ok_dimensions_new["max_stock_in_channel"] = np.floor(
    MAX_CHANNEL_HEIGHT / df_articles_with_ok_dimensions_new[["y_value"]]
)
print(df_articles_with_ok_dimensions_new)

# get average max stock in channel

mean_value = df_articles_with_ok_dimensions_new["max_stock_in_channel"].mean()
# since some articles do not have data their max stock in the A-frame have to be estimated.
# this estimates that to be the mean value of all the skus. This should be corrected when data
# exists as it will affect the solution.

df_articles_with_unknown_dimensions_new = df_articles_with_unknown_dimensions.copy()
df_articles_with_unknown_dimensions_new["y_value"] = 0
df_articles_with_unknown_dimensions_new["x_value"] = 0
df_articles_with_unknown_dimensions_new["max_stock_in_channel"] = np.floor(mean_value)

print(df_articles_with_unknown_dimensions_new)


df_articles_with_more_data = pd.concat(
    [df_articles_with_ok_dimensions_new, df_articles_with_unknown_dimensions_new]
)
print(df_articles_with_more_data)
df_articles_with_more_data.to_csv(
    "../generated_data/articles_with_sku_max.csv", index=False
)
