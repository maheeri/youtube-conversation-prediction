"""Retrieve the video_ids corresponding to particular channels (referred
to as usernames also) and write them to a file"""

#!/usr/bin/python

import httplib2
import os
import sys
import datetime
import json
import time

from apiclient.discovery import build
from apiclient.errors import HttpError

from captions3 import get_formatted_transcript
# from video_data import get_comments_metadata

# Key and version data 
DEVELOPER_KEY = "AIzaSyBEuuLWPO0AJIIp7TVGIB1uM_mNiNkMVbw"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Authenticate 
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
	developerKey=DEVELOPER_KEY)

# Retrieve the contentDetails part of the channel resource for the
# given username - loop
def retrieve_user_videos(vid_ids):
	results = []
	for vid_id in vid_ids:
		print "Getting: ", vid_id
		video_info_list = youtube.videos().list(
			part="topicDetails, snippet, contentDetails, statistics",
			id = vid_id
		).execute()
		video_info 		= video_info_list["items"][0]
		title			= video_info["snippet"]["title"]
		topics 			= video_info["topicDetails"]["topicIds"] if "topicDetails" in video_info and "topicIds" in video_info["topicDetails"] else []
		publish_date 	= video_info["snippet"]["publishedAt"]
		duration_string = video_info["contentDetails"]["duration"]
		num_views 		= int(video_info["statistics"]["viewCount"])
		num_comments 	= int(video_info["statistics"]["commentCount"])


		# "comments_metadata": 	get_comments_metadata(youtube, vid_id),
		my_entry = 	{
						"title":				title,
						"id": 					vid_id,
						"topic_ids": 			topics,
						"views" : 				num_views,
						"num_comments": 		num_comments,
						"duration": 			duration_string,
						"publish_date": 		publish_date,
						"transcript": 			get_formatted_transcript(vid_id)
					}
		results.append(my_entry)
	return results	

def open_vid_ids_json(filename):
	""" Takes a json name and returns a list of vid_ids """
	with open(filename) as data_file:    
		data = json.load(data_file)
		video_set = set()
		for key in data:
			for vid_id in data[key]:
				video_set.add(vid_id)
		return list(video_set)

def json_dump(content, filename):
	with open(filename+'.json', 'w') as outfile:
	    json.dump(content, outfile, indent = 4, ensure_ascii=True)

if __name__ == "__main__":
	print(time.ctime())
	input_json_filename = "vid_ids_v2.json"
	# vid_ids = open_vid_ids_json(input_json_filename)
	vid_ids = ['diU70KshcjA','fupWquPNoTc','B3YbODo7ieQ','pvJqvA0QU1g','BzpIB5TJ7LI']
	my_data = retrieve_user_videos(vid_ids)
	print(time.ctime())
	json_dump(my_data, 'test_data_nwp')

	"""
	print("Starting video collection")
	videos_data = retrieve_user_videos(vid_ids)
	print("Done", "Now dumping...")
	filename = "videos_data"
	with open(filename+'.json', 'w+') as datafile:
		json.dump(videos_data, datafile, sort_keys = True, indent = 4, ensure_ascii=True)
	print("Done dumping file to json", "filename:", filename)
	"""