from flask import Flask, jsonify, render_template, request
from autoab import *
import json

app = Flask(__name__)

ab_tests = format(experiment_list)
blank_data = [[['number of sessions', 0, 0], ['number of uniques:', 0, 0], ['sessions resulting in inquiry', 0, 0], ['uniques that have inquired', 0, 0], ['sum of inquiries / # of sessions', 0, 0], ['sum of inquiries / # of uniques', 0, 0], ['total artwork pageviews / uniques', 0, 0], ['avg inquiry rate per unique', 0, 0]], [[u'count_pv', 0, 0], [u'count_artwork_pv', 0, 0], [u'count_artist_pv', 0, 0], [u'count_article_pv', 0, 0], [u'inquiries', 0, 0], [u'three_way_handshakes', 0, 0], [u'three_way_handshakes_within_seven_days', 0, 0], [u'purchases', 0.0, 0.0], [u'total_purchase_price', 0.0, 0.0], [u'accounts_created', 0, 0]], [['positive LVID outcomes / uniques', 0, 0], ['positive sessions / total sessions', 0, 0]]]

@app.route("/test_dates")
def test_dates():
  result = get_start_end(request.args.to_dict().keys()[0])
  return jsonify(success = True, data = result)

@app.route("/test_data")
def test_data():
  global d3Data
  settings = request.args.to_dict().keys()[0].split(',')
  result = run_notebook(settings[0], settings[1], settings[2])
  overview_data = result[0:3]
  d3Data = result[3]
  return render_template('overview.html', overview = overview_data)

@app.route("/d3_data")
def d3_data():
  return jsonify(success = True, data = d3Data)

@app.route("/")
def index(overview = blank_data):
  return render_template('base.html', ab_tests = ab_tests, overview = overview)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port)