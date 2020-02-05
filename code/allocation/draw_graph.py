import csv
import ast
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


support = 0.001
confidence = 0.25

df_rules_clean = pd.read_csv("../machine_learning/cleaned_rules.csv")

df_rules_clean = df_rules_clean[df_rules_clean["support"] >= support]
df_rules_clean = df_rules_clean[df_rules_clean["confidence"] >= confidence]
df_rules_clean = df_rules_clean[df_rules_clean["lift"] >= 1]

df_rules_clean = df_rules_clean.sort_values(by="support", ascending=False)
df_rules_clean[
    [
        "antecedents",
        "consequents",
        "antecedent support",
        "consequent support",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction",
    ]
].to_csv("../machine_learning/clean_rules_after_conf_threshold.csv", index=False)

rules = []
with open("../machine_learning/clean_rules_after_conf_threshold.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # skip header
    for row in csv_reader:
        rules.append(row)

G = nx.Graph()
print("generating graph:")
for rule in rules:
    antecedent = ast.literal_eval(rule[0])[0]
    consequent = ast.literal_eval(rule[1])[0]
    G.add_edge(antecedent, consequent)


options = {
    "node_color": "blue",
    "node_size": 5,
    "line_color": "black",
    "linewidths": 1,
    "width": 0.1,
}
print("drawing normal graph:")
nx.draw(G, **options)

plt.savefig(
    "../../liuthesis-master/figures/graph_plots/graph_sup"
    + str(support).replace(".", "_")
    + "_conf"
    + str(confidence).replace(".", "_")
    + ".pdf"
)


DG = nx.DiGraph()
dg_list = []
for rule in rules:
    antecedent = ast.literal_eval(rule[0])[0]
    consequent = ast.literal_eval(rule[1])[0]
    rule_support = float(rule[4])
    dg_list.append([antecedent, consequent, rule_support])
DG.add_weighted_edges_from(dg_list)

options = {
    "node_color": "blue",
    "node_size": 5,
    "line_color": "black",
    "linewidths": 1,
    "width": 0.1,
    "arrowsize": 10,
}
nx.draw(DG, **options)

plt.savefig(
    "../../liuthesis-master/figures/graph_plots/directed_tree_sup"
    + str(support)
    + "_conf"
    + str(confidence)
    + ".pdf"
)
