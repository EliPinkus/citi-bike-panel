import panel as pn
import pandas as pd
import os
pn.extension()
annual_count_df = pd.read_parquet('annual_count.parq')
monthly_count_df = pd.read_parquet('monthly_count.parq')

print('READING data from S3')
df = dd.read_parquet(
    's3://citi-bike-demo-app/cleaned.parq/', 
    storage_options = {'key': os.environ["AWS_ACCESS_KEY_ID"], 'secret': os.environ["AWS_SECRET_ACCESS_KEY"]}, 
    columns = ['startedat', 'startstationname', 'endstationname', 'startlng', 'startlat']
)
print('DONE READING data from S3')
df = df.compute()
df = df.set_index('startedat')

endstations = df.endstationname.unique()
startstations = df.startstationname.unique()
starts = pn.widgets.MultiChoice(options=list(startstations), value=[], name='Select Start Stations')
ends = pn.widgets.MultiChoice(options=list(endstations), value=[], name='Select End Stations')
breakdown = pn.widgets.Select(options=['monthly', 'annually'], value='annually', name='Select Breakdown Granularity')

def annual_count(df, startstations, endstations, breakdown='monthly'):
    if startstations or endstations:
        if startstations:
            df = df[df.startstationname.isin(startstations)]
        if endstations:
            df = df[df.endstationname.isin(endstations)]
        annual_df = df['endstationname'].resample('Y' if breakdown=='annually' else 'M').count()
    else:
        annual_df = annual_count_df if breakdown=='annually' else monthly_count_df
    return px.scatter(annual_df, x=annual_df.index, y='endstationname', template='simple_white', trendline='ols')

app = pn.Column(
    pn.Row(
        pn.Column('# Ride Count Over Time', starts, ends, breakdown),
        pn.bind(annual_count, df, ends, starts, breakdown)
    ),
)
app.servable()