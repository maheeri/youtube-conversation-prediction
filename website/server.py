from flask import Flask, render_template, jsonify, request
from model import find_videos, prepare

app = Flask(__name__)
tfv, svr = prepare()

@app.route('/')
def main():
    return render_template('youtube_captions.html')

@app.route('/find_videos', methods=['POST'])
def ajax_find_restaurants():
  if request.method == 'POST':
    query = request.form['query']
    print query;
    results = find_videos(query, tfv, svr)

    return jsonify({ 'results': results })
  else:
    return 'Error'

if __name__ == '__main__':
  app.debug = True
  app.run()