#python3
import numpy as np
from bs4 import BeautifulSoup
import urllib3


def get_transcript(vid_id):
    """
    Input: 
        vid_id: Youtube video id
    Output:
        transcript: Beautiful soup xml object of transcipt
        of the format:
        <transcript>
            <text dur="DURATION_TIME" start="START_TIME">
                SPOKEN TEXT
            </text>
        </transcript>
    """
    http = urllib3.PoolManager() #init urllib
    resp = http.request('GET', 'http://video.google.com/timedtext',preload_content=False,
                       fields={'type': 'list', 'v': vid_id})
    sub_dir_xml = resp.read()
    resp.close()
    dir_soup = BeautifulSoup(sub_dir_xml)
    eng_track = dir_soup.find(lang_code="en")
    if eng_track is None:
        print('Skipped because no native subtitles in english')
        print('Could modify code to translate from other langauge')
        print(dir_soup.find_all('track'))
        return None
    track_resp = http.request('GET', 'http://video.google.com/timedtext',preload_content=False,
                       fields={'type': 'track',
                               'v':    vid_id, 
                               'name': eng_track['name'], 
                               'lang': eng_track['lang_code']})
    transcript_xml = track_resp.read()
    track_resp.close()
    return BeautifulSoup(transcript_xml).transcript

if __name__ == "__main__":
    # Testing
    transcript = get_transcript("SDdXVOD4llU")
    if transcript is not None:
        print(transcript.prettify())