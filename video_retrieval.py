"""Retrieve the video_ids corresponding to particular channels (referred
to as usernames also) and write them to a file"""

#!/usr/bin/python

import httplib2
import os
import sys
import datetime
import json

from apiclient.discovery import build
from apiclient.errors import HttpError

from comments import get_comments
from captions3 import get_formatted_transcript

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
def retrieve_user_videos(video_ids):
	results = []
	for video_id in video_ids:
		title = playlist_item["snippet"]["title"]
		video_id = playlist_item["snippet"]["resourceId"]["videoId"]
		

		video_info_list = youtube.videos().list(
			part="topicDetails, snippet, contentDetails, statistics",
			id = video_id
		).execute()
		#Todo: add title
		video_info 		= video_info_list["items"][0]
		title			= video_info["snippet"]["title"]
		topics 			= video_info["topicDetails"]["topicIds"] if "topicDetails" in video_info and "topicIds" in video_info["topicDetails"] else []
		publish_date 	= video_info["snippet"]["publishedAt"]
		duration_string = video_info["contentDetails"]["duration"]
		num_views 		= int(video_info["statistics"]["viewCount"])

		transcript = get_formatted_transcript(video_id)
		if transcript is not None:
			my_entry = 	{
							"id": 			video_id,
							"topic_ids": 	topics,
							"views" : 		num_views_string,
							"duration": 	duration_string,
							"publish_date": publish_date,
							"comments": 	get_comments(video_id),
							"transcript": 	transcript
							}
			results.append(my_entry)
		else:
			print("Could not get transcript")
	return results	


if __name__ == "__main__":
	print("Starting video collection")
	video_ids = ['ym4s2MeZ9E4']
	videos_data = retrieve_user_videos(video_ids)
	print("Done", "Now dumping...")
	filename = "videos_data"
	with open(filename+'.json', 'w+') as datafile:
		json.dump(videos_data, datafile, sort_keys = True, indent = 4, ensure_ascii=True)
	print("Done dumping file to json", "filename:", filename)