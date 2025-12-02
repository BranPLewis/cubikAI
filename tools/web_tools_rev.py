from smolagents import Tool
from youtube_transcript_api import YouTubeTranscriptApi as YTA
from youtube_transcript_api.proxies import WebshareProxyConfig
from youtube_search import YoutubeSearch
import cube_db  # Importing your provided database module

class YoutubeTranscriptSearchTool(Tool):
    name = "youtube_transcript_search"
    description = (
        "Searches YouTube for a query, retrieves transcripts for the top 2 videos, "
        "saves them to the local database, and returns the transcript text for analysis."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "The topic or keywords to search for on YouTube.",
        }
    }
    output_type = "string"

    def forward(self, query: str) -> str:
        # 1. Search for the top 2 videos
        # We use YoutubeSearch to get the ID and Metadata
        results = YoutubeSearch(query, max_results=2).to_dict()
        
        combined_output = []
        
        for video in results:
            video_id = video['id']
            title = video['title']
            # 'channel' key sometimes varies in API versions, usually 'channel' or 'uploader'
            channel = video.get('channel') or video.get('uploader') or "Unknown"
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            try:
                # 2. Fetch Transcript
                # Using the logic from your snippet: fetch list, then join text
                yto = YTA()
                transcript_list = yto.fetch(video_id)
                for snippet in transcript_list:
                    print(snippet.text)
                transcript_text = " ".join([entry.text for entry in transcript_list])
                
                # 3. Insert into TinyDB using your cube_db module
                cube_db.add_transcript(
                    video_id=video_id,
                    title=title,
                    channel=channel,
                    transcript_text=transcript_text,
                    url=url
                )
                
                combined_output.append(f"Video Title: {title}\nTranscript: {transcript_text}")
                
            except Exception as e:
                # Handle cases where transcripts are disabled or auto-generated text fails
                combined_output.append(f"Failed to get transcript for video '{title}' (ID: {video_id}). Error: {str(e)}")

        return "\n\n".join(combined_output)