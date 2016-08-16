import os 
import warnings
import numpy as np
import pandas as pd
import pymc as pm

from sqlalchemy import create_engine
engine_string = os.environ['REDSHIFT_CONN']
engine = create_engine(engine_string)

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

def query_experiment_data(exp_name, start_date, end_date):

    # pulls the first and last experiment logged
    start_end = sql("""
        SELECT MIN(sent_at),
               MAX(sent_at)
        FROM force_production.experiment_viewed
        WHERE experiment_name = '%s'
    """%exp_name)

    # selects the value from the data frame
    first_log_of_exp = start_end.iloc[0]['min']
    last_log_of_exp = start_end.iloc[0]['max']

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
    print df_metrics
    print

    control_sum = pd.DataFrame(control.ix[:,12:22].sum(), columns=['control'])
    test_sum = pd.DataFrame(test.ix[:,12:22].sum(), columns=['test'])
    print pd.merge(control_sum,test_sum,left_index=True,right_index=True)
    print 

    metrics = { 'positive LVID outcomes / uniques': [1.*control_lvid_positive/control.looker_visitor_id.nunique(),1.*test_lvid_positive/test.looker_visitor_id.nunique()],
                'positive sessions / total sessions': [1.*control.outcome.sum()/control.session_id.nunique(),1.*test.outcome.sum()/test.session_id.nunique()]
               }

    df_metrics = pd.DataFrame(metrics).T
    df_metrics.columns = [['control', 'test']]
    print df_metrics
    print '-'*70
    print

'''
exp = query_experiment_data('personalized_homepage', '2016-07-25', '2016-07-26')
control, test = control_test_split(exp)
generate_metrics(control, test)
'''
