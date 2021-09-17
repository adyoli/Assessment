import unittest
import covid_dash as covid
import os
from dash.testing.application_runners import import_app

class TestCases(unittest.TestCase):
    """ Due to time contraints I'll leave you with these measly tests. """

    """
    def test_one(self):
        app = import_app("covid_dash.py")
        self.dash_duo.start_server(app)
        self.dash_duo.wait_for_text_to_equal("h1", "Covid 19 Statistics", timeout=4)
    """

    def test_db_connection(self):
        db_exists = os.path.exists("covid_data.db")
        self.assertTrue(db_exists)

    def test_api_connection(self):
        data_list = covid.data_access("South Africa", "South_Africa")
        self.assertGreater(len(data_list),0)

    def test_input_comp(self):
        jsn = covid.app.callback_map
        print(jsn)
        self.assertEqual(jsn['container-button-basic.children']['inputs'],[{'id': 'submit-val', 'property': 'n_clicks'}])

    def test_state(self):
        jsn = covid.app.callback_map
        self.assertEqual(jsn['container-button-basic.children']['state'],[{'id': 'input-on-submit', 'property': 'value'}])

if __name__ == '__main__':
	unittest.main()
