#python3
import numpy as np
from bs4 import BeautifulSoup
import urllib3
import json
import re
import nltk

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


def format_transcript(transcript):
    """
    Inputs:
        beautifulsoup transcript
    Outputs:
        array/dictionary formatted transcript
    """
    foramtted_transcript = []
    for text in transcript.find_all("text"):
        line = {
                'text'  : text.get_text(),
                'dur'   : text['dur'],
                'start' : text['start']
                }
        foramtted_transcript.append(line)
    return foramtted_transcript

def get_formatted_transcript(vid_id):
    """
    Convience method
    """
    return format_transcript(get_transcript(vid_id))

if __name__ == "__main__":
    # Testing
    tokensDict = {}
    tokens = []
    transcript = get_transcript("SDdXVOD4llU")
    foramtted_transcript = format_transcript(transcript)
    print(foramtted_transcript)
    """
    for text in transcript.find_all("text"):
        toAppend = re.sub("&#39;", "\'", text.get_text())
        toAppend = re.sub("\n", " ", toAppend)
        toAppend = re.sub("[:&%$#@!,.?]", "", toAppend).lower()
        tokens += nltk.word_tokenize(toAppend)
    for word in tokens:
        if word not in tokensDict:
            tokensDict[word] = 1
        else:
            tokensDict[word] += 1
    with open("captions.json", "w") as captionsFile:
        json.dump(tokensDict, captionsFile, indent=4, ensure_ascii=True);
    """
