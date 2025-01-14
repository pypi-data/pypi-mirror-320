from re import X
import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split

def load_dataset(file_path):
    """
    Loads a dataset using the appropriate pandas function based on the file extension.

    Parameters:
        file_path (str): Path to the file to be loaded.

    Returns:
        pd.DataFrame: Loaded dataset as a pandas DataFrame.
    """
    #if not os.path.isfile(file_path):
        #raise FileNotFoundError(f"The file '{file_path}' does not exist or is not a valid file.")

    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        if file_extension == '.csv':
            return pd.read_csv(file_path)
        elif file_extension in ['.xls', '.xlsx']:
            return pd.read_excel(file_path)
        elif file_extension == '.json':
            return pd.read_json(file_path)
        elif file_extension == '.parquet':
            return pd.read_parquet(file_path)
        elif file_extension == '.feather':
            return pd.read_feather(file_path)
        elif file_extension == '.h5':
            return pd.read_hdf(file_path)
        elif file_extension == '.html':
            return pd.read_html(file_path)[0]
        elif file_extension == '.stata':
            return pd.read_stata(file_path)
        elif file_extension == '.sas7bdat':
            return pd.read_sas(file_path)
        elif file_extension == '.txt':
            return pd.read_csv(file_path, sep="\t")
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        raise RuntimeError(f"Error loading file '{file_path}': {str(e)}")


def fill_missing_values(data, strategy="mean"):
    """
    Fills missing values in a Pandas DataFrame or Series using the specified strategy.

    Parameters:
        data (pd.DataFrame or pd.Series): The input data with potential missing values.
        strategy (str): The strategy to fill missing values. Options are:
                        - "mean": Fill with the mean of the column.
                        - "median": Fill with the median of the column.
                        - "mode": Fill with the mode of the column.
                        - for constant input float as strategy.

    Returns:
        pd.DataFrame or pd.Series: Data with missing values filled.
    """
    if not isinstance(data, (pd.DataFrame, pd.Series)):
        raise TypeError("Input data must be a Pandas DataFrame or Series.")

    if strategy not in ["mean", "median", "mode", "constant"]:
        raise ValueError("Invalid strategy. Choose from 'mean', 'median', 'mode', or 'constant'.")

    if strategy == "mean":
        return data.fillna(data.mean())
    elif strategy == "median":
        return data.fillna(data.median())
    elif strategy == "mode":
        mode_values = data.mode()
        if isinstance(data, pd.DataFrame):
            return data.fillna({col: mode_values[col].iloc[0] for col in data.columns if not mode_values[col].empty})
        else:
            return data.fillna(mode_values.iloc[0])
    elif strategy == float:
        return data.fillna(strategy)



def remove_outliers(data, method="IQR", threshold=1.5):
    """
    Removes outliers from a Pandas DataFrame or Series using the specified method.

    Parameters:
        data (pd.DataFrame or pd.Series): The input data from which to remove outliers.
        method (str): The method to use for detecting outliers. Options are:
                      - "IQR": Interquartile Range method.
                      - "z-score": Z-score method.
        threshold (float): The threshold for detecting outliers.
                           For IQR, it's the multiplier for the IQR.
                           For z-score, it's the absolute value cutoff.

    Returns:
        pd.DataFrame or pd.Series: Data with outliers removed.
    """
    if not isinstance(data, (pd.DataFrame, pd.Series)):
        raise TypeError("Input data must be a Pandas DataFrame or Series.")

    if method not in ["IQR", "z-score"]:
        raise ValueError("Invalid method. Choose from 'IQR' or 'z-score'.")

    if method == "IQR":
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return data[(data >= lower_bound) & (data <= upper_bound)]

    elif method == "z-score":
        mean = data.mean()
        std = data.std()
        z_scores = (data - mean) / std
        return data[np.abs(z_scores) <= threshold]



def split_train_test(data, features, target, t_size=.3):
  if not isinstance(data, pd.DataFrame):
      raise TypeError("df must be a pandas DataFrame.")
  if not all(feature in data.columns for feature in features):
      raise ValueError("One or more specified features not found in the DataFrame.")
  if target not in data.columns:
      raise ValueError("Specified target not found in the DataFrame.")

  X = data[features]
  y = data[target]
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=t_size, random_state=42)
  return X_train, X_test, y_train, y_test