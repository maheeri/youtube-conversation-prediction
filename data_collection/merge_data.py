from __future__ import division
import json
import datetime
import os
import sys
from dateutil.parser import parse
from util import *
from scrape_format import *
from nltk import word_tokenize
from captions3 import get_formatted_transcript

def merge_data(target_views, threshold=".25", comment_path="comments/", scraped_path="scraped/"):
    """ Script to merge all data
    Require there to be a .scrape and a .json of all vid_ids in the comments folder
    =Inputs=
    target_views: string list
        The ammount of views to trim the videos down to 
    =Outputs=
    merged data
    """
    big_data = {}
    
    future_date = parse("3030-01-01")
    vid_ids = get_filenames(comment_path)
    for vid_id in vid_ids:
        print "processing: ", vid_id
        vid_data = json.load(open(comment_path+vid_id+'.json')) #load comment data

        scrape_results = get_date(100000,scraped_path, vid_id)  #load scrape data
        cut_date = future_date if scrape_results[0] is None else scrape_results[2] #cut into future if None
        vid_views = scrape_results[1]

        vid_score = 0
        threads = vid_data.pop("comment_thread")
        bad_threads = []
        for thread_id, thread in threads.iteritems():
            score = 0
            top_com_date = parse(thread["top_comment"]["date"])
            top_com_date = top_com_date.replace(tzinfo=None) #make unaware
            if top_com_date <= cut_date: #check date
                #then this is a good record...maybe. Check the count
                score += 1
                author_set = set()
                author_set.add(thread["top_comment"]["author"])
                for comment in thread["comments"]:
                    com_date = parse(comment["date"])
                    com_date = com_date.replace(tzinfo=None)        #make unaware
                    if com_date <= cut_date:                        #check date
                        if len(word_tokenize(comment["text"])) > 1: #check number of words
                            author_set.add(comment["author"])       #add author
                            score += 1                              #add to score
                score = score if len(author_set)>1 else 0           #set the score to zero if all comments made by just the author
                vid_score += score                                  #add score to video's score
            #add bad threads
            if score < 2:
                bad_threads.append(thread_id)
        #remove bad threads (after iteration)
        for bad_thread in bad_threads:
            del threads[bad_thread]
        #normalize the video score
        vid_score_normalized = (vid_score/float(vid_views))*target_views #normalize the score

        vid_data["comment_threads"] = threads
        vid_data["score"]           = vid_score_normalized
        vid_data["raw_score"]       = vid_score
        # vid_data["captions"]        = get_formatted_transcript(vid_id) #Re-get to correct my earlier error
        big_data[vid_id] = vid_data #write all back to big_data
    return big_data
    
if __name__ == "__main__":
    os.chdir(os.path.join(os.pardir, 'data')) #go into data folder
    big_data = merge_data(200000)
    with open('big_data_v5_200k.json', 'w') as datafile:
        json.dump(big_data, datafile, indent = 4, ensure_ascii=True)