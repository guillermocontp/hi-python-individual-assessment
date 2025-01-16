# importing functions for data loading and processing 
from data_loading import bigquery_authenticate, load_data, get_token
from src.data_processing import drop_duplicates, convert_to_datetime, merge_chart_audio_features, aggregate_audio_features, merge_chart_track_features, aggregate_track_features, fetch_spotify_data, parse_spotify_data, three_random_songs, fetch_and_parse_spotify_data
import os 
import pandas as pd
from dotenv import load_dotenv
from requests import post, get
import base64
import json

# authenticating to bigquery
client = bigquery_authenticate()

# execute the load_dotenv function to get API key from .env file
load_dotenv()

# authenticating to spotify
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
token = get_token(client_id, client_secret)

# loading data from bigquery
audio_features = load_data(client,'audio_features')
chart_positions = load_data(client, 'chart_positions')
tracks = load_data(client, 'tracks')

# cleaning data 
audio_features_clean = drop_duplicates(audio_features)
tracks_clean = drop_duplicates(tracks)
chart_positions_clean = convert_to_datetime(chart_positions)

# merging chart positions with audio features 
first_merge = merge_chart_audio_features(chart_positions_clean, audio_features_clean)

# merging charts with tracks
second_merge = merge_chart_track_features(first_merge, tracks_clean)

# aggregate data
aggregated_audio_features = aggregate_audio_features(first_merge)
aggregated_track_features = aggregate_track_features(second_merge)

# aggregating data for spotify api call 
song_reference = three_random_songs(chart_positions_clean)
parsed_spotify_data = fetch_and_parse_spotify_data(song_reference)

# create a new folder named "data_backup" in the current directory
folder_name = 'data'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    
# saving clean files in "data"
aggregated_audio_features.to_csv(os.path.join(folder_name, 'audio_data.csv'), index=False)
aggregated_track_features.to_csv(os.path.join(folder_name, 'track_data.csv'), index=False)
parsed_spotify_data.to_csv(os.path.join(folder_name, 'spotify_data.csv'), index=False)