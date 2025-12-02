from tinydb import TinyDB, Query
from datetime import datetime
from typing import Dict, List

db = TinyDB('cube_db.json')

def init_database():
    tables = db.tables()
    
    if 'transcripts' not in tables:
        db.table('transcripts')

def get_transcript_by_id(video_id: str) -> Dict | None:
    """Checks if a transcript for a given video ID already exists."""
    transcripts_table = db.table('transcripts')
    Transcript = Query()
    result = transcripts_table.search(Transcript.video_id == video_id)
    return True if result else None

def add_transcript(
    video_id: str,
    title: str,
    channel: str,
    transcript_text: str,
    url: str = ""
) -> int:
    transcripts_table = db.table('transcripts')
    return transcripts_table.insert({
        'video_id': video_id,
        'title': title,
        'channel': channel,
        'transcript': transcript_text,
        'url': url,
        'added_date': datetime.now().isoformat(),
        'indexed': True
    })

def get_transcripts_by_topic(topic: str) -> List[Dict]:
    transcripts_table = db.table('transcripts')
    Transcript = Query()
    return transcripts_table.search(Transcript.topic == topic)

def search_transcripts(keyword: str) -> List[Dict]:
    transcripts_table = db.table('transcripts')
    Transcript = Query()
    return transcripts_table.search(
        (Transcript.title.test(lambda x: keyword.lower() in x.lower())) |
        (Transcript.transcript.test(lambda x: keyword.lower() in x.lower()))
    )

def get_all_transcripts() -> List[Dict]:
    transcripts_table = db.table('transcripts')
    return transcripts_table.all()

def get_transcript_by_video_id(video_id: str) -> Dict:
    transcripts_table = db.table('transcripts')
    Transcript = Query()
    result = transcripts_table.search(Transcript.video_id == video_id)
    return result[0] if result else None

def get_database_summary() -> Dict:
    return {'transcripts': len(db.table('transcripts').all())}

init_database()
