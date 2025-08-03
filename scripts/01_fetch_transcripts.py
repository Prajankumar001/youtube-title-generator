import json
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.proxies import WebshareProxyConfig
from dotenv import load_dotenv
import os

load_dotenv()

proxy_config = WebshareProxyConfig(
    proxy_username=os.getenv("PROXY_USERNAME"),
    proxy_password=os.getenv("PROXY_PASSWORD"),
)

def get_video_data_for_ml(youtube_urls):
    """
    Fetches the title and a detailed, timestamped transcript for a list of 
    YouTube video URLs, formatted for machine learning applications.

    Args:
        youtube_urls (list): A list of strings, where each string is a 
                             URL to a YouTube video.

    Returns:
        str: A JSON formatted string containing the title and a list of 
             transcript snippets (with text, start, and duration) for each video.
             Returns an empty list in JSON format if no data is fetched.
    """
    all_videos_data = []
    transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)

    for url in youtube_urls:
        try:
            yt = YouTube(url)
            video_id = yt.video_id
            video_title = yt.title
            
            print(f"Processing: '{video_title}' (ID: {video_id})")

            try:
                transcript_list = transcript_api.fetch(video_id)
                transcript_snippets_list = []
                for snippet in transcript_list:
                    print(snippet)
                    # Each snippet in the fetched transcript is a FetchedTranscriptSnippet object
                    # Access attributes directly instead of using subscript notation
                    transcript_snippets_list.append({
                        'text': snippet.text,
                        'start': snippet.start,
                        'duration': snippet.duration
                    })

                # --- Structure the data for this video ---
                video_data = {
                    "url": url,
                    "title": video_title,
                    "video_id": video_id,
                    "transcript_snippets": transcript_snippets_list
                }
                all_videos_data.append(video_data)

            except (NoTranscriptFound, TranscriptsDisabled):
                print(f"  - WARNING: Could not find a transcript for video: {url}")
                continue

        except Exception as e:
            print(f"  - ERROR: An error occurred with URL {url}: {e}")
            continue
    
    return json.dumps(all_videos_data, indent=4)

# --- Example Usage ---
if __name__ == "__main__":
    video_links = [
        'https://www.youtube.com/watch?v=DUHQ_lLD0n0&pp=ygUJIkkgYnVpbHQi',
        'https://www.youtube.com/watch?v=Na_4ZWIJhyw&pp=ygUJIkkgYnVpbHQi',
        'https://www.youtube.com/watch?v=8W6UgN7SM64&t=17s&pp=ygUOIkkgcHJvZ3JhbW1lZCI%3D',
        'https://www.youtube.com/watch?v=bt8BwJs2JWI&pp=ygUOIkkgcHJvZ3JhbW1lZCI%3D',
        'https://www.youtube.com/watch?v=NTwQYZXB6vM&pp=ygUOIkkgcHJvZ3JhbW1lZCI%3D',
        'https://www.youtube.com/watch?v=N3tRFayqVtk&pp=ygUOIkkgcHJvZ3JhbW1lZCI%3D',
        'https://www.youtube.com/shorts/PL0cR-C2wkg',
        'https://www.youtube.com/shorts/-eA-OXXD-Dc',
        'https://www.youtube.com/shorts/lDv32d7oWrA'
    ]

    json_output = get_video_data_for_ml(video_links)

    print("\n--- Machine Learning Dataset (JSON Output) ---")
    print(json_output)

    output_filename = './../data/raw/transcripts_raw.json'
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"\nSuccessfully saved structured data to {output_filename}")
    except Exception as e:
        print(f"\nError saving to file: {e}")
