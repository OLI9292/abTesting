from flask import Flask, jsonify, render_template, request
from autoab import *
import json

app = Flask(__name__)

# Using static data for speed of development
ab_tests = format(experiment_list)
overview_data = [[['number of sessions', 1, 1], ['number of uniques:', 1, 1], ['sessions resulting in inquiry', 9.0, 14.0], ['uniques that have inquired', 9.0, 14.0], ['sum of inquiries / # of sessions', 0.011608623548922056, 0.032627865961199293], ['sum of inquiries / # of uniques', 0.01222707423580786, 0.034322820037105753], ['total artwork pageviews / uniques', 1.6253275109170306, 1.8541484716157206], ['avg inquiry rate per unique', 0.010480349344978166, 0.029684601113172542]], [[u'count_pv', 9150.0, 8997.0], [u'count_artwork_pv', 1861.0, 2123.0], [u'count_artist_pv', 1687.0, 1563.0], [u'count_article_pv', 492.0, 366.0], [u'inquiries', 14.0, 37.0], [u'three_way_handshakes', 2.0, 5.0], [u'three_way_handshakes_within_seven_days', 2.0, 5.0], [u'purchases', 0.0, 0.0], [u'total_purchase_price', 0.0, 0.0], [u'accounts_created', 37.0, 41.0]], [['positive LVID outcomes / uniques', 0.0078602620087336247, 0.012987012987012988], ['positive sessions / total sessions', 0.007462686567164179, 0.012345679012345678]]]
overview_data2 = [[['number of sessions', 68.0, 52.0], ['number of uniques:', 68.0, 52.0], ['sessions resulting in inquiry', 0.0, 0.0], ['uniques that have inquired', 0.0, 0.0], ['sum of inquiries / # of sessions', 0.0, 0.0], ['sum of inquiries / # of uniques', 0.0, 0.0], ['total artwork pageviews / uniques', 0.94117647058823528, 0.73529411764705888], ['avg inquiry rate per unique', 0.0, 0.0]], [[u'count_pv', 337.0, 279.0], [u'count_artwork_pv', 64.0, 50.0], [u'count_artist_pv', 53.0, 18.0], [u'count_article_pv', 10.0, 6.0], [u'inquiries', 0.0, 0.0], [u'three_way_handshakes', 0.0, 0.0], [u'three_way_handshakes_within_seven_days', 0.0, 0.0], [u'purchases', 0.0, 0.0], [u'total_purchase_price', 0.0, 0.0], [u'accounts_created', 3.0, 1.0]], [['positive LVID outcomes / uniques', 0.0, 0.0], ['positive sessions / total sessions', 0.0, 0.0]]]

@app.route("/test_dates")
def test_dates():
  result = get_start_end(request.args.to_dict().keys()[0])
  print result
  return jsonify(success = True, data = result)

@app.route("/test_data")
def test_data():
  settings = request.args.to_dict().keys()[0].split(',')
  print settings
  result = run_notebook(settings[0], settings[1], settings[2])
  print result
  return render_template('overview.html', overview = result)

@app.route("/")
def index(overview = overview_data):
  return render_template('base.html', ab_tests = ab_tests, overview = overview)

if __name__ == "__main__":
  app.run()
