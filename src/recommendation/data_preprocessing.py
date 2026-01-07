import pandas as pd
from sklearn.model_selection import train_test_split

def load_data(path: str):
    """Load dataset from CSV file."""
    df = pd.read_csv(path)
    return df

def split_data(df: pd.DataFrame, target_col: str = "label"):
    """Split dataset into train and test sets."""
    X = df.drop(target_col, axis=1)
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=5, stratify=y
    )
    return X_train, X_test, y_train, y_test
