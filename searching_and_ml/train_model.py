from __future__ import print_function
from __future__ import division
import numpy as np
import json

import httplib2
import os
import sys
import datetime
import json

from apiclient.discovery import build
from apiclient.errors import HttpError

from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer

from sklearn.cross_validation import train_test_split

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.dummy import DummyRegressor

from sklearn.metrics import mean_absolute_error

from sklearn.externals import joblib

"""Generates the captions and comments list for each video"""
def generate_captions_and_comments():
	os.chdir(r'C:\Users\Maheer\Dropbox\Cornell Course Materials\Spring 2015\CS 4300\youtube-caption-prediction\data')
	
	with open('big_data_approx.json') as json_file:   
		video_data = json.load(json_file)
		
	video_num_comments, video_captions = np.array([ (video_datum["score"], video_datum["captions"]) 
                                              for _,video_datum in video_data.iteritems() ]).T
												
	# Define a stemmer and lemmatizer for use with our captions
	stemmer = PorterStemmer()
	lemmatizer = WordNetLemmatizer()


	combined_video_captions = []
	video_num_comments_cut  = []
	for caption_data_list,num_comments in zip(video_captions,video_num_comments):
		text = ""
		if caption_data_list is not None:
			video_num_comments_cut.append(num_comments)
			for caption_data in caption_data_list:
				if caption_data is not None and "text" in caption_data:
					for word in caption_data["text"].split():
						#text += (stemmer.stem(word)+" ")
						text += (lemmatizer.lemmatize(word)+" ")
			combined_video_captions.append(text[:-1])
		
	video_captions = combined_video_captions
	
	return (video_num_comments_cut, video_captions)


"""Create a test-train split and return the data as a 4-tuple"""
def test_train_split():
	comments_and_captions = generate_captions_and_comments()
	Y_train, Y_test, video_captions_train, video_captions_test  = train_test_split(comments_and_captions[0], comments_and_captions[1], test_size=.25, random_state=0)
	return (Y_train, Y_test, video_captions_train, video_captions_test)
	

"""Create a vocab based on the training set above"""
def vectorize_on_training_set():
	train_test_split = test_train_split()
	tfv = TfidfVectorizer(ngram_range=(1,2), lowercase=True, strip_accents="unicode", 
                      stop_words='english', use_idf=False, norm='l1', min_df=1)
	tfv.fit(train_test_split[2])
	return tfv

	
"""Trains a classifier on the vectorized vocab from vectorize_on_training_set"""
def train_classifier():
	X_train = tfv.transform(video_captions_train)
	X_test  = tfv.transform(video_captions_test)
	
	dummy = DummyRegressor(strategy="median")
	dummy.fit(X_train, Y_train)
	Y_pred_med = dummy.predict(X_test)

	
if __name__ == "__main__":
	os.chdir(r'C:\Users\Maheer\Dropbox\Cornell Course Materials\Spring 2015\CS 4300\youtube-caption-prediction\trained_models')
	train_test_split = train_test_split()
	tfv = vectorize_on_training_set()
	X_train = tfv.transform(train_test_split[2])
	X_test  = tfv.transform(train_test_split[3])
	
	dummy = DummyRegressor(strategy="median")
	dummy.fit(X_train, train_test_split[0])
	#Y_pred_med = dummy.predict(X_test)
	#joblib.dump(dummy, 'dummy.pkl')