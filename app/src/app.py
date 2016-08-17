from flask import Flask
from flask import render_template
from autoab import *

app = Flask(__name__)

def format(experiments):
  return [x.replace('_',' ').title() for x in experiments.experiment_name.tolist()]

overview_data = zero_state_data(experiment_list.experiment_name[0])

@app.route("/")
def hello(ab_tests = format(experiment_list), overview = overview_data):
  return render_template('base.html', ab_tests = ab_tests, overview = overview)

if __name__ == "__main__":
  app.run()
