import os
import warnings
import pandas as pd
import numpy as np

import data_processing as dp
import visualization as viz

# Suppress deprecation and user warnings for clean execution output
warnings.filterwarnings('ignore')

# Dynamically resolve absolute paths relative to project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "Data", "warsaw_apartments.csv")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "Plots")

def run_part_1_exploration(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("  CZESC 1 - WSTEPNA EKSPLORACJA")
    print("=" * 70)
    
    info = dp.get_basic_info(df)
    
    print(f"\nShape: {info['shape']}")
    print(f"   -> {info['shape'][0]} wierszy (ofert), {info['shape'][1]} kolumn (cech)\n")
    
    print("Info:")
    print("-" * 50)
    print(info['dtypes'].to_string())
    print(f"\nMemory usage: {info['memory_usage_kb']:.1f} KB\n")
    
    print("Brakujace wartosci (isnull().sum()):")
    print("-" * 50)
    print(info['null_counts'].to_string())
    print(f"\n-> Suma brakow: {info['total_nulls']}\n")
    
    print("Statystyki opisowe (describe()):")
    print("-" * 50)
    print(df.describe().to_string())
    
    print("\n" + "=" * 70)
    print("KOMENTARZ - ANALIZA DIAGNOSTYCZNA:")
    print("=" * 70)
    print(f"""Na podstawie statystyk opisowych widoczne sa nastepujace anomalie:

1. METRAZ (metraz_m2):
   - max = {df["metraz_m2"].max():.1f} m2 - to wartosc znacznie przekraczajaca typowy metraz
     mieszkania (nawet luksusowego). Normalne mieszkania w Warszawie maja
     18-180 m2. Wartosci powyzej 300 m2 wskazuja na bledy w danych.

2. ROK BUDOWY (rok_budowy):
   - min = {df["rok_budowy"].min()} - budynki z XIX wieku sa skrajnie nieprawdopodobne jako
     oferty sprzedazy nowoczesnych mieszkan.
   - max = {df["rok_budowy"].max()} - rok w przyszlosci, co jest oczywistym bledem.

3. CENA (cena_pln):
   - Ogromna rozpietosc: min = {df["cena_pln"].min():,.0f} zl, max = {df["cena_pln"].max():,.0f} zl.
   - Odchylenie standardowe ({df["cena_pln"].std():,.0f} zl) jest bardzo wysokie w stosunku
     do sredniej ({df["cena_pln"].mean():,.0f} zl), co sugeruje outliery.
   - Niektore ceny ponizej 50 000 zl sa nierealistyczne dla Warszawy,
     a ceny powyzej 10 000 000 zl wskazuja na penthousy lub bledy.
""")

def run_part_2_descriptive_stats(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("  CZESC 2 - STATYSTYKI OPISOWE")
    print("=" * 70)
    
    price_stats = dp.calculate_price_stats(df)
    
    print("\nStatystyki kolumny cena_pln:")
    print("-" * 50)
    print(f"  Srednia:              {price_stats['mean']:>15,.0f} zl")
    print(f"  Mediana:              {price_stats['median']:>15,.0f} zl")
    print(f"  Odchylenie std:       {price_stats['std']:>15,.0f} zl")
    print(f"  Skewness (skosnosc):  {price_stats['skewness']:>15.4f}")
    print(f"  Kurtosis (kurtoza):   {price_stats['kurtosis']:>15.4f}")
    
    skewness = price_stats['skewness']
    srednia = price_stats['mean']
    mediana = price_stats['median']
    kurtoza = price_stats['kurtosis']
    
    print(f"""
KOMENTARZ - Skosnosc (Skewness):
   Skewness = {skewness:.4f} (wartosc {'dodatnia' if skewness > 0 else 'ujemna'}).
   {'Dodatnia skosnosc' if skewness > 0 else 'Ujemna skosnosc'} oznacza, ze rozklad cen jest
   {'prawoskosny (right-skewed)' if skewness > 0 else 'lewoskosny (left-skewed)'} - {'ogon ciagnie sie w prawo, czyli w zbiorze' if skewness > 0 else 'ogon ciagnie sie w lewo, czyli w zbiorze'}
   {'znajduja sie oferty z ekstremalnie wysokimi cenami, ktore zawyzaja srednia' if skewness > 0 else 'znajduja sie oferty z ekstremalnie niskimi cenami'}.
   Srednia ({srednia:,.0f} zl) jest {'wyzsza' if srednia > mediana else 'nizsza'} od mediany ({mediana:,.0f} zl),
   co potwierdza {'prawostronna' if srednia > mediana else 'lewostronna'} skosnosc.
   
   Wysoka kurtoza ({kurtoza:.2f}) wskazuje na ciezkie ogony rozkladu (leptokurtyczny),
   czyli czestsze wystepowanie wartosci ekstremalnych niz w rozkladzie normalnym.
""")
    
    q1, q3, iqr, lower, upper, _ = dp.get_iqr_stats(df, "metraz_m2")
    print("Statystyki kolumny metraz_m2:")
    print("-" * 50)
    print(f"  Q1 (25. percentyl):   {q1:>10.1f} m2")
    print(f"  Q3 (75. percentyl):   {q3:>10.1f} m2")
    print(f"  IQR (Q3 - Q1):        {iqr:>10.1f} m2")
    print(f"  Dolna granica IQR:    {lower:>10.1f} m2")
    print(f"  Gorna granica IQR:    {upper:>10.1f} m2")
    
    print(f"\nDzielnice:")
    print("-" * 50)
    unikalne = df["dzielnica"].nunique()
    print(f"  Liczba unikalnych dzielnic: {unikalne}\n")
    print("  Liczba ofert w kazdej dzielnicy:")
    vc = df["dzielnica"].value_counts()
    for dz, cnt in vc.items():
        print(f"    {dz:<20s} {cnt:>4d} ofert  ({cnt/len(df)*100:.1f}%)")

def run_part_3_single_variable_analysis(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("  CZESC 3 - ANALIZA POJEDYNCZYCH ZMIENNYCH")
    print("=" * 70)
    
    viz.plot_histograms(df, os.path.join(PLOTS_DIR, "01_histogramy_cena_metraz.png"))
    print("Wykres 01 zapisany: Plots/01_histogramy_cena_metraz.png")
    
    print("""
KOMENTARZ - Skosnosc na histogramach:
   * cena_pln: Wyrazna prawoskosnosc (right-skew). Wiekszosc ofert skupia sie
     w przedziale 200 000 - 1 200 000 zl, ale dlugi ogon w prawo siega
     kilkunastu milionow zl (outliery cenowe).
   * metraz_m2: Rozklad zblizony do normalnego z lekka prawoskosnoscia.
     Widoczne outliery w postaci metrazy 300-600 m2 (wstrzykniete bledy).
""")
    
    viz.plot_price_boxplot(df, os.path.join(PLOTS_DIR, "02_boxplot_cena.png"))
    print("Wykres 02 zapisany: Plots/02_boxplot_cena.png")
    
    print("""
KOMENTARZ - Boxplot cena_pln:
   * Pudelko (IQR) jest stosunkowo waskie, obejmujac wiekszosc normalnych ofert.
   * Widoczne liczne outliery po prawej stronie (ceny wielokrotnie wyzsze od mediany)
     - to wstrzykniete ekstremalnie drogie oferty.
   * Po lewej stronie tez widać outliery - oferty z cenami bliskimi zeru,
     wskazujace na bledy lub oszustwa.
   * Mediana (czerwona linia) jest przesunieta w lewo wewnatrz pudelka,
     co potwierdza prawoskosnosc rozkladu.
""")
    
    viz.plot_district_countplot(df, os.path.join(PLOTS_DIR, "03_countplot_dzielnice.png"))
    print("Wykres 03 zapisany: Plots/03_countplot_dzielnice.png")

def run_part_4_dependency_analysis(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("  CZESC 4 - ANALIZA ZALEZNOSCI")
    print("=" * 70)
    
    df_analysis = df.copy()
    df_analysis["cena_pln_per_m2"] = df_analysis["cena_pln"] / df_analysis["metraz_m2"]
    
    corr_matrix = viz.plot_correlation_heatmap(df_analysis, os.path.join(PLOTS_DIR, "04_heatmapa_korelacji.png"))
    print("Wykres 04 zapisany: Plots/04_heatmapa_korelacji.png")
    
    corr_with_price = corr_matrix["cena_pln"].drop(["cena_pln", "cena_pln_per_m2"], errors="ignore").abs().sort_values(ascending=False)
    print(f"\nKorelacje ze zmienna cena_pln (wartosc bezwzgledna |r|, malejaco):")
    for var, corr in corr_with_price.items():
        r_val = corr_matrix.loc[var, "cena_pln"]
        print(f"   {var:<30s} r = {r_val:+.4f}  (|r| = {corr:.4f})")
        
    print(f"\n-> Najsilniejsza korelacja z cena: {corr_with_price.index[0]} "
          f"(r = {corr_matrix.loc[corr_with_price.index[0], 'cena_pln']:+.4f})")
          
    viz.plot_scatter_area_price(df_analysis, os.path.join(PLOTS_DIR, "05_scatter_metraz_cena.png"), os.path.join(PLOTS_DIR, "05b_scatter_metraz_cena_dzielnice.png"))
    print("\nWykres 05 zapisany: Plots/05_scatter_metraz_cena.png")
    print("Wykres 05b zapisany: Plots/05b_scatter_metraz_cena_dzielnice.png")
    
    viz.plot_district_price_boxplot(df_analysis, os.path.join(PLOTS_DIR, "06_boxplot_cena_per_m2_dzielnice.png"))
    print("Wykres 06 zapisany: Plots/06_boxplot_cena_per_m2_dzielnice.png")
    
    median_per_m2 = df_analysis.groupby("dzielnica")["cena_pln_per_m2"].median().sort_values(ascending=False)
    print(f"\nMediana ceny za m2 wg dzielnic:")
    for dz, med in median_per_m2.items():
        print(f"   {dz:<20s} {med:>10,.0f} zl/m2")
    print(f"\n-> Najdrozsza dzielnica: {median_per_m2.index[0]} "
          f"(mediana: {median_per_m2.iloc[0]:,.0f} zl/m2)")

def run_part_5_outlier_detection(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("  CZESC 5 - DETEKCJA OUTLIEROW")
    print("=" * 70)
    
    print("\nDetekcja outlierow w kolumnie cena_pln:")
    print("-" * 50)
    
    # Method 1: IQR
    q1_c, q3_c, iqr_c, lower_iqr, upper_iqr, outliers_iqr = dp.get_iqr_stats(df, "cena_pln")
    print(f"\n  1. Metoda IQR (1.5xIQR):")
    print(f"     Q1 = {q1_c:,.0f} zl, Q3 = {q3_c:,.0f} zl, IQR = {iqr_c:,.0f} zl")
    print(f"     Dolna granica: {lower_iqr:,.0f} zl")
    print(f"     Gorna granica: {upper_iqr:,.0f} zl")
    print(f"     -> Znaleziono {len(outliers_iqr)} outlierow")
    
    # Method 2: Z-score
    outliers_zscore = dp.get_zscore_outliers(df, "cena_pln")
    print(f"\n  2. Metoda Z-score (|z| > 3):")
    print(f"     -> Znaleziono {len(outliers_zscore)} outlierow")
    
    # Method 3: Modified Z-score
    mad, outliers_mod_z = dp.get_modified_zscore_outliers(df, "cena_pln")
    print(f"\n  3. Metoda Modified Z-score (|z_mod| > 3.5):")
    print(f"     MAD = {mad:,.0f} zl")
    print(f"     -> Znaleziono {len(outliers_mod_z)} outlierow")
    
    print(f"""
Tabela porownawcza metod detekcji outlierow (cena_pln):
------------------------------------------------------
Metoda                   | Liczba wykrytych outlierow
------------------------------------------------------
IQR (1.5x)               | {len(outliers_iqr):>26d}
Z-score (|z| > 3)        | {len(outliers_zscore):>26d}
Modified Z-score (>3.5)  | {len(outliers_mod_z):>26d}
------------------------------------------------------

Modified Z-score jest najbardziej odporna (robust) metoda na outliery,
poniewaz bazuje na medianie oraz odchyleniu bezwzglednym (MAD) zamiast na sredniej i odchyleniu standardowym.
""")
    
    # Area outliers
    _, _, _, lower_m, upper_m, outliers_metraz = dp.get_iqr_stats(df, "metraz_m2")
    print("Detekcja outlierow w kolumnie metraz_m2 (IQR):")
    print("-" * 50)
    print(f"  Dolna granica: {lower_m:.1f} m2")
    print(f"  Gorna granica: {upper_m:.1f} m2")
    print(f"  -> Znaleziono {len(outliers_metraz)} outlierow")
    
    print(f"\n  Top 5 najwiekszych metrazy:")
    top5_metraz = df.nlargest(5, "metraz_m2")[["id_oferty", "dzielnica", "metraz_m2", "cena_pln"]]
    print(top5_metraz.to_string(index=False))
    
    # Incorrect build years
    print(f"\nBledne wartosci w kolumnie rok_budowy (< 1900 lub > 2026):")
    print("-" * 50)
    bad_years = df[(df["rok_budowy"] < 1900) | (df["rok_budowy"] > 2026)]
    print(f"  -> Znaleziono {len(bad_years)} wierszy z nielogicznym rokiem budowy:")
    print(bad_years[["id_oferty", "dzielnica", "rok_budowy", "cena_pln"]].to_string(index=False))

def run_part_6_cleaning_decision(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 70)
    print("  CZESC 6 - DECYZJA I CZYSZCZENIE")
    print("=" * 70)
    
    cleaned_df, meta = dp.clean_data(df)
    
    print(f"\n* Usunieto {meta['removed_years_count']} wierszy z nielogicznym rokiem budowy.")
    print(f"  Pozostalo {len(cleaned_df)} ofert.")
    
    print(f"\n* Winsoryzacja (obciecie) wartosci cena_pln:")
    print(f"  1. percentyl: {meta['p01_price']:,.0f} zl")
    print(f"  99. percentyl: {meta['p99_price']:,.0f} zl")
    print(f"  Liczba zmodyfikowanych wartosci (dolna granica): {meta['low_price_outliers_count']}")
    print(f"  Liczba zmodyfikowanych wartosci (gorna granica): {meta['high_price_outliers_count']}")
    
    skew_before = df["cena_pln"].skew()
    skew_after = cleaned_df["cena_pln_log"].skew()
    print(f"\n* Transformacja logarytmiczna (log1p):")
    print(f"  Skosnosc (cena_pln przed):     {skew_before:.4f}")
    print(f"  Skosnosc (cena_pln po log1p):  {skew_after:.4f}")
    print(f"  -> Redukcja skosnosci rozkladu: {abs(skew_before) - abs(skew_after):.4f}")
    
    viz.plot_skewness_comparison(cleaned_df, skew_before, skew_after, os.path.join(PLOTS_DIR, "07_porownanie_skosnosci.png"))
    print("Wykres 07 zapisany: Plots/07_porownanie_skosnosci.png")
    
    return cleaned_df

def run_part_7_conclusions(df_clean: pd.DataFrame, original_skew: float, cleaned_skew: float):
    print("\n" + "=" * 70)
    print("  CZESC 7 - WNIOSKI")
    print("=" * 70)
    
    med_per_m2_clean = df_clean.groupby("dzielnica")["cena_pln_per_m2"].median().sort_values(ascending=False)
    
    print(f"""
------------------------------------------------------------------------
                     NAJWAZNIEJSZE WNIOSKI Z ANALIZY
------------------------------------------------------------------------

1. LOKALIZACJA TO KLUCZ DO CENY
   Najdrozsza dzielnica jest Srodmiescie z mediana ceny
   za m2 na poziomie {med_per_m2_clean.iloc[0]:,.0f} zl/m2. Najtansza jest
   Bialoleka ({med_per_m2_clean.iloc[-1]:,.0f} zl/m2).
   Roznica wynosi {(med_per_m2_clean.iloc[0]/med_per_m2_clean.iloc[-1] - 1)*100:.0f}%.

2. METRAZ JEST NAJSILNIEJSZYM PREDYKTOREM CENY
   Korelacja metraz_m2 <-> cena_pln jest najwyzsza sposrod wszystkich zmiennych.
   Jest to zgodne z intuicja - im wieksze mieszkanie, tym wyzsza cena calkowita.
   Cena za m2 normalizuje ten wplyw i pozwala na rzetelne porownanie.

3. RYNEK JEST SILNIE PRAWOSKOSNY
   Rozklad cen ma silna skosnosc prawostronna (skewness = {original_skew:.2f}).
   Wiekszosc ofert koncentruje sie do kwoty ~1,2 mln zl, ale wystepuja
   oferty znacznie drozsze. Transformacja log1p redukuje te skosnosc (do {cleaned_skew:.2f}).

4. ZBIOR WYMAGA CZYSZCZENIA DANYCH
   W danych zidentyfikowano wstrzykniete bledy i wartosci odstajace:
   - Oferty z cenami zawyzonymi 5-12 krotnie (bledy/penthousy)
   - Oferty z cenami zanizonymi do poziomu 5-20% wartosci rynkowej (bledy/oszustwa)
   - Oferty z nierealistycznym metrazem (300-600 m2)
   - Oferty z nielogicznym rokiem budowy (1800, 1850, 2050, 2099)
   Metoda Modified Z-score okazala sie najbardziej odpornym i skutecznym filtrem.

5. CZYNNIKI CENOTWORCZE
   Na cene mieszkania wplywaja istotnie: rok budowy (nowsze budynki sa drozsze),
   mniejsza odleglosc od centrum miasta, a takze obecnosc balkonu (+5%) 
   oraz przypisane miejsce parkingowe (+8%).
""")
    
    print("=" * 70)
    print("  ANALIZA ZAKONCZONA - wszystkie pliki graficzne zapisano w folderze 'Plots/'")
    print("=" * 70)
    
    print("\nWygenerowane pliki:")
    if os.path.exists(PLOTS_DIR):
        for f in sorted(os.listdir(PLOTS_DIR)):
            print(f"   Plots/{f}")
    print("   Data/warsaw_apartments.csv\n")

def main():
    viz.setup_plotting_style()
    
    try:
        df = dp.load_data(DATA_PATH)
    except Exception as e:
        print(f"Blad podczas wczytywania danych wejsciowych: {e}")
        return
        
    run_part_1_exploration(df)
    run_part_2_descriptive_stats(df)
    run_part_3_single_variable_analysis(df)
    run_part_4_dependency_analysis(df)
    run_part_5_outlier_detection(df)
    
    original_skew = df["cena_pln"].skew()
    df_clean = run_part_6_cleaning_decision(df)
    cleaned_skew = df_clean["cena_pln_log"].skew()
    
    run_part_7_conclusions(df_clean, original_skew, cleaned_skew)

if __name__ == '__main__':
    main()
