from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()
fetched_transcript = ytt_api.fetch("7Ron6MN45LY")

for snippet in fetched_transcript:
    print(snippet.text)