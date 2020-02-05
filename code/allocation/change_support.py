import pandas as pd


support = 0.00001
confidence = 0

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
