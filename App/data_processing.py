import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Dict, Any

def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads apartment data from a CSV file.
    
    Args:
        filepath: Path to the CSV file.
        
    Returns:
        pd.DataFrame: Loaded data.
    """
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found at: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Error loading CSV file: {e}")

def get_basic_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes basic metadata info about the dataset.
    
    Args:
        df: Input DataFrame.
        
    Returns:
        dict: Summary containing shape, dtypes, null counts, and memory usage.
    """
    return {
        "shape": df.shape,
        "dtypes": df.dtypes,
        "memory_usage_kb": df.memory_usage(deep=True).sum() / 1024,
        "null_counts": df.isnull().sum(),
        "total_nulls": df.isnull().sum().sum()
    }

def calculate_price_stats(df: pd.DataFrame, column: str = "cena_pln") -> Dict[str, float]:
    """
    Calculates summary statistics for a given price column.
    
    Args:
        df: Input DataFrame.
        column: Name of the price column.
        
    Returns:
        dict: Mean, median, standard deviation, skewness, and kurtosis.
    """
    series = df[column]
    return {
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "skewness": series.skew(),
        "kurtosis": series.kurtosis()
    }

def get_iqr_stats(df: pd.DataFrame, column: str, factor: float = 1.5) -> Tuple[float, float, float, float, float, pd.DataFrame]:
    """
    Computes IQR and boundaries for outlier detection, and extracts outlier rows.
    
    Args:
        df: Input DataFrame.
        column: Column to analyze.
        factor: IQR multiplier.
        
    Returns:
        Tuple: (Q1, Q3, IQR, lower_bound, upper_bound, outliers_df)
    """
    series = df[column]
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    outliers = df[(series < lower_bound) | (series > upper_bound)]
    return q1, q3, iqr, lower_bound, upper_bound, outliers

def get_zscore_outliers(df: pd.DataFrame, column: str, threshold: float = 3.0) -> pd.DataFrame:
    """
    Identifies outliers using standard Z-score method.
    
    Args:
        df: Input DataFrame.
        column: Column to analyze.
        threshold: Absolute Z-score limit.
        
    Returns:
        pd.DataFrame: Outlier rows.
    """
    z_scores = np.abs(stats.zscore(df[column]))
    return df[z_scores > threshold]

def get_modified_zscore_outliers(df: pd.DataFrame, column: str, threshold: float = 3.5) -> Tuple[float, pd.DataFrame]:
    """
    Identifies outliers using the robust Modified Z-score method.
    
    Args:
        df: Input DataFrame.
        column: Column to analyze.
        threshold: Modified Z-score limit.
        
    Returns:
        Tuple: (median absolute deviation (MAD), outliers_df)
    """
    series = df[column]
    median_val = series.median()
    mad = np.median(np.abs(series - median_val))
    
    # Avoid division by zero
    if mad == 0:
        modified_z = np.zeros_like(series)
    else:
        modified_z = 0.6745 * (series - median_val) / mad
        
    outliers = df[np.abs(modified_z) > threshold]
    return mad, outliers

def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans the dataset by filtering invalid construction years, applying
    winsorization (clipping price outliers), and computing log transform.
    
    Args:
        df: Input DataFrame.
        
    Returns:
        Tuple: (cleaned_df, cleaning_metadata)
    """
    cleaned_df = df.copy()
    
    # 1. Filter incorrect build years
    initial_count = len(cleaned_df)
    cleaned_df = cleaned_df[(cleaned_df["rok_budowy"] >= 1900) & (cleaned_df["rok_budowy"] <= 2026)]
    removed_years = initial_count - len(cleaned_df)
    
    # 2. Winsorization of price
    p01 = cleaned_df["cena_pln"].quantile(0.01)
    p99 = cleaned_df["cena_pln"].quantile(0.99)
    
    low_price_outliers = (cleaned_df["cena_pln"] < p01).sum()
    high_price_outliers = (cleaned_df["cena_pln"] > p99).sum()
    
    cleaned_df["cena_pln_capped"] = cleaned_df["cena_pln"].clip(lower=p01, upper=p99)
    
    # 3. Log transformation
    cleaned_df["cena_pln_log"] = np.log1p(cleaned_df["cena_pln"])
    
    # 4. Add helper calculation columns
    cleaned_df["cena_pln_per_m2"] = cleaned_df["cena_pln"] / cleaned_df["metraz_m2"]
    
    metadata = {
        "removed_years_count": removed_years,
        "p01_price": p01,
        "p99_price": p99,
        "low_price_outliers_count": low_price_outliers,
        "high_price_outliers_count": high_price_outliers
    }
    
    return cleaned_df, metadata
