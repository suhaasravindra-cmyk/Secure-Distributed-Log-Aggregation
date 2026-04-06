import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv("logs.csv")

print("\n📊 Log Summary:")
print(df['level'].value_counts())

# 🔹 1. Log Level Distribution (Bar Graph)
plt.figure()
df['level'].value_counts().plot(kind='bar')
plt.title("Log Level Distribution")
plt.xlabel("Log Level")
plt.ylabel("Count")
plt.show()

# 🔹 2. Logs Over Time (Throughput)
plt.figure()
df['timestamp'].value_counts().sort_index().plot()
plt.title("Logs per Timestamp")
plt.xlabel("Time")
plt.ylabel("Number of Logs")
plt.show()

# 🔹 3. Pie Chart
plt.figure()
df['level'].value_counts().plot(kind='pie', autopct='%1.1f%%')
plt.title("Log Level Percentage")
plt.ylabel("")
plt.show()