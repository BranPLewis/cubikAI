from smolagents import Tool
import cube_db

class LocalTranscriptSearchTool(Tool):
    name = "local_transcript_search"
    description = (
            "Searches the local database of previously saved YouTube video transcripts. "
            "Use this tool to find specific Rubik's Cube algorithms, steps, or advice "
            "that has already been indexed from videos."
            )
    inputs = {
            "keyword": {
                "type": "string",
                "description": "The specific technique, step, or term to search for (e.g., 'white cross', 'PLL', 'corner swap').",
                }
            }
    output_type = "string"
    def forward(self, keyword:str) -> str:
        results = cube_db.search_transcripts(keyword)
        if not results:
            return f"No local transcripts found containing the keyword '{keyword}'."
        output = []
        for i,r in enumerate(results,1):
            title = r.get('title','Unknown Title')
            channel = r.get('channel', 'Unknown Channel')
            text = r.get('transcript', '')

            output.append(f"--- Result {i} ---\nTitle: {title}\nChannel: {channel}\nContent Snippet: {text}\n")
        return "\n".join(output)
