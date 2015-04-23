"""Creates a dictionary of category IDs as keys with the category names
as values"""

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

	
"""Returns a dictionary with the category IDs mapped to their category names for the 
US region"""
def create_category_id_dict():
	category_response = youtube.videoCategories().list(
		part="snippet",
		regionCode = "US"
	).execute()
	
	category_id_dict = {}
	for category_item in category_response["items"]:
		id = int(category_item["id"])
		category_name = category_item["snippet"]["title"]
		category_id_dict[id] = category_name
		
	return category_id_dict
	
if __name__ == "__main__":
	print(create_category_id_dict())