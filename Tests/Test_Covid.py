import unittest
import dash
import covid_dash as covid
import datetime
import sqlite3
import threading
import dash_bootstrap_components as dbc
import time
import sys
import os
from dash import dcc


lock = threading.Lock()

class TestCases(unittest.TestCase):
    dash_obj = covid.app

    def test_create_dash_obj(self):
        self.assertEqual(dash.dash.Dash,type(self.dash_obj))

    def test_database_connection(self):
        self.assertEqual(dash.dash.Dash,type(self.dash_obj))

    def test_up_to_date_SA_Deaths(self):
        covid.up_to_date("South_Africa_Recovered")
        final_day = covid.last_day
        today = datetime.date.today()
        yesterday= today - datetime.timedelta(days=1)
    
        if final_day == yesterday:
            self.assertTrue(covid.up_to_date("South_Africa_Recovered"))
        else:
            self.assertFalse(covid.up_to_date("South_Africa_Recovered"))

    def test_table_exists_SA_Recovered(self):
        DATA_BASE = "covid_data.db"
        conn = sqlite3.connect(DATA_BASE, check_same_thread=False) 
        c = conn.cursor()
        table_name = "South_Africa_Recovered"
        table_query = f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?"

        try:
            lock.acquire(True)
            c.execute(table_query, ('Date',))
            exists = True
        except Exception as e:
            exists = False
        finally:
            lock.release()
        
        if exists:
            self.assertTrue(table_name)
        else:
            self.assertFalse(table_name)
  
    def test_db_connection(self):
        db_exists = os.path.exists("covid_data.db")
        self.assertTrue(db_exists)

    def test_api_connection_found(self):
        data_list = covid.data_access("South Africa", "South_Africa_Recovered","Recovered")
        self.assertGreater(len(data_list),0)

    def test_api_connection_not_found(self):
        data_list = covid.data_access("Lalaland", "Lalaland_Recovered","Recovered")
        self.assertEqual(0, len(data_list))


    def test_check_title(self):
        covid.run_app()
        jsn = covid.app.callback_map
        self.assertTrue('country-name.children' in jsn)

    def test_check_recovery_graph(self):
        covid.run_app()
        jsn = covid.app.callback_map
        self.assertTrue('covid-recovery-graph.figure' in jsn)

    def test_check_death_graph(self):
        covid.run_app()
        jsn = covid.app.callback_map
        self.assertTrue('covid-death-graph.figure' in jsn)

if __name__ == '__main__':
	unittest.main()
