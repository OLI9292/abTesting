import os 
import warnings
import numpy as np
import pandas as pd
import pymc as pm
from datetime import date, timedelta, datetime

from sqlalchemy import create_engine
engine_string = os.environ['REDSHIFT_CONN']
engine = create_engine(engine_string)

def to_array(df):
    arr = []
    for i in df.index.values:
        row = [i ,df.control[i], df.test[i]]
        arr.append(row)
    return arr

def sql(query):
    return pd.read_sql("%s" %query, engine)

# list of experiments in database
experiment_list = (sql("""
    SELECT DISTINCT experiment_name
    FROM force_production.experiment_viewed
    WHERE experiment_name != 'partner_application_copy'
    AND experiment_name   != 'masonry_artwork_sort'
    AND experiment_name   != 'artwork_item_contact_gallery'
"""))

# Variations; this is necessary because of of the inconsistencies in the experiments table for variation_name for the default group
defaults = ['default', 'original', 'old_homepage_1', 'old_homepage_2', 
            'old_homepage_3', 'old_homepage_4', 'old_homepage_5']

def query_experiment_data(exp_name, start_date=None, end_date=None):

    # pulls the first and last experiment logged
    start_end = sql("""
        SELECT MIN(sent_at),
               MAX(sent_at)
        FROM force_production.experiment_viewed
        WHERE experiment_name = '%s'
    """%exp_name)

    print start_date, end_date

    # selects the value from the data frame
    first_log_of_exp = start_end.iloc[0]['min']
    last_log_of_exp = start_end.iloc[0]['max']

    end_date = end_date if end_date else last_log_of_exp - timedelta(days=2)
    start_date = start_date if start_date else end_date - timedelta(hours=1)

    # queries the experiment table
    exp = sql("""
        SELECT exp.variation_id,
               fins.*,
               SPLIT_PART(fins.session_id,' - ',1) as session_number
        FROM (SELECT DISTINCT session_id,
                     variation_id,
                     experiment_id
              FROM analytics.force_mapped_experiment_viewed afmev
              WHERE afmev.experiment_id = '%s') exp
          LEFT JOIN analytics.force_inquiry_funnel_sessions fins
                 ON exp.session_id = fins.session_id
                AND exp.variation_id is not null
        WHERE (session_start_at >= '%s' AND session_start_at <= '%s') LIMIT 5000000
    """%(exp_name, start_date, end_date))

    exp['date'] = exp.session_start_at.values.astype('datetime64[D]')
    exp['session_number'] = exp.session_number.values.astype(int)
    exp['outcome'] = (exp.inquiries > 0).astype('int')
    exp = exp.set_index('session_start_at').sort_index()
    
    return exp

def control_test_split(exp):
    control = exp.loc[exp.variation_id.isin(defaults)]
    test = exp.loc[~exp.variation_id.isin(defaults)]

    return control, test

def generate_metrics(control,test):
    control_lvid_positive = len(control.loc[control.inquiries>0].groupby('looker_visitor_id').inquiries.count())
    test_lvid_positive    = len(test.loc[test.inquiries>0].groupby('looker_visitor_id').inquiries.count())

    metrics = { 'number of uniques:': [control.looker_visitor_id.nunique(), test.looker_visitor_id.nunique()],
                'number of sessions': [len(control), len(test)],
                'uniques that have inquired': [control_lvid_positive, test_lvid_positive],
                'sessions resulting in inquiry': [control.outcome.sum(), test.outcome.sum()],
                'total artwork pageviews / uniques': [control.count_artwork_pv.sum()*1./control.looker_visitor_id.nunique(),test.count_artwork_pv.sum()*1./control.looker_visitor_id.nunique()],
                'sum of inquiries / # of sessions': [1.*control.inquiries.sum()/control.session_id.nunique(), 1.*test.inquiries.sum()/test.session_id.nunique()],
                'sum of inquiries / # of uniques': [1.*control.inquiries.sum() / control.looker_visitor_id.nunique(), 1.*test.inquiries.sum() / test.looker_visitor_id.nunique()],
                'avg inquiry rate per unique': [ 1.*int(control.groupby('looker_visitor_id').inquiries.mean().sum())/control.looker_visitor_id.nunique(), 1.*int(test.groupby('looker_visitor_id').inquiries.mean().sum())/test.looker_visitor_id.nunique()]
               }

    df_metrics = pd.DataFrame(metrics)
    cols = df_metrics.columns.tolist()
    cols = cols[1:] + cols[0:1]
    cols = cols[0:3] + cols[6:7] + cols[3:6] + cols[-1:]
    df_metrics = df_metrics[cols]
    df_metrics = df_metrics.T
    df_metrics.columns = [['control', 'test']]
    df_metrics_one = to_array(df_metrics)

    control_sum = pd.DataFrame(control.ix[:,12:22].sum(), columns=['control'])
    test_sum = pd.DataFrame(test.ix[:,12:22].sum(), columns=['test'])
    df_metrics_two = to_array(pd.merge(control_sum,test_sum,left_index=True, right_index=True))

    metrics = { 'positive LVID outcomes / uniques': [1.*control_lvid_positive/control.looker_visitor_id.nunique(),1.*test_lvid_positive/test.looker_visitor_id.nunique()],
                'positive sessions / total sessions': [1.*control.outcome.sum()/control.session_id.nunique(),1.*test.outcome.sum()/test.session_id.nunique()]
               }

    df_metrics = pd.DataFrame(metrics).T
    df_metrics.columns = [['control', 'test']]
    df_metrics_three = to_array(df_metrics)

    # Formatted-data for D3 charts
    control['status'] = 'control'
    test['status'] = 'test'
    cols = ['status', 'count_pv', 'count_artwork_pv', 'count_artist_pv', 'count_article_pv', 
        'inquiries', 'accounts_created', 'three_way_handshakes', 'three_way_handshakes_within_seven_days', 
        'purchases', 'total_purchase_price']
    control = control[cols]
    test = test[cols]
    for i in cols[1:]:
      control[i] = control[i].cumsum()
      test[i] = test[i].cumsum()
    frames = [control, test]
    d3Data = pd.concat(frames).fillna('')[cols]
    d3Data = d3Data.reset_index()
    d3Data['session_start_at'] = d3Data['session_start_at'].astype(str)

    d3Data = d3Data.to_json(orient='records')


    return [df_metrics_one, df_metrics_two, df_metrics_three, d3Data]

def run_notebook(experiment, start=None, end=None):
  print 'Requesting: ' + experiment, start, end
  exp = query_experiment_data(experiment, start, end)
  control, test = control_test_split(exp)
  return generate_metrics(control, test)

def format(experiments):
  return [x.replace('_',' ').title() for x in experiments.experiment_name.tolist()]

def get_start_end(experiment):
  start_end = sql("""
        SELECT MIN(sent_at),
               MAX(sent_at)
        FROM force_production.experiment_viewed
        WHERE experiment_name = '%s'
    """%experiment)
  return ['{:%Y-%m-%d}'.format(start_end.iloc[0]['min']), 
          '{:%Y-%m-%d}'.format(start_end.iloc[0]['max'])]
