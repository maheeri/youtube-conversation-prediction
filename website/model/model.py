from __future__ import print_function
from __future__ import division
from apiclient.discovery import build
from apiclient.errors import HttpError
import json, time, os, sys, httplib2
import numpy as np
import json
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.dummy import DummyClassifier
from sklearn.svm import SVR

sys.path.append(os.path.abspath("../..")) 
from captions3 import has_english


# Key and version data 
DEVELOPER_KEY = "AIzaSyBEuuLWPO0AJIIp7TVGIB1uM_mNiNkMVbw"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Authenticate 
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

# Copy of function
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
	num_comments = video_info["statistics"]["commentCount"]
	publish_date = video_info["snippet"]["publishedAt"]
	duration_string = video_info["contentDetails"]["duration"]
	
	# Check for a 6 +- 2 minute duration
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
	valid_num_views = (int(num_views) > 100000)
	
	# Check that video has been online for > 5 days 
	# current_date = datetime.datetime.now()
	# date_diff = current_date - publish_date 
	# valid_publish_date = date_diff.days > 5
	
	valid_captions = has_english(video_id)

	valid_num_comments = int(num_comments) > 0

	return (valid_captions and valid_duration and valid_num_views and valid_num_comments)
	
"""Retrieves num_required video_ids for the given category id. num_required is the number of 
videos that will be returned for this category if possible (if that many are available, 
otherwise write the max possible). Returns a list of video_ids for the cateogry id for videos
that have closed captions"""
def video_search(query, num_required):
	# Call the search.list method to retrieve results matching the specified
	# query term.
	search_request = youtube.search().list(
		part="id",
		maxResults=50,
		type="video",
		videoCaption="closedCaption",
		videoType="any",
		videoEmbeddable="true",
		videoDuration="medium",
		safeSearch="strict",
		relevanceLanguage="en",
		q=query,
		publishedAfter="2013-01-01T00:00:00Z",
		publishedBefore="2014-12-31T23:59:59Z"
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

def process_videos(video_list):

	video_num_comments, video_captions = np.array([(video_list["num_comments"], video_list["transcript"]) 
											  for video_datum in video_list ]).T
	combined_video_captions = []
	video_num_comments_cut  = []

	for caption_data_list,num_comments in zip(video_captions,video_num_comments):
		text = ""
		if caption_data_list is not None and caption_data_list is not "":
			video_num_comments_cut.append(num_comments)
			for caption_data in caption_data_list:
				if caption_data is not None and "text" in caption_data:
					text += (caption_data["text"]+" ")
			combined_video_captions.append(text[:-1])  

	data = zip(video_num_comments_cut, combined_video_captions)

	tfv = TfidfVectorizer(ngram_range=(1,2), lowercase=True, strip_accents="unicode", 
					  stop_words='english', use_idf=False, norm='l1', min_df=1)
	tfv.fit(video_captions_train)

	data_formatted = tfv.transform(data)

	return data_formatted


# Load Data:
def prepare():	
	with open('data_wo_replies.json') as json_file:   
		video_data = json.load(json_file)

	video_num_comments, video_captions = np.array([ (video_datum["num_comments"], video_datum["transcript"]) 
											  for video_datum in video_data ]).T

	combined_video_captions = []
	video_num_comments_cut  = []

	for caption_data_list,num_comments in zip(video_captions,video_num_comments):
		text = ""
		if caption_data_list is not None and caption_data_list is not "":
			video_num_comments_cut.append(num_comments)
			for caption_data in caption_data_list:
				if caption_data is not None and "text" in caption_data:
					text += (caption_data["text"]+" ")
			combined_video_captions.append(text[:-1])  

	video_captions = combined_video_captions

	num_comments_train, num_comments_test, video_captions_train, video_captions_test  = train_test_split(video_num_comments_cut, combined_video_captions, 
																	   test_size=.5, random_state=0)
	tfv = TfidfVectorizer(ngram_range=(1,2), lowercase=True, strip_accents="unicode", 
						  stop_words='english', use_idf=False, norm='l1', min_df=1)
	tfv.fit(video_captions_train)
	X_train = tfv.transform(video_captions_train)
	X_test  = tfv.transform(video_captions_test)
	svm_regression_classifier = SVR(kernel="linear")
	svm_regression_classifier.fit(X_test, num_comments_test)
	return tfv, svm_regression_classifier

def return_ranked_videos(query):
	returned_videos = video_search(query, 20)
	classifier_data = process_videos(returned_videos)
	classifier = prepare()
	scores = classifer.predict(classifer_data)

	ranking = zip(scores, returned_videos)
	ranking = sorted(ranking, key=lambda x: x[0], reverse=True)

	return ranking


def find_videos(query):
    returned_videos = video_search(query, 20)
    results = []
    for vid_id in returned_videos:
        flat_trans = get_flattened_transcript(vid_id)
        #tfidf fit
        capt_vector = tfv.transform(flat_trans)
        num_comments_pred_svr = svm_regression_classifier.predict(capt_vector)
        results.appened((num_comments_pred_svr, vid_id, title, orig))


return_ranked_videos("cats")