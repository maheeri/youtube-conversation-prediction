'''
Input json of vid_ids, ouputs data as json file
'''

from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
import httplib2
import os
import sys
import urllib	
import urllib3
import json
from captions3 import get_formatted_transcript


# Authenticate
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = "AIzaSyBt4F-EsA1jsLMWERsivgufl0Wn7nwuZ9o"

# Assign
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)



def get_comment_threads(vid_id, data=None, next_page_tok=None):
	""" Get the thread of comments from a videoID """

	def comments_list(parent_id):
		"""Get the comments from a particular thread"""
		api_results = youtube.comments().list(
			part 		= "snippet",
			parentId 	= parent_id,
			textFormat 	= "plainText",
		).execute()
		comments = api_results["items"]:
		return comments

	def format_comment(comment):
		""" Format comments """
		return {
			'author': comment["snippet"]["authorDisplayName"],
			'date'	: comment["snippet"]["updatedAt"],
			'text'	: comment["snippet"]["textDisplay"]
		}
	##############################################
	# Check base case
	if next_page_tok == '' or next_page_tok is None:
		return data
	# If this is the first call, start data
	if data is None:
		data = {}
	# Get the thread via API call
	api_results = youtube.commentThreads().list(
		part 		= "snippet",
		videoId 	= vid_id,
		textFormat	= "plainText",
		maxResults	= 100,
		pageToken 	= next_page_tok
	).execute()

	# Process the thread and get the associated comments
	for item in api_results["items"]:
		comment_id 	= item["id"]
		top_comment = format_comment(item["snippet"]["topLevelComment"])
		num_replies = item["snippet"]["totalReplyCount"]
		# Only if this has 2 or more replies do I add it
		if num_replies >= 2:
			data[comment_id] = {
				"top_comment"	: top_comment,
				"num_replies"	: num_replies,
				"comments"		: [format_comment(comment) for comment in comments_list(comment_id)]
			}

	# Recur
	return get_comment_threads(vid_id, data, api_results["nextPageToken"])


def get_video_data(vid_id, categories_list):
	""" Gets all the relevant data for a video """
	video_info_list = youtube.videos().list(
		part="topicDetails, snippet, contentDetails, statistics",
		id = vid_id
	).execute()

	video_info 	= video_info_list["items"][0]
	title 			= video_info["snippet"]["title"]
	duration_string = video_info["contentDetails"]["duration"]
	video_defintion = video_info["contentDetails"]["definition"]
	num_views 		= int(video_info["statistics"]["viewCount"])
	publish_date 	= video_info["snippet"]["publishedAt"]
	topics 			= video_info["topicDetails"]["topicIds"] if 'topicDetails' in video_info and 'topicIds' in video_info["topicDetails"] else [] #code around bug
	captions 		= get_formatted_transcript(vid_id);

	if captions == None: #Optimization by doing this check also throws away videos with bad captions
		return None
	comment_thread = get_comment_threads(vid_id)
	return {
		"title" 				: title,
		"video_length" 			: duration_string,
		"vide_defintion"		: video_defintion,
		"number_views" 			: num_views,
		"publish_date" 			: publish_date,
		"topics" 				: topics,
		'categories'			: categories_list,
		"captions" 				: captions,
		'comment_thread'		: comment_thread
	}

def process_inv_idx(inv_idx):
	all_data = {}
	for vid_id, categories_list in inv_idx.iteritems():
		print "proccessing: ", vid_id
		all_data[vid_id] = get_video_data(vid_id, categories_list)
	return all_data

if __name__ == "__main__":
	os.chdir(os.path.join(os.pardir, 'data')) #go into data folder
	input_json_filename = 'video_ids_v5_pruned_pruned.json'
	videoIds_inv_idx = json.load(open(input_json_filename))
	videos_data = process_inv_idx(videoIds_inv_idx)
	with open('video_ids_v5_pruned_pruned_data.json', 'w') as datafile:
		json.dump(videos_data, datafile, indent = 4, ensure_ascii=True)