import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import wbdata
import pandas as pd
import datetime
import plotly.express as px

cache_file = 'wbdata_cache.pkl'
start_year, end_year = 2000, 2020
data_date = (datetime.datetime(start_year, 1, 1), datetime.datetime(end_year, 1, 1))

indicators = {
    'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
    'SP.DYN.LE00.IN': 'Life expectancy at birth (years)',
    'SH.H2O.SMDW.ZS': 'Access to clean water (% pop)'
}

if os.path.exists(cache_file):
    print(f"Loading data from cache ({cache_file})...")
    raw_df = pd.read_pickle(cache_file)
else:
    print("Fetching data from World Bank API...")
    raw_df = wbdata.get_dataframe(indicators, date=data_date)
    raw_df.to_pickle(cache_file)

df = raw_df.reset_index()
if isinstance(df.loc[0, 'country'], dict):
    df['iso2'] = df['country'].apply(lambda x: x.get('id'))
    df['country_name'] = df['country'].apply(lambda x: x.get('value'))
else:
    df['iso2'] = df['country']
    df['country_name'] = df['country']
df['Year'] = pd.to_datetime(df['date']).dt.year
df.rename(columns=indicators, inplace=True)

print("Loaded data for years:", df['Year'].min(), "to", df['Year'].max())
print(df[['iso2', 'country_name', 'Year', 'GDP per capita (current US$)', 'Life expectancy at birth (years)']].head())

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1(f"World Bank Dashboard: {start_year}-{end_year}"),
    html.Div([
        dcc.Graph(id='gdp-life-scatter'),
        dcc.Graph(id='water-access-bar')
    ], style={'display': 'flex', 'justify-content': 'space-between'})
])

@app.callback(
    Output('gdp-life-scatter', 'figure'),
    Output('water-access-bar', 'figure'),
    Input('gdp-life-scatter', 'clickData'),
    Input('water-access-bar', 'clickData')
)
def update_figures(click_scatter, click_bar):
    dff = df.copy()
    selected = []
    if click_scatter:
        selected = [pt['customdata'][0] for pt in click_scatter['points']]
    elif click_bar:
        selected = [pt['customdata'][0] for pt in click_bar['points']]
    if selected:
        dff = dff[dff['iso2'].isin(selected)]

    # Chart 1: GDP vs Life Expectancy over time
    fig1 = px.scatter(
        dff,
        x='GDP per capita (current US$)',
        y='Life expectancy at birth (years)',
        animation_frame='Year',
        animation_group='iso2',
        color='country_name',
        custom_data=['iso2', 'country_name'],
        title='GDP per Capita vs Life Expectancy (2000-2020)',
        labels={
            'GDP per capita (current US$)': 'GDP per Capita (US$)',
            'Life expectancy at birth (years)': 'Life Expectancy (years)'
        }
    )
    fig1.update_layout(clickmode='event+select')

    # Chart 2: Clean Water Access by Country (latest year, top 15)
    latest = dff[dff['Year'] == end_year]
    bar_df = latest[['iso2', 'country_name', 'Access to clean water (% pop)']]
    bar_df = bar_df.sort_values('Access to clean water (% pop)', ascending=False).head(15)
    fig2 = px.bar(
        bar_df,
        x='country_name',
        y='Access to clean water (% pop)',
        custom_data=['iso2', 'country_name'],
        title=f'Top 15 Countries by Clean Water Access ({end_year})',
        labels={'Access to clean water (% pop)': 'Clean Water Access (%)'}
    )
    fig2.update_layout(xaxis_tickangle=-45, clickmode='event+select')

    return fig1, fig2

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)# import os
# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import wbdata
# import pandas as pd
# import datetime
# import plotly.express as px

# cache_file = 'wbdata_cache.pkl'
# start_year, end_year = 2000, 2020
# data_date = (datetime.datetime(start_year, 1, 1), datetime.datetime(end_year, 1, 1))

# indicators = {
#     'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
#     'SP.DYN.LE00.IN': 'Life expectancy at birth (years)',
#     'SH.H2O.SMDW.ZS': 'Access to clean water (% pop)'
# }

# if os.path.exists(cache_file):
#     print(f"Loading data from cache ({cache_file})...")
#     raw_df = pd.read_pickle(cache_file)
# else:
#     print("Fetching data from World Bank API...")
#     raw_df = wbdata.get_dataframe(indicators, date=data_date)
#     raw_df.to_pickle(cache_file)

# df = raw_df.reset_index()
# if isinstance(df.loc[0, 'country'], dict):
#     df['iso2'] = df['country'].apply(lambda x: x.get('id'))
#     df['country_name'] = df['country'].apply(lambda x: x.get('value'))
# else:
#     df['iso2'] = df['country']
#     df['country_name'] = df['country']
# df['Year'] = pd.to_datetime(df['date']).dt.year
# df.rename(columns=indicators, inplace=True)

# print("Loaded data for years:", df['Year'].min(), "to", df['Year'].max())
# print(df[['iso2', 'country_name', 'Year', 'GDP per capita (current US$)', 'Life expectancy at birth (years)']].head())

# app = dash.Dash(__name__)
# server = app.server
# app.layout = html.Div([
#     html.H1(f"World Bank Dashboard: {start_year}-{end_year}"),
#     html.Div([
#         dcc.Graph(id='gdp-life-scatter'),
#         dcc.Graph(id='water-access-bar')
#     ], style={'display': 'flex', 'justify-content': 'space-between'})
# ])

