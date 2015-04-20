#!/usr/bin/python

# Usage example:
# python comment_threads.py --channelid='<channel_id>' --videoid='<video_id>' --text='<text>'

import httplib2
import os
import sys
import re
import nltk

from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import json
import urllib	

# Assign file of video ids to parse
videolist = "./video_id_data/VICE2.txt"

# Authenticate
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = "AIzaSyBt4F-EsA1jsLMWERsivgufl0Wn7nwuZ9o"

# Assign
service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

# Call the API's commentThreads.list method to list the existing comments.
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

if __name__ == "__main__":

	videoDict = {}

	with open(videolist) as f:
		videoIds = [line.strip() for line in f.readlines()]		

	for index, videoId in enumerate(videoIds):
		print(index)
		# Get first results
		data, nextPage = get_comment_threads({}, service, videoId, None)

		while nextPage != None:
			# print(len(data))
			data, nextPage = get_comment_threads(data, service, videoId, nextPage)

		tokensDict = {}
		repliesCount = 0
		for each in data:
			tokens = nltk.word_tokenize((data[each])["text"].lower())
			for word in tokens:
				if word not in tokensDict:
					tokensDict[word] = 1
				else:
					tokensDict[word] += 1
			repliesCount += (data[each])["replies"]

		videoDict[videoId] = {
			"text" : tokensDict,
			"replies" : repliesCount
		}

	with open('comments.json', 'w') as commentfile:
		json.dump(videoDict, commentfile, sort_keys = True, indent = 4, ensure_ascii=True)

