import pandas as pd
import glob
from pathlib import Path

def create_df():
    path_name = str(Path("data/raw") / "billboard_top_100_songs_*.json")
    file_list=glob.glob(path_name)
    df_list=[pd.read_json(file) for file in file_list]
    df=pd.concat(df_list, ignore_index=True)
    
    df2=pd.read_csv(Path("data/raw") / "spotify_audio_features.csv")

    normalize_text(df, df2, merge_df)


def normalize_text(df, df2, merge_df):
    df = df.copy()
    df2 = df2.copy()

    df['title'] =  df['title'].str.replace('"', '', regex=False).str.lower().str.strip()
    df['artists'] = df['artist'].str.replace(",|with|featuring|and|&",",",regex=True).str.lower().str.strip()
    
    df2['title'] = df2['title'].str.lower().str.strip()
    df2['artists'] = df2['artist'].str.replace(",|with|featuring|and|x|feat|&",",",regex=True).str.lower().str.strip()

    merge_df(df, df2)



def merge_df(df,df2):
    output_dir = Path("data/processed")

    merged_df = pd.merge(df, df2, on=['title', 'artists'], how='left')

    columns_to_keep = [
        'year', 
        'rank', 
        'title', 
        'artists', 
        'track_id', 
        'album_name', 
        'popularity', 
        'track_genre',
        'danceability', 
        'energy', 
        'loudness', 
        'tempo', 
        'valence', 
        'speechiness'
    ]
    
    # Filter the merged dataset down to just those targeted fields
    final_df = merged_df[columns_to_keep]

    final_df.to_csv(output_dir / "merged_data.csv", index=False)

    total_chart_songs = len(df)
    matched_songs = final_df['track_id'].notna().sum() 
    match_percentage = (matched_songs / total_chart_songs) * 100 if total_chart_songs > 0 else 0

    print("=== Merge Coverage Report ===")
    print(f"Total Chart Songs: {total_chart_songs}")
    print(f"Successfully Matched: {matched_songs}")
    print(f"Match Percentage: {match_percentage:.2f}%")


if __name__ == "__main__":
    create_df()