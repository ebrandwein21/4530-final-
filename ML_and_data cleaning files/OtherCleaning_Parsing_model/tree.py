import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

df = pd.read_csv("cleaned_player.csv")

# Sort by player and game
df = df.sort_values(["player1_id", "game_id"])

#finding Slope of points over games for each player
def compute_slope(points):
    if len(points) < 2:
        return 0
    x = np.arange(len(points))
    slope = np.polyfit(x, points, 1)[0]
    return slope

df["slope"] = df.groupby("player1_id")["points"].transform(compute_slope)

# 1 means improving, 0 means declining
df["improving"] = (df["slope"] > 0).astype(int)
df["slope"] = df.groupby("player1_id")["points"].transform(compute_slope)
df["improving"] = (df["slope"] > 0).astype(int)

# Console output
print("\nPlayer Summary:")
player_summary = df.groupby("player1_id").agg(
    name=("player1_name", "first"),
    slope=("slope", "first"),
    improving=("improving", "first")
)

print(player_summary.head(20))
print("\nTotal improving players:", player_summary["improving"].sum())
print("Total declining players:", len(player_summary) - player_summary["improving"].sum())


features = [
    "points",
    "two_pt_made",
    "three_pt_made",
    "rebounds",
    "turnovers",
    "fouls",
]

df = df.fillna(0)
X = df[features]
y = df["improving"]

# split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# training
model = DecisionTreeClassifier(class_weight="balanced",random_state=42)
model.fit(X_train, y_train)

# Evaluation
accuracy = model.score(X_test, y_test)
print("\nModel accuracy:", accuracy)

# Feature importance
importances = model.feature_importances_
print("\nFeature importance (higher = more important):")
for feat, imp in zip(features, importances):
    print(f"{feat}: {imp:.3f}")
df["prediction"] = model.predict(X)
df.to_csv("player_improvement_predictions.csv", index=False)
print("\nSaved to player_improvement_predictions.csv")

# plotting portion
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

plt.figure(figsize=(8,4))
plt.hist(player_summary["slope"], bins=30, color="royalblue", alpha=0.7)
plt.axvline(0, color="red", linestyle="--")
plt.title("Distribution of Player Scoring Slopes (One Slope Per Player)")
plt.xlabel("Slope of Points Over Games")
plt.ylabel("Number of Players")
plt.tight_layout()
plt.show()



