import csv

channels = []
with open("aframe_channels.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    for row in csv_reader:
        channels.append(row)

new_channels = []

num_channels_for_a_sku = {}
# with open('../generated_data/num_channels_per_sku_mean.csv') as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=',')
#     next(csv_reader)
#     for row in csv_reader:
#         num_channels_for_a_sku[row[0]] = float(row[1])

with open("../generated_data/num_channels_per_sku_median.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)
    for row in csv_reader:
        num_channels_for_a_sku[row[0]] = float(row[1])

sku_score = {}
with open("../generated_data/quantity_per_ok_sku.csv") as csv_file:
    # this file has to be sorted to work!
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)
    for row in csv_reader:
        sku_score[row[0]] = float(row[1])


for sku in sku_score.keys():
    if sku in num_channels_for_a_sku.keys():
        sku_score[sku] = sku_score[sku] / num_channels_for_a_sku[sku]

added_skus = []
while len(added_skus) <= len(
    channels
):  # while channels not reached the maximum capacity.

    chosen_sku = max(sku_score, key=sku_score.get)
    if (
        chosen_sku in num_channels_for_a_sku.keys()
    ):  # if it has many channels, add all those channels
        for i in range(1, int(num_channels_for_a_sku[chosen_sku])):
            added_skus.append(chosen_sku)
    else:
        added_skus.append(chosen_sku)
    del sku_score[chosen_sku]


new_allocation = []
for index, channel in enumerate(channels):
    # print(channel)

    if len(added_skus) != 0:
        channel.append(added_skus[index])
    else:
        channel.append("-1")
    new_allocation.append(channel)

    print(channel)

with open("aframe_allocation.csv", "w") as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=",")
    csv_writer.writerow(["channel", "sku_id"])
    for channel in new_allocation:
        csv_writer.writerow(channel)
