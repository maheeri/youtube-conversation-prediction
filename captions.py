from __future__ import print_function
from __future__ import division
import numpy as np
from bs4 import BeautifulSoup
import urllib3
import urlparse

def get_transcript(url):
    """
    Input: 
        url: Youtube video url
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
    par = urlparse.parse_qs(urlparse.urlparse(url).query)
    vid_id = par['v'][0]
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
    transcript = get_transcript("https://www.youtube.com/watch?v=SDdXVOD4llU")
    print(transcript.prettify())