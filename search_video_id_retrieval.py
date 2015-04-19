"""Retrieves video_ids based on queries and stores them into separate files"""

#!/usr/bin/python

import httplib2
import os
import sys
import datetime
import json

from apiclient.discovery import build
from apiclient.errors import HttpError

# Key and version data 
DEVELOPER_KEY = "AIzaSyBEuuLWPO0AJIIp7TVGIB1uM_mNiNkMVbw"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Authenticate 
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
	developerKey=DEVELOPER_KEY)
	
"""Check that the video given by video_id satisfies the following
constraints: (1) Has greater than 100,000 views and (2) Is more
than 5 days old"""
def valid_constraints(video_id):
	video_info_list = youtube.videos().list(
		part="snippet, statistics",
		id = video_id
	).execute()
	video_info = video_info_list["items"][0]
	num_views = video_info["statistics"]["viewCount"]
	publish_date = video_info["snippet"]["publishedAt"]

	publish_date = datetime.datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%S.%fZ')
	
	# Check for a valid number of views
	valid_num_views = num_views > 100000 
	
	# Check that video has been online for > 5 days 
	current_date = datetime.datetime.now()
	date_diff = current_date - publish_date 
	valid_publish_date = date_diff.days > 5
	
	return (valid_num_views and valid_publish_date)
	

"""Retrieves video IDs given a search query and places the results into a file with 
a name corresponding to the search query. Currently only returns videos and not
channels or playlists. Also only return search results with closed captioning and
and length less than 4 minutes. query is a string. num_search is the number of 
videos that will be searched for this query (if that many are available, otherwise
write the max possible from the search results"""
def query_video_search(query, num_search):
	# Call the search.list method to retrieve results matching the specified
	# query term.
	search_request = youtube.search().list(
		q=query,
		part="id",
		maxResults=50,
		type="video",
		videoCaption="closedCaption",
		videoDuration="short"
	)
	
	search_response = search_request.execute()
	
	os.chdir(r"C:\Users\Maheer\Dropbox\Cornell Course Materials\Spring 2015\CS 4300\youtube-caption-prediction\query_search_video_ids")
	f = open(query+".txt", "w")
	
	total_results = search_response["pageInfo"]["totalResults"] # To see if we can attain the number of searched videos
	
	num_videos_searched = 0 # Keep track of the number of videoIDs searched so far
	
	# Add each a result to a file with the name query.txt
	while (num_videos_searched < num_search and num_videos_searched < total_results):
		
		search_response = search_request.execute()
		
		for search_result in search_response.get("items", []):
			num_videos_searched = num_videos_searched + 1
			if valid_constraints(search_result["id"]["videoId"]):
				f.write(search_result["id"]["videoId"]+"\n")
		
		search_request = youtube.search().list_next(
			search_request, search_response) # Get the next page of results 
			
	
	f.close() # Close file after writing to it 

	
if __name__ == "__main__":
	query_video_search("cooking", 100)