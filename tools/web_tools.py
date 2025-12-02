import re, dotenv
from smolagents import Tool, DuckDuckGoSearchTool
from youtube_transcript_api import YouTubeTranscriptApi as YTA
from typing import List, Dict, Optional
from cube_db import add_transcript
from googleapiclient.discovery import build

g_dotenv_loaded = False

def getenv(variable: str) -> str:
    global g_dotenv_loaded
    if not g_dotenv_loaded:
        dotenv.load_dotenv()
        g_dotenv_loaded = True
    return dotenv.os.getenv(variable)

def get_api_key(key) -> str:
    api_key = getenv(key)
    if not api_key:
        msg =  (f"{key} not set. "
                f"Be sure .env has {key}. "
                f"Be sure dotenv.load_dotenv() is called at initialization.")
        raise ValueError(msg)
    return api_key

def fetch_video_metadata(video_id: str) -> Dict[str, str]:
    try:
        youtube = build('youtube', 'v3', developerKey=get_api_key("YOUTUBE_API_KEY"))
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        if response and response.get('items'):
            snippet = response['items'][0]['snippet']
            title = snippet['title']
            channel_name = snippet['channelTitle']
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            return {
                "video_id": video_id,
                "title": title,
                "channel": channel_name,
                "url": url,
            }
    except Exception as e:
        print(f"YouTube API error: {e}. Using fallback metadata.")
    
    # Fallback: Return basic metadata if API fails
    return {
        "video_id": video_id,
        "title": f"YouTube Video - {video_id}",
        "channel": "Unknown Channel",
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }
        
class YoutubeTranscriptSearchTool(Tool):
    name = "Youtube_video_transcript_search"
    description = (
        "Searches through youtube videos realated to solving rubik's cubes, Video ID's."
    )
    # FIX: Corrected input description
    inputs = {"query": {"type":"string","description":"The search query to find YouTube videos."}}
    output_type = "string"

    def __init__(self, sites: List[str] = None):
        super().__init__()
        self._ddgs = DuckDuckGoSearchTool()
        if sites is None:
            sites = ["https://www.youtube.com"]
        self.sites = sites

    def forward(self, query: str, max_results: int = 2) -> dict:
        site_filter = [f"site:{site}" for site in self.sites]
        site_query = f"({' OR '.join(site_filter)})"
        full_query = f"{site_query} {query}"

        try:
            results = self._ddgs(full_query)
        except Exception as e:
            return {"error": f"Search engine error: {str(e)}"}

        if not results:
            return {"error": "No results found."}

        video_id_regex = r"(?:v=|\/embed\/|\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})"
        ids = []

        if isinstance(results, str):
            ids = re.findall(video_id_regex, results)
        elif isinstance(results, list):
            for result in results:
                if isinstance(result, dict):
                    url = result.get("href") or result.get("url")
                elif isinstance(result, str):
                    url = result
                else:
                    url = None
                if url:
                    match = re.search(video_id_regex, url)
                    if match:
                        ids.append(match.group(1))
        else:
            ids = re.findall(video_id_regex, str(results))

        ids = list(set(ids))[:max_results]
        if not ids:
            return {"error": "No video IDs found."}

        transcripts = {}
        for vid in ids:
            try:
                tro = YTA()
                transcript_list = tro.fetch(vid)
                transcript_text = " ".join([entry.text for entry in transcript_list])
                transcripts[vid] = transcript_text
            except Exception as e:
                transcripts[vid] = f"ERROR: {str(e)}"
        return {"video_ids": ids, "transcripts": transcripts}

class YoutubeTranscriptFetchTool(Tool):
    name = "Youtube_video_transcript_fetch"
    description = (
        "Fetches the transcript and essential metadata (title, channel) for a given YouTube video ID. "
        "The output is a string summarizing the operation."
    )
    inputs = {"video_id": {"type":"string","description":"YouTube Video ID"}}
    output_type = "string"

    def __init__(self):
        super().__init__()

    def forward(self, video_id: str) -> str:
        metadata = fetch_video_metadata(video_id)
        
        try:
            transcript_list = YTA.fetch(video_id)
            transcript_text = " ".join([f"[{entry['start']:.0f}s] {entry['text']}" for entry in transcript_list])
        except Exception as e:
            # FIX 1: Return a string on error
            return f"ERROR: Failed to fetch transcript for video ID {video_id}. Reason: No transcript available or YTA error: {str(e)}"
        
        try:
            inserted_id = add_transcript(
                video_id=metadata["video_id"],
                title=metadata["title"],
                channel=metadata["channel"],
                transcript_text=transcript_text,
                url=metadata["url"]
            )
            # SUCCESS: Returns a string (already correct)
            return f"SUCCESS: Transcript for '{metadata['title']}' inserted into DB with ID: {inserted_id}."
        except Exception as e:
            error_msg = f"Database insertion failed: {str(e)}"
            print(f"ERROR: {error_msg}")
            # FIX 2: Return a string on database error
            return f"ERROR: Database insertion failed for '{metadata['title']}' ({video_id}). Reason: {error_msg}"