import pandas as pd

def normalize_features(df):
    return (df - df.mean()) / df.std()

data = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 7, 7]
})

normalized = normalize_features(data)
print(normalized)