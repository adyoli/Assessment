import dash
import plotly.express as px
import pandas as pd
import requests
import dash_bootstrap_components as dbc
import sqlite3
import json
import threading
import datetime
import logging
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

logging.basicConfig(filename="covid_dash.log", filemode="w")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])

BASE_URL = "https://covid-api.mmediagroup.fr/v1/history?"

DATA_BASE = "covid_data.db"
conn = sqlite3.connect(DATA_BASE, check_same_thread=False) 
c = conn.cursor()

with open('country_names.json') as f:
    countries = json.load(f)
    VALID_COUNTRIES = countries['valid_names']

lock = threading.Lock()
last_day = '2020-01-01'

def up_to_date(table_name):
    """
    This function checks whether the relevant db table has the most recent data

    Parameters:
        table_name (str): This is the name of the table 

    Returns:
        (bool): The boolean telling us if up-to-date or not
    """

    today = datetime.date.today()
    yesterday= today - datetime.timedelta(days=1)

    last_entry_query = 'SELECT * FROM "{}" ORDER BY ?'.format(table_name.replace('"', '""'))

    try:
        lock.acquire(True)
        last_day = c.execute(last_entry_query, ('Date',)).fetchall()[-1]
    except Exception as e:
        logging.error("Exception in up_to_date function", exc_info=True)
        return False
    finally:
        lock.release()

    if last_day == yesterday:
        return True
    return False


def table_exists(table_name):
    """
    This function checks whether the relevant db table exists

    Parameters:
        table_name (str): This is the name of the table 

    Returns:
        (bool): The boolean telling us if it exists or not
    """

    table_query = f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?"
    try:
        lock.acquire(True)
        c.execute(table_query,(table_name,))
        return True
    except sqlite3.OperationalError as e:
        logging.error("Exception in table_exists function", exc_info=True)
        return False
    finally:
        lock.release()


def data_access(country,country_table,status):
    """
    This function calls the api and populates the data into the database.
    This function is only called if it is the first time that db request has
    been made or if the information in the db is not up-to-date.

    Parameters:
        country (str)      : This is the name of the country in question
        country_table (str): This is the name of the table the db will need to access
        status (str)       : This is specifies wether to look for data for deaths or recoveries

    Returns:
        data_list (list): A list of tuples , (date,deaths) or (date,recovered) 
                          depending on the status
    """

    response = requests.get(BASE_URL + f"country={country}&status={status}")
    try:
        data = response.json()['All']['dates']
    except KeyError as e:
        logging.error("Exception in data_access function", exc_info=True)
        return []
    data_list = data.items()
    data_list = list(data_list)

    for data in list(data_list)[::-1]:
        day = data[0]
        condition = data[1]
        sql_query = f"INSERT OR IGNORE INTO {country_table}(Date, {status}) VALUES(?,?);"

        try:
            lock.acquire(True)
            c.execute(sql_query,(str(day), condition))
            conn.commit()
        except Exception as e:
            logging.error("Exception in data_access function", exc_info=True)
            return []
        finally:
            lock.release()

    return data_list


def crud_db(country,status):
    """
    This function handles all crud operations

    Parameters:
        country (str): This is the name of the country in question
        status  (str): This is either 'deaths' or 'recovered' and 
                       tells us whether to perfom the crud operations 
                       for the deaths table or the recovered table of
                       that specific country.

    Returns:
        data_list (list): A list of tuples , (date,deaths) or (date,recovered) 
                          depending on the status
    """

    country_table = country.replace(" ", "_")
    table_name = country_table + "_" + status
    sql_create = f"CREATE TABLE IF NOT EXISTS {table_name}(Date TEXT PRIMARY KEY, {status} int);"
    sql_select = f"SELECT * FROM {table_name}"

    if not table_exists(table_name) or not up_to_date(table_name):
        try:
            lock.acquire(True)
            c.execute(sql_create)
            conn.commit()
            
        except Exception as e:
            logging.error("Exception in data_access function", exc_info=True)
            return []
        finally:
            lock.release()
        data_list = data_access(country,table_name,status)
    else:
        data_list = c.execute(sql_select).fetchall()

    return data_list


