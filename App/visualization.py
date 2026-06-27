import os
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Tuple

def setup_plotting_style():
    """
    Configures default plotting styles for matplotlib and seaborn.
    """
    plt.rcParams.update({
        'figure.figsize': (12, 7),
        'figure.dpi': 150,
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'figure.facecolor': 'white',
        'axes.facecolor': '#fafafa',
        'axes.grid': True,
        'grid.alpha': 0.3,
    })
    sns.set_style("whitegrid")

def plot_histograms(df: pd.DataFrame, output_path: str):
    """
    Generates and saves histograms with KDE for price and area.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Price distribution
    ax1 = axes[0]
    sns.histplot(df["cena_pln"], bins=60, kde=True, color="#4C72B0", alpha=0.7,
                 edgecolor='white', linewidth=0.5, ax=ax1)
    ax1.set_title("Rozkład ceny mieszkań (cena_pln)", fontweight='bold')
    ax1.set_xlabel("Cena [PLN]")
    ax1.set_ylabel("Liczba ofert")
    ax1.axvline(df["cena_pln"].median(), color='red', linestyle='--', linewidth=1.5,
                label=f'Mediana: {df["cena_pln"].median():,.0f} zł')
    ax1.axvline(df["cena_pln"].mean(), color='orange', linestyle='--', linewidth=1.5,
                label=f'Średnia: {df["cena_pln"].mean():,.0f} zł')
    ax1.legend(fontsize=9)
    
    # Area distribution
    ax2 = axes[1]
    sns.histplot(df["metraz_m2"], bins=50, kde=True, color="#55A868", alpha=0.7,
                 edgecolor='white', linewidth=0.5, ax=ax2)
    ax2.set_title("Rozkład metrażu (metraz_m2)", fontweight='bold')
    ax2.set_xlabel("Metraż [m²]")
    ax2.set_ylabel("Liczba ofert")
    ax2.axvline(df["metraz_m2"].median(), color='red', linestyle='--', linewidth=1.5,
                label=f'Mediana: {df["metraz_m2"].median():.1f} m²')
    ax2.legend(fontsize=9)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_price_boxplot(df: pd.DataFrame, output_path: str):
    """
    Generates and saves a horizontal boxplot for price.
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.boxplot(df["cena_pln"], vert=False, patch_artist=True,
               boxprops=dict(facecolor='#4C72B0', alpha=0.7),
               medianprops=dict(color='red', linewidth=2),
               flierprops=dict(marker='o', markerfacecolor='#C44E52', markersize=4, alpha=0.5),
               whiskerprops=dict(linewidth=1.5),
               capprops=dict(linewidth=1.5))
    ax.set_title("Boxplot ceny mieszkań (cena_pln)", fontweight='bold', fontsize=14)
    ax.set_xlabel("Cena [PLN]")
    ax.set_yticks([])
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_district_countplot(df: pd.DataFrame, output_path: str):
    """
    Generates and saves a countplot of offers per district.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    order = df["dzielnica"].value_counts().index
    colors = sns.color_palette("husl", len(order))
    sns.countplot(data=df, y="dzielnica", order=order, palette=colors, ax=ax,
                  edgecolor='white', linewidth=0.5)
    ax.set_title("Liczba ofert w każdej dzielnicy", fontweight='bold', fontsize=14)
    ax.set_xlabel("Liczba ofert")
    ax.set_ylabel("Dzielnica")
    
    # Add count labels
    vc = df["dzielnica"].value_counts()
    for i, v in enumerate(vc.values):
        ax.text(v + 2, i, str(v), va='center', fontweight='bold', fontsize=10)
        
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_correlation_heatmap(df: pd.DataFrame, output_path: str) -> pd.DataFrame:
    """
    Generates and saves a correlation heatmap for numerical variables.
    
    Returns:
        pd.DataFrame: The computed correlation matrix.
    """
    df_corr = df.copy()
    if "ma_balkon" in df_corr.columns:
        df_corr["ma_balkon"] = df_corr["ma_balkon"].astype(int)
    if "ma_miejsce_parkingowe" in df_corr.columns:
        df_corr["ma_miejsce_parkingowe"] = df_corr["ma_miejsce_parkingowe"].astype(int)
        
    corr_matrix = df_corr.select_dtypes(include="number").drop(columns=["id_oferty"], errors="ignore").corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                vmin=-1, vmax=1, linewidths=0.5, ax=ax,
                square=True, cbar_kws={"shrink": 0.8})
    ax.set_title("Macierz korelacji zmiennych numerycznych", fontweight='bold', fontsize=14)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return corr_matrix

def plot_scatter_area_price(df: pd.DataFrame, output_path_a: str, output_path_b: str):
    """
    Generates and saves scatter plots showing relationship between area and price.
    """
    # 1. Scatter with year of construction color mapping
    fig, ax = plt.subplots(figsize=(14, 8))
    scatter = ax.scatter(df["metraz_m2"], df["cena_pln"],
                         c=df["rok_budowy"], cmap="viridis", alpha=0.5, s=20, edgecolors='none')
    plt.colorbar(scatter, ax=ax, label="Rok budowy")
    ax.set_title("Metraż vs Cena (kolorowanie: rok budowy)", fontweight='bold', fontsize=14)
    ax.set_xlabel("Metraż [m²]")
    ax.set_ylabel("Cena [PLN]")
    ax.ticklabel_format(style='plain', axis='y')
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path_a), exist_ok=True)
    plt.savefig(output_path_a, dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Scatter with top 6 districts color mapping
    top_districts = df["dzielnica"].value_counts().head(6).index.tolist()
    df_top = df[df["dzielnica"].isin(top_districts)]
    palette = sns.color_palette("husl", len(top_districts))
    
    fig, ax = plt.subplots(figsize=(14, 8))
    for i, dz in enumerate(top_districts):
        subset = df_top[df_top["dzielnica"] == dz]
        ax.scatter(subset["metraz_m2"], subset["cena_pln"],
                   alpha=0.5, s=25, label=dz, color=palette[i])
    ax.set_title("Metraż vs Cena (top 6 dzielnic)", fontweight='bold', fontsize=14)
    ax.set_xlabel("Metraż [m²]")
    ax.set_ylabel("Cena [PLN]")
    ax.ticklabel_format(style='plain', axis='y')
    ax.legend(title="Dzielnica", fontsize=9, title_fontsize=10)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path_b), exist_ok=True)
    plt.savefig(output_path_b, dpi=150, bbox_inches='tight')
    plt.close()

def plot_district_price_boxplot(df: pd.DataFrame, output_path: str):
    """
    Generates and saves a boxplot showing prices per square meter by district.
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    order_dzielnice = df.groupby("dzielnica")["cena_pln_per_m2"].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x="cena_pln_per_m2", y="dzielnica", order=order_dzielnice,
                palette="husl", ax=ax, fliersize=3, linewidth=1.2)
    ax.set_title("Cena za m² w podziale na dzielnice", fontweight='bold', fontsize=14)
    ax.set_xlabel("Cena za m² [PLN/m²]")
    ax.set_ylabel("Dzielnica")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_skewness_comparison(df: pd.DataFrame, skew_before: float, skew_after: float, output_path: str):
    """
    Generates and saves side-by-side histograms comparing price before and after log transform.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Before transform
    sns.histplot(df["cena_pln"], bins=60, kde=True, color="#C44E52", alpha=0.7,
                 edgecolor='white', linewidth=0.5, ax=ax1)
    ax1.set_title(f"Cena PLN (oryginalna)\nSkewness = {skew_before:.4f}", fontweight='bold')
    ax1.set_xlabel("Cena [PLN]")
    ax1.set_ylabel("Liczba ofert")
    
    # After transform
    sns.histplot(df["cena_pln_log"], bins=60, kde=True, color="#55A868", alpha=0.7,
                 edgecolor='white', linewidth=0.5, ax=ax2)
    ax2.set_title(f"Cena PLN (log1p)\nSkewness = {skew_after:.4f}", fontweight='bold')
    ax2.set_xlabel("log1p(Cena)")
    ax2.set_ylabel("Liczba ofert")
    
    plt.suptitle("Porównanie rozkładu ceny: przed i po transformacji logarytmicznej",
                 fontweight='bold', fontsize=15, y=1.02)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
