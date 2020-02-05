import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import pandas as pd

date_list = [
    "2019-11-01",
    "2019-11-02",
    "2019-11-03",
    "2019-11-04",
    "2019-11-05",
    "2019-11-06",
    "2019-11-07",
    "2019-11-08",
    "2019-11-09",
    "2019-11-10",
    "2019-11-11",
    "2019-11-12",
    "2019-11-13",
    "2019-11-14",
    "2019-11-15",
]


df_max_automation = pd.read_csv("../generated_data/max_automation_level_by_date.csv")
df_max_automation["Date"] = pd.to_datetime(df_max_automation["Date"])

x = df_max_automation["Date"]
y = df_max_automation["max_automation_level"] * 100
y_mean = df_max_automation["max_automation_level"].mean() * 100
fig, ax = plt.subplots()
ax.bar(x, y)
ax.set_xlabel("Date")
ax.set_ylabel("Max Automation level")
ax.axhline(
    y_mean, linestyle="--", color="red", label="Mean: " + str(round(y_mean, 2)) + "%"
)
legend = ax.legend(loc="lower left")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter("%Y-%m-%d")


ax.set_title("Max Automation level for a date")
fig.savefig("../../liuthesis-master/figures/a_frame_figures/max_automation_level.pdf")


df_aframe_stats = pd.concat(
    pd.read_csv("../generated_data/aframe_info/" + date + "/general_stats.csv")
    for date in date_list
)
df_aframe_stats["date"] = pd.to_datetime(df_aframe_stats["date"])


x = df_aframe_stats.date
y = df_aframe_stats.automation_level * 100
y_mean = df_aframe_stats["automation_level"].mean() * 100
fig, ax = plt.subplots()
ax.bar(x, y, label="Automation level")
ax.set_xlabel("Date")
ax.set_ylabel("Automation level")
ax.axhline(
    y_mean, linestyle="--", color="red", label="Mean: " + str(round(y_mean, 2)) + "%"
)
legend = ax.legend(loc="upper right")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter("%Y-%m-%d")


ax.set_title("Automation level for the allocation by date")
fig.savefig("../../liuthesis-master/figures/a_frame_figures/allocation.pdf")


x = df_aframe_stats.date
y = df_aframe_stats.automation_level * 100
y_2 = df_max_automation["max_automation_level"] * 100
fig, ax = plt.subplots()
ax.bar(x, y_2, color="red", label="Unused capacity")

ax.bar(x, y)

ax.set_xlabel("Date")
ax.set_ylabel("Automation level")
legend = ax.legend(loc="lower left")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter("%Y-%m-%d")


ax.set_title("Automation level for the allocation by date and max")
fig.savefig("../../liuthesis-master/figures/a_frame_figures/unused_capacity.pdf")

x = df_aframe_stats.date
y = df_aframe_stats["total_refills"]
y_mean = df_aframe_stats["total_refills"].mean()
fig, ax = plt.subplots()
ax.bar(x, y, label="Refills")
ax.set_xlabel("Date")
ax.set_ylabel("Refills")
ax.axhline(y_mean, linestyle="--", color="red", label="Mean: " + str(round(y_mean, 2)))
legend = ax.legend(loc="upper right")
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter("%Y-%m-%d")


ax.set_title("Number of channel refills for the allocation by date")
fig.savefig("../../liuthesis-master/figures/a_frame_figures/num_refills_allocation.pdf")
