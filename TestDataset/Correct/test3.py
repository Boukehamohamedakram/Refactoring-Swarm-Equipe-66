import pandas as pd

def normalize_features(df):
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    # Compute column-wise mean and std
    mean = df.mean(axis=0)
    std = df.std(axis=0)

    # Avoid divide by zero for constant columns
    std_replaced = std.replace(0, 1)

    # Normalize each column
    df_norm = (df - mean) / std_replaced
    return df_norm


data = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 7, 7]
})

normalized = normalize_features(data)
print(normalized)