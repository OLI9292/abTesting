from flask import Flask
from flask import render_template
from autoab import *
app = Flask(__name__)

def format(experiments):
  return [x.replace('_',' ').title() for x in experiments.experiment_name.tolist()]

@app.route("/")
def hello(ab_tests = format(experiment_list)):
  return render_template('base.html', ab_tests = ab_tests)

if __name__ == "__main__":
  app.run()
