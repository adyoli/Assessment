import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import requests
from dash.exceptions import PreventUpdate
import sqlite3

app = dash.Dash(__name__)

BASE_URL = "https://covid-api.mmediagroup.fr/v1/history?"

db = "covid_data.db"
conn = sqlite3.connect(db,check_same_thread=False) 
c = conn.cursor()

def data_access(country,country_table):
    response = requests.get(BASE_URL + f"country={country}&status=deaths")
    try:
        data = response.json()['All']['dates']
    except KeyError as e:
        return []
    data_list = data.items()

    for data in list(data_list)[::-1]:
        day = data[0]
        dead = data[1]
        sql_query = f"INSERT OR IGNORE INTO {country_table}(Date, Deaths) VALUES(?,?);"
        c.execute(sql_query,(str(day), dead))
        conn.commit()
    return data_list


def run_app():
    country = "South Africa"
    country_table = country.replace(" ", "_")
    response = requests.get(BASE_URL + f"country={country}&status=deaths")
    data = response.json()['All']['dates']
    data_list = data.items()
    sql_create = f"CREATE TABLE IF NOT EXISTS {country_table}(Date TEXT PRIMARY KEY, Deaths int);"
    c.execute(sql_create)
    conn.commit()

    for data in list(data_list)[::-1]:
        day = data[0]
        dead = data[1]
        sql_query = f"INSERT OR IGNORE INTO {country_table}(Date, Deaths) VALUES(?,?);"
        c.execute(sql_query,(str(day), dead))
        conn.commit() 

    df = pd.DataFrame(data=data_list,columns=['Date','Deaths'])

    fig = px.bar(df, x='Date', y='Deaths')
    app.layout = html.Div([
                        html.Div(
                            [html.H1(children='Covid 19 Statistics',style={'textAlign': 'center'}),
                            html.Div(children='''Search covid-19 death rates by country.''',style={'textAlign': 'center'}),
                            html.Div(dcc.Input(id='input-on-submit', placeholder="South Africa",type='text',style={'textAlign': 'center'})),
                            html.Button('Submit', id='submit-val',style={'textAlign': 'center'}),
                            html.Div(id='container-button-basic',children='Enter a value and press submit')],
                            style={'textAlign': 'center'}),
                        html.Div([dcc.Graph(id="covid-graph", figure=fig)])])

    @app.callback(Output(component_id='container-button-basic', component_property='children'),[Input('submit-val', 'n_clicks')],[State('input-on-submit', 'value')])
    def update_text(n_clicks, value):
        if n_clicks is None:
            raise PreventUpdate
        else:
            return 'Here are the covid-19 stats for  "{}"'.format("South Africa" if value == None else value)

    @app.callback(Output(component_id='covid-graph', component_property='figure'),[Input('submit-val', 'n_clicks')],[State('input-on-submit', 'value')])
    def update_graph(n_clicks, value):
        if n_clicks is None:
            raise PreventUpdate
        else:
            data_list = crud_db(value)
            df =pd.DataFrame(data=data_list,columns=['Date','Deaths'])
            fig = px.bar(df, x='Date', y='Deaths')
            return fig

def up_to_date(country):
    table_name = country.replace(" ", "_")
    last_entry_query = f"SELECT * FROM {table_name} ORDER BY column DESC LIMIT 1;"
    res = c.execute(last_entry_query)
    row = c.fetchone()
    if row == None:
        return False
    return True

def table_exists(country):
    table_name = country.replace(" ", "_")
    table_query = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name={table_name}"
    try:
        c.execute(table_query)
        return True
    except sqlite3.OperationalError:
        return False

def crud_db(country):
    country_table = country.replace(" ", "_")
    if not table_exists(country) or not up_to_date(country):
        sql_create = f"CREATE TABLE IF NOT EXISTS {country_table}(Date TEXT PRIMARY KEY, Deaths int);"
        c.execute(sql_create)
        conn.commit()
        data_access(country,country_table)

    db_query = f"SELECT * FROM {country_table}"
    data_list = c.execute(db_query).fetchall()
    return data_list

if __name__ == "__main__":
    run_app()
    app.run_server(debug=True)