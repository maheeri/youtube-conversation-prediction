#!/usr/bin/python

import os
import json
from collections import defaultdict

def json_dump(content, filename):
	""" Dumps content to json file """
	with open(filename+'.json', 'w') as outfile:
		json.dump(content, outfile, indent = 4, ensure_ascii=True)

def inverted_index(vid_ids_json_cat_dict):
	inv_idx = defaultdict(list)
	for cat_id, vid_ids in vid_ids_json_cat_dict.iteritems():
		for vid_id in vid_ids:
			inv_idx[vid_id].append(cat_id)
	return inv_idx

def prune(inv_idx, failed_list):
	""" Deletes vid_ids from inv_idx if they are in the failed list """
	start_size = len(inv_idx)
	for failed_vid_id in failed_list:
		if failed_vid_id in inv_idx:
			del inv_idx[failed_vid_id]
	print "I pruned this many vid ids: ", (start_size - len(inv_idx))
	return inv_idx

if __name__ == "__main__":
	#### The code prunces incoming lists ####
	os.chdir(os.path.join(os.pardir, 'data')) #go into data folder
	inv_idx = json.load(open('video_ids_v5_pruned.json'))
	failed_list = json.load(open('failedList.json'))
	inv_idx_pruned = prune(inv_idx, failed_list)
	json_dump(inv_idx_pruned, 'video_ids_v5_pruned_pruned')
	########

	#### The code below converts an old cat vid dict to an inverted index style dict ####
	# os.chdir(os.path.join(os.pardir, 'data')) #go into data folder
	# cat_vid_dict = json.load(open('video_ids_v4.json'))
	# inv_idx = inverted_index(cat_vid_dict)
	# print len(inv_idx)
	# json_dump(inv_idx, 'video_ids_v5')	
	########
	pass