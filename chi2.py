import scipy.stats
import pandas
import numpy

df = pandas.read_csv("data/predictions.csv")

count = len(df.index)

max = df["predictionError"].max()
print("max: ", max)
min = df["predictionError"].min()
print("min: ", min)
avg = df["predictionError"].mean()
print("avg: ", avg)
dsum = df["predictionError"].sum()
print("sum: ", dsum)
stdev = df["predictionError"].std()
print("stdev: ", stdev)
var = df["predictionError"].var()
print("var: ", var)
diff_sum = sum((x - avg) ** 2 for x in df["predictionError"])
print("Summation of difference from mean squared:", diff_sum)

bin_method = 30

bin_edges = numpy.histogram_bin_edges(df["predictionError"], bins=bin_method)
bin_count = len(bin_edges) - 1
print("bin count:", bin_count)

df["bins"] = pandas.cut(x=df["predictionError"], bins=bin_edges, include_lowest=True)

binned = df.groupby("bins", observed=False).count()

total = binned["predictionError"].sum()
print("total: ", total)

distr = scipy.stats.norm(avg, stdev)

binned["expected"] = [
    (distr.cdf(bin_edges[i + 1]) - distr.cdf(bin_edges[i])) * total
    for i in range(0, bin_count)
]
binned["chicalc"] = ((binned["predictionError"] - binned["expected"]) ** 2) / binned[
    "expected"
]

print(binned)

chi2 = binned.loc[binned["expected"] > 0, "chicalc"].sum()
print("calc:", chi2)

crit = scipy.stats.chi2.ppf(q=0.95, df=bin_count - 3)
print("crit:", crit)
