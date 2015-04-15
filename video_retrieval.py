#!/usr/bin/python

import httplib2
import os
import sys
import datetime

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
constraints: (1) The length is 5 +- 3 minutes, (2) Captions
are enabled,(3) Has greater than 100,000 views and (4) Is more
than 5 days old"""
def valid_constraints(video_id):
 	video_info_list = youtube.videos().list(
		part="snippet, contentDetails, statistics",
		id = video_id
	).execute()
	
	video_info = video_info_list["items"][0]
	
	duration_string = video_info["contentDetails"]["duration"]
	captions_enabled = video_info["contentDetails"]["caption"]
	num_views_string = video_info["statistics"]["viewCount"]
	publish_date = video_info["snippet"]["publishedAt"]
	publish_date = datetime.datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%S.%fZ')
	
	# Check for a 5 +- 2 minute duration
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
	
	valid_duration = (duration > 120) and (duration < 480)
	
	# Check for a valid number of views
	valid_num_views = int(num_views_string) > 100000 
	
	# Check if captions are enabled
	captions_enabled = captions_enabled == "true" 
	
	# Check that video has been online for > 5 days 
	current_date = datetime.datetime.now()
	date_diff = current_date - publish_date 
	valid_publish_date = date_diff.days > 5
	
	return valid_duration and valid_num_views and captions_enabled and valid_publish_date

# Change directory to be able to write to file 
os.chdir('C:\\Users\\Maheer\\Dropbox\\Cornell Course Materials\\Spring 2015\\CS 4300\\youtube-caption-prediction\\video_id_data')

# List of usernames to retrive videos from 
username_list = ["VICE"]

# Retrieve the contentDetails part of the channel resource for the
# given username - loop 
for username in username_list:
	channels_response = youtube.channels().list(
	forUsername=username,
	part="contentDetails"
	).execute()
	
	# Open a file with the name "username" for writing video IDs
	f = open(username+".txt", "w+")
	
	processed_count = 0 # Number of videos processed 
	
	for channel in channels_response["items"]:
		# From the API response, extract the playlist ID that identifies the list
		# of videos uploaded to the authenticated user's channel.
		uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

		print "Videos in list %s" % uploads_list_id

		# Retrieve the list of videos uploaded to the authenticated user's channel.
		playlistitems_list_request = youtube.playlistItems().list(
			playlistId=uploads_list_id,
			part="snippet",
			maxResults=50
		)
	
		while playlistitems_list_request:
			playlistitems_list_response = playlistitems_list_request.execute()

			# Print information about each video.
			for playlist_item in playlistitems_list_response["items"]:
				processed_count = processed_count + 1
				print(processed_count) # To track progress
				title = playlist_item["snippet"]["title"]
				video_id = playlist_item["snippet"]["resourceId"]["videoId"]
				if (valid_constraints(video_id)):
					print("Valid video found: " + title)
					f.write(video_id + "\n")

			playlistitems_list_request = youtube.playlistItems().list_next(
				playlistitems_list_request, playlistitems_list_response)
	
	# Close file after all the video IDs for a username have been found 
	f.close()
	# Reset the count of procssed videos
	processed_count = 0
	
print("Done")