import scipy.stats
import pandas
import numpy

df = pandas.read_csv("data/predictions.csv")

df["predictionErrorAbs"] = df["predictionError"].abs()

n = len(df)
print("n:", n)

r = scipy.stats.pearsonr(df["predictionDelta"], df["predictionErrorAbs"])[0]
print("Correlation coefficient:", r)

t = r * numpy.sqrt(n - 2) / numpy.sqrt(1 - r**2)
print("t:", t)

crit = scipy.stats.t.ppf(0.95, n - 2)
print("Critical value:", crit)
