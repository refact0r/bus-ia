import scipy.stats
import pandas

df = pandas.read_csv("data/predictions.csv")

# count
count = len(df.index)
print("Count:", count)

# absolute prediction error
df["predictionErrorAbsolute"] = df["predictionError"].abs()

# sample sum
sample_sum = df["predictionErrorAbsolute"].sum()
print("Sample sum:", sample_sum)

# sample mean
sample_mean = df["predictionErrorAbsolute"].mean()
print("Sample mean:", sample_mean)

# summation of difference from mean squared
diff_sum = sum((x - sample_mean) ** 2 for x in df["predictionErrorAbsolute"])
print("Summation of difference from mean squared:", diff_sum)

# sample variance
sample_variance = df["predictionErrorAbsolute"].var()
print("Sample variance:", sample_variance)

# sample standard deviation
sample_std = df["predictionErrorAbsolute"].std()
print("Sample standard deviation:", sample_std)

# 95% confidence interval for population mean
val = sample_std / (count**0.5)
tval = scipy.stats.t.ppf(1 - 0.025, count - 1) * val
print("Population confidence interval:", sample_mean - tval, sample_mean + tval)
