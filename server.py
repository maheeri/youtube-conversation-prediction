import os, sys
sys.path.append(os.path.abspath("./model")) 


from flask import Flask, render_template, jsonify, request
# from model import prepare, find_videos
import json

app = Flask(__name__)
# tfv, svr = prepare()


@app.route('/')
def main():
    return render_template('youtube_new.html')

@app.route('/find_videos')
def ajax_find_vides():
  query = request.args.get('query')

  # CALCULATE THINGS NOW

  return jsonify(result=query)

if __name__ == '__main__':
  app.debug = True
  app.run()