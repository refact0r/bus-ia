import seaborn
import pandas

df = pandas.read_csv("data/predictions.csv")

seaborn.set_theme()

plot = seaborn.histplot(data=df, x="predictionError", bins=30)

plot.set_title("Prediction Error Distribution")
plot.set_xlabel("Prediction Error (seconds)")

plot.get_figure().savefig("images/histogram.png", dpi=500)
