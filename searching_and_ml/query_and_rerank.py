from __future__ import print_function
from __future__ import division
import numpy as np
import json

import httplib2
import os
import sys
import datetime
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
import numpy as np
from bs4 import BeautifulSoup
import re
import nltk
import urllib3
from operator import itemgetter

from sklearn.externals import joblib

from train_model import vectorize_on_training_set

# Key and version data 
DEVELOPER_KEY = "AIzaSyBEuuLWPO0AJIIp7TVGIB1uM_mNiNkMVbw"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Authenticate 
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

"""Returns the top ten search results for the query in the form 
   {video_id:{"thumbnail":thumbnail_url, "title":video title, 
   "description":description, "categoryId":category_id}}"""

def query_search(query):
    search_request = youtube.search().list(part="snippet", q=query, maxResults=10, videoCaption="closedCaption", type="video")
    
    search_response = search_request.execute()
    
    
    search_results = {}
    for search_result in search_response["items"]:
        video_id = search_result["id"]["videoId"]
        thumbnail = search_result["snippet"]["thumbnails"]["default"]["url"]
        title = search_result["snippet"]["title"]
        description = search_result["snippet"]["description"]
        # Need the video response to get the cateogry id for ranking
        video_response = youtube.videos().list(id=video_id, part='snippet').execute()
        category_id = video_response["items"][0]["snippet"]["categoryId"]
        search_results[video_id] = {"thumbnail":thumbnail, "title":title, "description":description, "categoryId":category_id}
    
    return search_results
	

def has_english(vid_id):
    http = urllib3.PoolManager() #init urllib
    resp = http.request('GET', 'http://video.google.com/timedtext',preload_content=False,
                       fields={'type': 'list', 'v': vid_id})
    sub_dir_xml = resp.read()
    resp.close()
    dir_soup = BeautifulSoup(sub_dir_xml)
    eng_track = dir_soup.find(lang_code="en")
    return False if eng_track is None else True

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
        return None
    track_resp = http.request('GET', 'http://video.google.com/timedtext',preload_content=False,
                               fields={'type': 'track',
                                       'v':    vid_id, 
                                       'name': eng_track['name'].encode('unicode-escape'), 
                                       'lang': 'en'})
    transcript_xml = track_resp.read()
    track_resp.close()
    return BeautifulSoup(transcript_xml).transcript

def get_tokens(text):
    text = re.sub("&#39;", "\'", text)
    text = re.sub("\n", " ", text)
    text = re.sub("[:&%$#@!,.?]", "", text)
    return nltk.word_tokenize(text.lower())

def format_transcript(transcript):
    """
    Inputs:
        beautifulsoup transcript
    Outputs:
        array/dictionary formatted transcript
    """
    foramtted_transcript = []
    for text_soup in transcript.find_all("text"):
        text = text_soup.get_text()
        if len(text) > 0:
            line = {
                    'text'  : text,
                    'dur'   : text_soup['dur'] if 'dur' in text_soup else 0,
                    'start' : text_soup['start'] if 'start' in text_soup else 0
                    }
            foramtted_transcript.append(line)
    return foramtted_transcript


def get_flattened_transcript(vid_id):
    transcript = get_transcript(vid_id)
    flat_text = ""
    if transcript is not None:
        for text_soup in transcript.find_all("text"):
            text = text_soup.get_text()
            if len(text) > 0:
                flat_text += (text + " ")
    else:
        return None # The case where we could not get the transcript
    return flat_text[:-1]


def get_formatted_transcript(vid_id):
    """
    Convience method
    """
    transcript = get_transcript(vid_id)
    if transcript is None:
        return None
    return format_transcript(transcript)
	

"""Assign conversationality scores to the videos returned and 
return a list with the video in ascending order of conversationality
score. The final list consists tuple of the form (video_info dictionary, score)."""

def rerank_search_results(model, search_results):
	tfv = joblib.load(r'trained_models/tfv.pkl')
	videos_with_score = [] # contain tuples of video dictionaries and their conversationality score
	for video_id, video_info in search_results.iteritems():
		flattened_transcript = get_flattened_transcript(video_id)
		if flattened_transcript is not None: 
			vectorized_captions = tfv.transform([flattened_transcript]) # using previous vectorizer
			conversationality_score = model.predict(vectorized_captions)
			videos_with_score.append(({video_id : video_info}, conversationality_score[0]))
        
	return sorted(videos_with_score, key=itemgetter(1), reverse=True)
	
def get_classifer():
    return joblib.load('./trained_models/svr.pkl')

if __name__ == "__main__":
	os.chdir(r'C:\Users\Maheer\Dropbox\Cornell Course Materials\Spring 2015\CS 4300\youtube-caption-prediction')
	svr = joblib.load('trained_models/svr.pkl')
	print(rerank_search_results(svr, query_search("soup")))