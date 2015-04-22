from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('youtube_captions.html')

@app.route('/find_restaurants', methods=['POST'])
def ajax_find_restaurants():
  if request.method == 'POST':
    location = request.args.form['input_location']
    dist = request.args.form['dist']

    input_data, results = find_nearest(location, float(dist))

    formatted_results = format_results(input_data, results)
    with open('queries.txt', 'a') as output:
      output.write(formatted_results + '\n')

    return jsonify({ 'input_data': input_data, 'results': results })
  else:
    return 'Error'

@app.route('/results', methods=['GET'])
def ajax_get_results():
  with open('queries.txt', 'r') as results:
    return results.read()

if __name__ == '__main__':
  app.debug = True
  app.run()