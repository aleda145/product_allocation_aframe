import csv
import ast

rules = []

with open("../machine_learning/clean_rules_after_conf_threshold.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # skip header
    for row in csv_reader:
        rules.append(row)
graph = {}

for rule in rules:
    antecedent = ast.literal_eval(rule[0])[0]  # antecedent
    consequent = ast.literal_eval(rule[1])[0]  # consequent
    rule_support = float(rule[4])
    if antecedent not in graph.keys():
        graph[antecedent] = {}
    graph[antecedent][consequent] = rule_support

print(graph)
sku_dict = {}

with open("../generated_data/support_for_single_sku_orders.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)
    for row in csv_reader:
        sku_dict[row[0]] = float(row[1])

channels = []
with open("aframe_channels.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    for row in csv_reader:
        channels.append(row)

num_channels_for_a_sku = {}
# try:
#     with open('../generated_data/num_channels_per_sku_mean.csv') as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         next(csv_reader)
#         for row in csv_reader:
#             num_channels_for_a_sku[row[0]] = float(row[1])
# except FileNotFoundError:
#     print("no channels assigned, all skus will be assigned to one channel")

try:
    with open("../generated_data/num_channels_per_sku_median.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            num_channels_for_a_sku[row[0]] = float(row[1])
except FileNotFoundError:
    print("no channels assigned, all skus will be assigned to one channel")

# start algo:
# choose highest value from the sku_dict, this is our starting sku.
added_skus = []
chosen_sku = max(sku_dict, key=sku_dict.get)
print("starting sku: " + chosen_sku)
if (
    chosen_sku in num_channels_for_a_sku.keys()
):  # if it has many channels, add all those channels
    for i in range(1, int(num_channels_for_a_sku[chosen_sku])):
        added_skus.append(chosen_sku)
else:
    added_skus.append(chosen_sku)
del sku_dict[chosen_sku]
while len(added_skus) <= len(
    channels
):  # while channels not reached the maximum capacity.

    candidate_sku = max(
        sku_dict, key=sku_dict.get
    )  # choose the highest sku with single support
    candidate_score = sku_dict[candidate_sku]
    print("first candidate: " + candidate_sku)
    print("with score: " + str(candidate_score))

    sku_association_score = {}
    for antecedent in set(
        added_skus
    ):  # the added skus are antecedents, i.e. they have relations => to other skus
        print("checking association from this sku:" + antecedent)

        if antecedent in graph.keys():
            for consequent in graph[antecedent]:  # checking each consequent the sku has
                if (
                    consequent in sku_dict.keys()
                ):  # make sure this consequent has not already been added to the chosen sku list
                    if consequent not in sku_association_score.keys():
                        sku_association_score[consequent] = graph[antecedent][
                            consequent
                        ]
                    else:
                        sku_association_score[consequent] += graph[antecedent][
                            consequent
                        ]

    for consequent in sku_association_score.keys():
        score = sku_dict[consequent] + sku_association_score[consequent]
        if consequent in num_channels_for_a_sku.keys():
            score = (
                score / num_channels_for_a_sku[consequent]
            )  # if it is assigned a specific number of channels
            # divide the score by that number. This will make the algorithm choose SKUs that have a higher
            # overall value for the A-frame
        # the score is a consequents single support and the support from the chosen antecedent
        # to the consequent.
        # since different antecedents will have different supports to the consequent
        # this will be done mulitple times
        print(score)
        if score > candidate_score:
            # if the new score is better, change candidate sku
            candidate_sku = consequent
            candidate_score = score
            print("new candidate: " + candidate_sku)
            print("with score: " + str(candidate_score))

    print("adding this sku to list:" + candidate_sku)
    # delete the edges of all  items in the added_skus, as they are no longer valid

    for i in added_skus:
        if i in graph.keys():
            if candidate_sku in graph[i].keys():
                del graph[i][candidate_sku]

    if (
        candidate_sku in num_channels_for_a_sku.keys()
    ):  # if it has many channels, add all those channels
        for i in range(1, int(num_channels_for_a_sku[candidate_sku])):
            added_skus.append(candidate_sku)
    else:
        added_skus.append(candidate_sku)

    del sku_dict[
        candidate_sku
    ]  # delete it from the sku dict, its single support is already counted


print(len(added_skus))
new_allocation = []
for index, channel in enumerate(channels):

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