def run_app():
    """
    This function runs everything besides the databse, it starts the application.
    Initial variables are instantiated here. The layout is also setup here.

    Parameters:

    Returns:
        (bool) : This True is to confirm that everything ran.
    """

    data_list_death = crud_db("South Africa", "Deaths")
    data_list_rec = crud_db("South Africa", "Recovered")

    df_d = pd.DataFrame(data=data_list_death ,columns=['Date', 'Deaths'])
    df_d['Deaths'] = -1*df_d['Deaths'].diff()
    fig_a = px.bar(df_d, x='Date', y='Deaths')
    fig_a.update_layout(title={'text':"Daily deaths", 'y':0.9, 'x':0.5})

    df_r = pd.DataFrame(data=data_list_rec,columns=['Date', 'Recovered'])
    fig_b = px.bar(df_r, x='Date', y='Recovered')
    fig_b.update_layout(title={'text':"Total recoveries", 'y':0.9, 'x':0.5})

    app.layout = html.Div(
        children = [
            html.Br(),
            html.H1(children='Covid-19 Dashboard',style={'textAlign': 'center'}),
            html.Br(),
            dbc.Row(
                children=[
                    dbc.Col(dcc.Dropdown(
                                id='input-on-submit', 
                                placeholder="Please enter a country...", 
                                options=VALID_COUNTRIES,
                                style={'text-align':'center','width' : '100%'})),
                    dbc.Col(dbc.Button(
                                children=['Submit'], 
                                id='submit-val',
                                size='md',
                                style={'text-align':'center','width' : '100%'})
                            )
                ],
                style={"padding-right" : "20%", "padding-left" : "20%"}
            ),
            html.Br(),
            html.H3(id='country-name',children='South Africa',style={'textAlign': 'center'}),
            dbc.Row(dbc.Col(dcc.Loading(
                                children=[
                                    dcc.Graph(id="covid-death-graph", figure=fig_a),
                                    dcc.Graph(id="covid-recovery-graph", figure=fig_b)
                                ],
                                style={'display':'flex', 'justify-content':'center'}
                            )
                    )
            )
        ]
    )

    @app.callback(Output(component_id='country-name', component_property='children'),
                [Input('submit-val', 'n_clicks')],
                [State('input-on-submit', 'value')]
    )
    def update_title(n_clicks, value):
        """
        This function with the callback refreshes the name 
        of the country show at the top of the graphs.

        Parameters:
            n_clicks (int): This is the number of times the button is clicked
            value    (str): This it the name of the country

        Returns:
            fig (plotly.graph_objs._figure.Figure): This object will allow us to plot the graph
        """
        if n_clicks is None:
            raise PreventUpdate
        else:
            return value


    @app.callback(Output(component_id='covid-death-graph', component_property='figure'),
                [Input('submit-val', 'n_clicks')],
                [State('input-on-submit', 'value')]
    )
    def update_graph_death(n_clicks, value):
        """
        This function with the callback refreshes the deaths graph

        Parameters:
            n_clicks (int): This is the number of times the button is clicked
            value    (str): This it the name of the country

        Returns:
            fig (plotly.graph_objs._figure.Figure): This object will allow us to plot the graph
        """
        if n_clicks is None:
            raise PreventUpdate
        else:
            data_list_dead = crud_db(value, 'deaths')
            df_d =pd.DataFrame(data=data_list_dead,columns=['Date', 'Deaths'])
            df_d['Deaths'] = -1*df_d['Deaths'].diff()
            fig = px.bar(df_d, x='Date', y='Deaths')
            fig.update_layout(title={'text':"Daily deaths", 'y':0.9, 'x':0.5})
            return fig


    @app.callback(Output(component_id='covid-recovery-graph', component_property='figure'),
                [Input('submit-val', 'n_clicks')],[State('input-on-submit', 'value')])
    def update_graph_recovery(n_clicks, value):
        """
        This function with the callback refreshes the recovery graph

        Parameters:
            n_clicks (int): This is the number of times the button is clicked
            value    (str): This it the name of the country

        Returns:
            fig (plotly.graph_objs._figure.Figure): This object will allow us to plot the graph
        """

        if n_clicks is None:
            raise PreventUpdate
        else:
            data_list = crud_db(value,'Recovered')
            df_r =pd.DataFrame(data=data_list,columns=['Date','Recovered'])
            fig = px.bar(df_r, x='Date', y='Recovered')
            fig.update_layout(title={'text':"Total recoveries", 'y':0.9,'x':0.5})
            return fig


if __name__ == "__main__":
    run_app()
    app.run_server(debug=False)


""" And so it goes ..."""