import seaborn
import pandas

df = pandas.read_csv("data/predictions.csv")

df["predictionErrorAbs"] = df["predictionError"].abs()

seaborn.set_theme()

plot = seaborn.scatterplot(
    data=df,
    x="predictionDelta",
    y="predictionErrorAbs",
    s=1,
    alpha=0.01,
    edgecolor="none",
)

plot.set_title("Absolute Prediction Error vs. Time to Arrival")
plot.set_ylabel("Absolute Prediction Error (Seconds)")
plot.set_xlabel("Time to Arrival (Seconds)")

plot.figure.savefig("images/graph.png", dpi=500)
