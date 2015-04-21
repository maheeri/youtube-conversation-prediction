"""Retrieves video_ids based on queries and stores them into separate files"""

#!/usr/bin/python

import httplib2
import os
import sys
import datetime
import json

from apiclient.discovery import build
from apiclient.errors import HttpError

from categories import create_category_id_dict

# Key and version data 
DEVELOPER_KEY = "AIzaSyBEuuLWPO0AJIIp7TVGIB1uM_mNiNkMVbw"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Authenticate 
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
	developerKey=DEVELOPER_KEY)

global_retrieved = 0
global_searched = 0

"""Check that the video given by video_id satisfies the following
constraints: (1) The length is 6 +- 2 minute,(2) Has more than
100,000 views, (3) Was pubslihed in 2013 or 2014"""
def valid_constraints(video_id):
	video_info_list = youtube.videos().list(
		part="snippet, statistics, contentDetails",
		id = video_id
	).execute()
	video_info = video_info_list["items"][0]
	num_views = video_info["statistics"]["viewCount"]
	publish_date = video_info["snippet"]["publishedAt"]
	duration_string = video_info["contentDetails"]["duration"]

	publish_date = datetime.datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%S.%fZ')
	
	# Check for a 5 +- 1 minute duration
	hour_index = duration_string.find("H")
	minute_index = duration_string.find("M")
	second_index = duration_string.find("S")
	duration = 0 # duration in seconds 
	if (hour_index != -1):
		return False 
	elif (minute_index == -1 and second_index != -1):
		duration = int(duration_string[2:second_index])
	elif (minute_index != -1 and second_index != -1):
		duration = int(duration_string[2:minute_index]) * 60 + int(duration_string[minute_index+1:second_index])
		
	valid_duration = (duration > 240) and (duration < 480)
	
	# Check for a valid number of views
	valid_num_views = (num_views > 100000)
	
	# Check that video has been online for > 5 days 
	# current_date = datetime.datetime.now()
	# date_diff = current_date - publish_date 
	# valid_publish_date = date_diff.days > 5
	valid_publish_date = (publish_date.year == 2013) or (publish_date.year == 2014)
	
	return (valid_duration and valid_num_views and valid_publish_date)
	

"""Retrieves num_required video_ids for the given category id. num_required is the number of 
videos that will be returned for this category if possible (if that many are available, 
otherwise write the max possible). Returns a list of video_ids for the cateogry id for videos
that have closed captions"""
def category_video_search(category_id, num_required):
	# Call the search.list method to retrieve results matching the specified
	# query term.
	search_request = youtube.search().list(
		part="id",
		maxResults=50,
		type="video",
		videoCaption="closedCaption",
		videoCategoryId=category_id
	)
	 
	search_response = search_request.execute()
	
	total_results = search_response["pageInfo"]["totalResults"] # To see if we can attain the number of searched videos
	
	num_videos_retrieved = 0 # Keep track of the number of videoIDs retrieved so far
	num_videos_searched = 0 # Keep track of the number of videoIDs searched so far
	
	
	video_id_list = []
	while (num_videos_retrieved < num_required and num_videos_searched < total_results):
		
		if search_request is None: # No more searches can be run
			return video_id_list
		else:
			search_response = search_request.execute()
		
		for search_result in search_response.get("items", []):
			num_videos_searched = num_videos_searched + 1
			if num_videos_searched >= total_results: # Looked through all results
				return video_id_list
			if valid_constraints(search_result["id"]["videoId"]):
				if (num_videos_retrieved < num_required):
					num_videos_retrieved = num_videos_retrieved + 1
					video_id_list.append(search_result["id"]["videoId"])
				else: # Have reached the required limit
					return video_id_list
		
		search_request = youtube.search().list_next(
			search_request, search_response) # Get the next page of results 
			
	return video_id_list
	
	
"""Returns a dictionary where the keys are the category ids and the values are the 
lists of associated video_ids for the US region. Each list has videos_per_category
number of video_ids"""
def populate_all_category_searches(videos_per_category):
	category_id_to_name_dict = create_category_id_dict() # maps category ids to names
	
	category_to_video_id_dict = {}
	
	for category_id in category_id_to_name_dict.keys():
		category_to_video_id_dict[category_id] = category_video_search(category_id, videos_per_category)

	return category_to_video_id_dict

	
if __name__ == "__main__":
	print(populate_all_category_searches(1))