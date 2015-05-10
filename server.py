import os, sys
sys.path.append("./model") 
sys.path.append("./searching_and_ml/") 

from flask import Flask, render_template, jsonify, request, session

from query_and_rerank import *

import json

app = Flask(__name__)

CLASSIFIER = get_classifer()
tfv = get_tfv() 

@app.route('/')
def main():
    return render_template('youtube_new.html')

@app.route('/find_videos')
def ajax_find_videos():
  query = request.args.get('query')
  query_results = rerank_search_results(CLASSIFIER, query_search(query), tfv)

  scores = []
  thumbnails = []
  descriptions = []
  titles = []
  urls = []

  for video in query_results:
    video_details, score = video

    scores.append(round(score, 2))

    for key in video_details:
      urls.append(key)
      thumbnails.append('https://i.ytimg.com/vi/' + key + '/mqdefault.jpg')
      descriptions.append(video_details[key]['description'])
      titles.append(video_details[key]['title'])

  return jsonify(result=query, scores=scores, thumbnails=thumbnails, descriptions=descriptions, titles=titles, urls=urls)

@app.route('/get_info')
def ajax_find_details():
  video = request.args.get('video')
  words = get_wordcloud(video)
  print(video)


  return jsonify(words=words)


if __name__ == '__main__':
  app.debug = True
  app.secret_key = 'helloworld'
  app.run()