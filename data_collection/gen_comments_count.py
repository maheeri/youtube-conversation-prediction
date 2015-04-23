"""Retrieve the comment counts for a file with video_ids and 
save into a separate file"""

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

"""Gets the comment count for the video with the given video_id"""
def get_comment_count(video_id):
	video_info_list = youtube.videos().list(
		part="snippet, contentDetails, statistics",
		id = video_id
	).execute()
	
	video_info = video_info_list["items"][0]
	
	num_comments = video_info["statistics"]["commentCount"]
	
	return num_comments


"""Retrieves the comment counts for the video_ids given in the file
represented by filename. The filename has the form [username].txt. 
The file has each video ID in a separate line. Writes the comment 
counts to a new file with the name[username]_commentcount.txt in 
same order as it reads the video_ids in the file"""
def get_all_comm_counts(filename):
	username = filename[:-4] # get rid of the .txt
	
	
	# Change directory to be able to read and write to files
	os.chdir('C:\\Users\\Maheer\\Dropbox\\Cornell Course Materials\\Spring 2015\\CS 4300\\youtube-caption-prediction\\video_id_data')
	
	with open(filename) as f:
		video_id_list = f.readlines()
	video_id_list = [video_id.rstrip('\n') for video_id in video_id_list] 
	
	counts_file = open(username+"_commentcount"+".txt", "w+")
	for video_id in video_id_list:
		counts_file.write(get_comment_count(video_id)+"\n")
		
	
if __name__ == "__main__":
	get_all_comm_counts("VSauce.txt")