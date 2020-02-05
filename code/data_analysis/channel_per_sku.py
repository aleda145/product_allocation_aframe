import scipy
import csv
import ast
import math

sku_dict = {}
sku_hypothesis = {}

# load in the SKUs.

with open(
    "../generated_data/quantity_skus_picked_per_day_that_overflowed.csv"
) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # skip header
    for row in csv_reader:
        sku_dict[row[0]] = ast.literal_eval(row[1])


# Load in their max

sku_max_dict = {}
with open("../generated_data/articles_with_sku_max.csv") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)  # skip header:
    for row in csv_reader:
        if row[0] in sku_dict.keys():
            sku_max_dict[row[0]] = float(row[7])

# find mean for each sku. Then find how many channels that is for the sku
for key, value in sku_dict.items():
    mean = scipy.mean(value)
    print("mean for sku " + str(key) + "is: " + str(mean))
    channels = math.ceil(mean / sku_max_dict[key])
    print("assign number of channels: ")
    print(channels)


with open("../generated_data/num_channels_per_sku_mean.csv", "w") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["sku", "num_channels"])
    for key, value in sku_dict.items():
        mean = scipy.mean(value)
        channels = math.ceil(mean / sku_max_dict[key])
        writer.writerow([key, channels])

for key, value in sku_dict.items():
    median = scipy.median(value)
    print("median for sku " + str(key) + "is: " + str(median))
    channels = math.ceil(median / sku_max_dict[key])
    print("assign number of channels: ")
    print(channels)


with open("../generated_data/num_channels_per_sku_median.csv", "w") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["sku", "num_channels"])
    for key, value in sku_dict.items():
        median = scipy.median(value)
        # to prevent assigning a channel to 0.
        if math.ceil(median / sku_max_dict[key]) >= 1:
            channels = math.ceil(median / sku_max_dict[key])
        else:
            channels = 1
        writer.writerow([key, channels])