# @app.callback(
#     Output('gdp-life-scatter', 'figure'),
#     Output('water-access-bar', 'figure'),
#     Input('gdp-life-scatter', 'clickData'),
#     Input('water-access-bar', 'clickData')
# )
# def update_figures(click_scatter, click_bar):
#     dff = df.copy()
#     selected = []
#     if click_scatter:
#         selected = [pt['customdata'][0] for pt in click_scatter['points']]
#     elif click_bar:
#         selected = [pt['customdata'][0] for pt in click_bar['points']]
#     if selected:
#         dff = dff[dff['iso2'].isin(selected)]

#     # Chart 1: GDP vs Life Expectancy over time
#     fig1 = px.scatter(
#         dff,
#         x='GDP per capita (current US$)',
#         y='Life expectancy at birth (years)',
#         animation_frame='Year',
#         animation_group='iso2',
#         color='country_name',
#         custom_data=['iso2', 'country_name'],
#         title='GDP per Capita vs Life Expectancy (2000-2020)',
#         labels={
#             'GDP per capita (current US$)': 'GDP per Capita (US$)',
#             'Life expectancy at birth (years)': 'Life Expectancy (years)'
#         }
#     )
#     fig1.update_layout(clickmode='event+select')

#     # Chart 2: Clean Water Access by Country (latest year, top 15)
#     latest = dff[dff['Year'] == end_year]
#     bar_df = latest[['iso2', 'country_name', 'Access to clean water (% pop)']]
#     bar_df = bar_df.sort_values('Access to clean water (% pop)', ascending=False).head(15)
#     fig2 = px.bar(
#         bar_df,
#         x='country_name',
#         y='Access to clean water (% pop)',
#         custom_data=['iso2', 'country_name'],
#         title=f'Top 15 Countries by Clean Water Access ({end_year})',
#         labels={'Access to clean water (% pop)': 'Clean Water Access (%)'}
#     )
#     fig2.update_layout(xaxis_tickangle=-45, clickmode='event+select')

#     return fig1, fig2

# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=False)


import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import wbdata
import pandas as pd
import datetime
import plotly.express as px

cache_file = 'wbdata_cache.pkl'
start_year, end_year = 2000, 2020
data_date = (datetime.datetime(start_year, 1, 1), datetime.datetime(end_year, 1, 1))


indicators = {
    'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
    'SP.DYN.LE00.IN': 'Life expectancy at birth (years)',
    'SH.H2O.SMDW.ZS': 'Access to clean water (% pop)'
}


if os.path.exists(cache_file):
    print(f"Loading data from cache ({cache_file})...")
    raw_df = pd.read_pickle(cache_file)
else:
    print("Fetching data from World Bank API...")
    raw_df = wbdata.get_dataframe(indicators, date=data_date)
    raw_df.to_pickle(cache_file)


df = raw_df.reset_index()

if isinstance(df.loc[0, 'country'], dict):
    df['iso2'] = df['country'].apply(lambda x: x.get('id'))
    df['country_name'] = df['country'].apply(lambda x: x.get('value'))
else:
    df['iso2'] = df['country']
    df['country_name'] = df['country']

df['Year'] = pd.to_datetime(df['date']).dt.year

df.rename(columns=indicators, inplace=True)


print(f"Loaded data for years: {df['Year'].min()} to {df['Year'].max()}")


app = dash.Dash(__name__)
server = app.server  # expose Flask server for Gunicorn
app.layout = html.Div([
    html.H1(f"World Bank Dashboard: {start_year}-{end_year}"),
    html.Div([
        dcc.Graph(id='gdp-life-scatter'),
        dcc.Graph(id='water-access-bar')
    ], style={'display': 'flex', 'justify-content': 'space-between'})
])


@app.callback(
    Output('gdp-life-scatter', 'figure'),
    Output('water-access-bar', 'figure'),
    Input('gdp-life-scatter', 'clickData'),
    Input('water-access-bar', 'clickData')
)
def update_figures(click_scatter, click_bar):
    dff = df.copy()
    selected = []
    if click_scatter:
        selected = [pt['customdata'][0] for pt in click_scatter['points']]
    elif click_bar:
        selected = [pt['customdata'][0] for pt in click_bar['points']]
    if selected:
        dff = dff[dff['iso2'].isin(selected)]

    # Chart 1: GDP vs Life Expectancy over time
    fig1 = px.scatter(
        dff,
        x='GDP per capita (current US$)',
        y='Life expectancy at birth (years)',
        animation_frame='Year',
        animation_group='iso2',
        color='country_name',
        custom_data=['iso2', 'country_name'],
        title='GDP per Capita vs Life Expectancy (2000-2020)',
        labels={
            'GDP per capita (current US$)': 'GDP per Capita (US$)',
            'Life expectancy at birth (years)': 'Life Expectancy (years)'
        }
    )
    fig1.update_layout(clickmode='event+select')

    # Chart 2: Top 15 Countries by Clean Water Access in latest year
    latest = dff[dff['Year'] == end_year]
    water_df = latest[['country_name', 'Access to clean water (% pop)', 'iso2']]
    water_df = water_df.sort_values('Access to clean water (% pop)', ascending=False).head(15)
    fig2 = px.bar(
        water_df,
        x='country_name',
        y='Access to clean water (% pop)',
        custom_data=['iso2', 'country_name'],
        title=f'Top 15 Countries by Clean Water Access ({end_year})',
        labels={'Access to clean water (% pop)': 'Clean Water Access (%)'}
    )
    fig2.update_layout(xaxis_tickangle=-45, clickmode='event+select')

    return fig1, fig2


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


