'''
Come our functions to output one json file
'''

from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from bs4 import BeautifulSoup
import httplib2
import os
import sys
import re
import nltk
import json
import urllib	
import numpy as np
import urllib3
import json
import re
import nltk

# Assign file of video ids to parse
videolist = "./video_id_data/VICE2.txt"

# Retrives the transcript (tokenized) given a videoId
def get_transcript_tokens(vid_id):
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
	resp = http.request('GET', 'http://video.google.com/timedtext',preload_content=False, fields={'type': 'list', 'v': vid_id})
	sub_dir_xml = resp.read()
	resp.close()
	dir_soup = BeautifulSoup(sub_dir_xml)
	eng_track = dir_soup.find(lang_code="en")
	if eng_track is None:
		# print('Skipped because no native subtitles in english')
		# print('Could modify code to translate from other langauge')
		# print(dir_soup.find_all('track'))
		return None

	track_resp = http.request('GET', 'http://video.google.com/timedtext',
		preload_content=False, 
		fields={'type': 'track',
				'v'   : vid_id, 
				'name': eng_track['name'], 
				'lang': eng_track['lang_code']
				})
	transcript_xml = track_resp.read()
	track_resp.close()
	transcript =  BeautifulSoup(transcript_xml).transcript

	tokensDict = {}
	tokens = []
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

	return tokensDict

# Retrieves the metadata of a video
def valid_constraints(youtube, video_id):
	video_info_list = youtube.videos().list(
		part="topicDetails, snippet, contentDetails, statistics",
		id = video_id
	).execute()
	video_info = video_info_list["items"][0]
	duration_string = video_info["contentDetails"]["duration"]
	captions_enabled = video_info["contentDetails"]["caption"]
	num_views_string = video_info["statistics"]["viewCount"]
	num_comments = video_info["statistics"]["commentCount"]
	publish_date = video_info["snippet"]["publishedAt"]
	topics = video_info["topicDetails"]["topicIds"] 

	return duration_string, num_views_string, num_comments, publish_date, topics

def get_comment_threads(data, youtube, videoId, nextPageToken):
	length = len(data)
	results = youtube.commentThreads().list(
		part="snippet",
		videoId=videoId,
		textFormat="plainText",
		maxResults=100,
		pageToken=nextPageToken
	).execute()

	for item in results["items"]:
		comment_id = item["id"]
		comment = item["snippet"]["topLevelComment"]
		author = comment["snippet"]["authorDisplayName"]
		text = re.sub('\W+',' ', comment["snippet"]["textDisplay"][:-1])
		date = comment["snippet"]["updatedAt"]
		replies = item["snippet"]["totalReplyCount"]

		data[comment_id] = {
			"id": comment_id,
			"author": author,
			"text": text,
			"date": date,
			"replies": replies
		}

	if (length == len(data)):
		return data, None
	else:
		return data, results["nextPageToken"]

def comments_list(youtube, parentId): 
	results = youtube.comments().list(
		part="snippet",
		parentId=parentId,
		textFormat="plainText",
	).execute()
	comments = []
	for item in results["items"]:
		comments += nltk.word_tokenize(item["snippet"]["textDisplay"].lower())
	return comments, len(results)


def get_all_comments(youtube, videoId):

	# Get first results
	data, nextPage = get_comment_threads({}, youtube, videoId, None)

	while nextPage != None:
		# print(len(data))
		data, nextPage = get_comment_threads(data, youtube, videoId, nextPage)

	wordList = []
	repliesCount = 0
	commentSize = len(data)
	topCommentSize = len(data)
	avgReplies = 0

	for each in data:
		tokens = nltk.word_tokenize((data[each])["text"].lower())
		wordList += tokens
		if data[each]["replies"] != 0:
			avgReplies += data[each]["replies"]
			nestedComments, nestedCommentsLen = comments_list(youtube, data[each]["id"])
			wordList += nestedComments
			commentSize += nestedCommentsLen

	avgReplies = avgReplies / topCommentSize
	avgWords = len(wordList) / commentSize

	return avgReplies, avgWords

if __name__ == "__main__":

	# Authenticate
	YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
	YOUTUBE_API_SERVICE_NAME = "youtube"
	YOUTUBE_API_VERSION = "v3"
	DEVELOPER_KEY = "AIzaSyBt4F-EsA1jsLMWERsivgufl0Wn7nwuZ9o"

	# Assign
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

	with open(videolist) as f:
		videoIds = [line.strip() for line in f.readlines()]		

	videoDict = {}
	for index, videoId in enumerate(videoIds):
		avgReplies, avgWords = get_all_comments(youtube, videoId)
		captions = get_transcript_tokens(videoId)
		videoLength, numberViews, numberComments, publishDate, topics = valid_constraints(youtube, videoId)

		json_format = {
			"videoLength" : videoLength, 
			"numberViews" : numberViews,
			"numberComments" : numberComments,
			"avgRepliesPerComment" : avgReplies,
			"avgWordsPerComment": avgWords,
			"publishDate" : publishDate,
			"topics" : topics,
			"captions" : captions
		}

		videoDict[videoId] = json_format


	with open('data.json', 'w') as commentfile:
		json.dump(videoDict, commentfile, sort_keys = True, indent = 4, ensure_ascii=True)



