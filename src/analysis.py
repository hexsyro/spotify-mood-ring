import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def read_and_sort():
    df=pd.read_csv('data/processed/merged_data.csv')

    #sort the dataframe by year
    df.sort_values(by=['year'], inplace=True)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

#melting and pivoting
def valence_by_genre(df):
    pivoted = df.pivot_table(index='year', columns='track_genre', values='valence', aggfunc='mean').round(3)

    pivoted = pivoted.reset_index()
    melted = pivoted.melt(id_vars='year', var_name='track_genre', value_name='valence').dropna()
    melted.to_csv('data/processed/valence_by_genre_data.csv', index=False)
    df1=melted
    return df1

#calculating
def valence_analysis(df1):
    valence_mean=df1['valence'].rolling(3).mean().to_numpy()

    valence_zscore=(df1['valence']-valence_mean)/df1['valence'].rolling(3).std().to_numpy()

    outliners = np.abs(valence_zscore) > 1 #if set to 2 it becomes Index: []
    outliners = df1[outliners]

    return valence_mean, valence_zscore, outliners

def correlation_analysis(df):
    correlation_matrix = np.corrcoef([df['valence'], df['energy'], df['danceability'], df['tempo']])
    df_correlation_matrix = pd.DataFrame(correlation_matrix, index=['valence', 'energy', 'danceability', 'tempo'], columns=['valence', 'energy', 'danceability', 'tempo'])
    return df_correlation_matrix

#charting
def plot_by_genre(df1):
    os.makedirs('outputs', exist_ok=True)
    
    plt.figure(figsize=(12, 7))
    
    top_genres = df1['track_genre'].value_counts().head(6).index  # limit to avoid clutter
    
    for genre in top_genres:
        genre_data = df1[df1['track_genre'] == genre].sort_values('year')
        plt.plot(genre_data['year'], genre_data['valence'], marker='o', label=genre, alpha=0.8)
    
    plt.title('Valence Trend by Genre Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=11)
    plt.ylabel('Valence (musical positivity, 0–1)', fontsize=11)
    plt.legend(title='Genre', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig('outputs/valence_by_genre_lines.png', dpi=150)
    plt.show()
    

def main():
    print("======= READING AND SORTING =======")
    df = read_and_sort()
    print(f"Loaded {len(df)} songs spanning {df['year'].min()}–{df['year'].max()}\n")

    df1 = valence_by_genre(df)
    print(f"Aggregated to {len(df1)} year-genre combinations")
    print(df1.head(5))
    print()

    print("======= CALCULATING =======")
    valence_mean, valence_zscore, outliners = valence_analysis(df1)

    df1_display = df1.copy()
    df1_display['rolling_mean'] = valence_mean
    df1_display['zscore'] = valence_zscore
    print("Valence with rolling mean & z-score (first 10 rows):")
    print(df1_display[['year', 'track_genre', 'valence', 'rolling_mean', 'zscore']].head(10))
    print()

    print(f"Outliers found: {len(outliners)} year-genre combos with |z| > 1")
    if len(outliners) > 0:
        print(outliners[['year', 'track_genre', 'valence']].head(10))
    print()

    correlation_matrix = correlation_analysis(df)
    print("Correlation matrix (valence, energy, danceability, tempo):")
    print(correlation_matrix)
    print()

    print("======= ANALYSIS CHARTS =======")
    plot_by_genre(df1)
    print("Chart saved to outputs/valence_by_genre_lines.png")
    print()
    print()
    print("1. How does average song 'valence' (musical positivity) trend year-over-year within each genre?\n")

    def valence_trend_over_year(df1):
        for genre in df1['track_genre'].unique():
            genre_data = df1_display[df1_display['track_genre'] == genre].sort_values('year')
            if len(genre_data) >= 3:
                trend = genre_data['rolling_mean'].iloc[-1] - genre_data['rolling_mean'].iloc[0]
                direction = "increased" if trend > 0 else "decreased"
                print(f"{genre}: valence {direction} by {abs(trend):.3f} from {genre_data['year'].iloc[0]} to {genre_data['year'].iloc[-1]}")
    valence_trend_over_year(df1)
    
    print()
    print()
    print("2. Which genres show the widest mood swings across different years?\n")

    def genre_mood_swing(df1):
        swings = df1.groupby('track_genre')['valence'].std().sort_values(ascending=False)
        print(swings.head())
    genre_mood_swing(df1)
    
    print()
    print()
    print("3. Are there outlier year-genre combos that break the trend?\n")

    def year_genre_combo():
        print(f"Found {len(outliners)} outlier combinations (|z| > 1)")
        print(outliners.sort_values('valence', ascending=False).head())  # happiest outliers
        print(outliners.sort_values('valence', ascending=True).head())   # saddest outliers
    year_genre_combo()
    
    print()
    print()
    print("4. Is there a correlation between tempo/energy/danceability and valence?\n")

    def corr():
        print(correlation_matrix)
    corr()

if __name__ == '__main__':
    main()