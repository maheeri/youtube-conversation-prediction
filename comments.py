#!/usr/bin/python

# Usage example:
# python comment_threads.py --channelid='<channel_id>' --videoid='<video_id>' --text='<text>'

import httplib2
import os
import sys
import re

from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import json
import urllib


# Authenticate
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = "AIzaSyBt4F-EsA1jsLMWERsivgufl0Wn7nwuZ9o"

# Assign
service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
video_id = 'RtWw3OtdBkw'

# Call the API's commentThreads.list method to list the existing comments.
def get_comment_threads(data, youtube, video_id, nextPageToken):

	length = len(data)

	results = youtube.commentThreads().list(
		part="snippet",
		videoId=video_id,
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

# Get first results
data, nextPage = get_comment_threads({}, service, video_id, None)

while nextPage != None:
	# print(len(data))
	data, nextPage = get_comment_threads(data, service, video_id, nextPage)

with open('comments.txt', 'w') as commentfile:
	json.dump(data, commentfile, sort_keys = True, indent = 4, ensure_ascii=True)

