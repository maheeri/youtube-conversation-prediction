'''
Input json of vid_ids, ouputs data as json file
'''

from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from bs4 import BeautifulSoup
import httplib2
import os
import sys
import urllib	
import numpy as np
import urllib3
import json
import re
import nltk
from captions3 import get_formatted_transcript

# Retrieves the metadata of a video
def valid_constraints(youtube, video_id):
	video_info_list = youtube.videos().list(
		part="topicDetails, snippet, contentDetails, statistics",
		id = video_id
	).execute()

	video_info 		= video_info_list["items"][0]
	title 			= video_info["snippet"]["title"]
	duration_string = video_info["contentDetails"]["duration"]
	num_views 		= int(video_info["statistics"]["viewCount"])
	num_comments 	= int(video_info["statistics"]["commentCount"])
	publish_date 	= video_info["snippet"]["publishedAt"]
	topics 			= video_info["topicDetails"]["topicIds"] 
	captions 		= get_formatted_transcript(video_id);

	return title, duration_string, num_views, num_comments, publish_date, topics, captions

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
		comment_id 	= item["id"]
		comment 	= item["snippet"]["topLevelComment"]
		author 		= comment["snippet"]["authorDisplayName"]
		text 		= re.sub('\W+',' ', comment["snippet"]["textDisplay"][:-1])
		date 		= comment["snippet"]["updatedAt"]
		replies 	= item["snippet"]["totalReplyCount"]

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

	numReplies = avgReplies
	avgReplies = avgReplies / topCommentSize
	avgWords = len(wordList) / commentSize

	return avgReplies, avgWords, numReplies

def open_video_ids_json(filename):
	""" Takes a json name and returns a list of video_ids """
	with open(filename) as data_file:    
		data = json.load(data_file)
		video_set = set()
		for key in data:
			for vid_id in data[key]:
				video_set.add(vid_id)
		return list(video_set)


if __name__ == "__main__":
	input_json_filename = "video_ids_v2.json"

	# Authenticate
	YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
	YOUTUBE_API_SERVICE_NAME = "youtube"
	YOUTUBE_API_VERSION = "v3"
	DEVELOPER_KEY = "AIzaSyBt4F-EsA1jsLMWERsivgufl0Wn7nwuZ9o"

	# Assign
	YOUTUBE = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


	videoIds = open_video_ids_json(input_json_filename)

	videoDict = {}
	for index, videoId in enumerate(videoIds):
		avgReplies, avgWords, numReplies = get_all_comments(youtube, videoId)
		title, videoLength, numberViews, numberComments, publishDate, topics, captions = valid_constraints(youtube, videoId)

json_format = {
	"title" : title,
	"videoLength" : videoLength, 
	"numberViews" : numberViews,
	"numberComments" : numberComments,
	"numReplies" : numReplies,
	"avgRepliesPerComment" : avgReplies,
	"avgWordsPerComment": avgWords,
	"publishDate" : publishDate,
	"topics" : topics,
	"captions" : captions
}

		videoDict[videoId] = json_format


	with open('data.json', 'w') as commentfile:
		json.dump(videoDict, commentfile, sort_keys = True, indent = 4, ensure_ascii=True)



