import requests
import json
import pandas as pd

class digfr:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://digfr.info"
        # self.base_url = "http://127.0.0.1:5000/"

    def _post_request(self, endpoint, params):
        url = f"{self.base_url}/{endpoint}?"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers = headers, json= params)

        if response.status_code == 200:
            response_text = json.loads(response.text)
            if response_text['ret'] != 0:
                df = pd.DataFrame([response_text])
            else:
                df = pd.DataFrame(response_text['E_T_DATA']['data']) 
            return df
        else:
            raise Exception(f"API request failed with status code: {response.status_code}")

    def fr_data(self, com_code, frname, syear, eyear = '', quarter = [1,2,3,4], unit = '元'): # Get report data
        
        if not isinstance(com_code, str):
            raise ValueError("com_code must be a string")
        if not isinstance(frname, str): 
            raise ValueError("frname must be a string")
        if not isinstance(syear, (str, int)):
            raise ValueError("syear must be a string or integer")
        if not isinstance(eyear, (str, int)) and eyear != '':
            raise ValueError("eyear must be a string or integer or an empty string")
        if not isinstance(unit, str):
            raise ValueError("unit must be a string")
        if not isinstance(quarter, list):
            raise ValueError("quarter must be a list")

        com_code = str(com_code)
        frname = str(frname)
        syear = str(syear)
        eyear = str(eyear) if eyear else syear
        unit = str(unit)

        params = {
            "token": self.token,
            "com_code": com_code,
            "unit": unit,
            "frname": frname,
            "syear": syear,
            "eyear": syear if eyear == '' else eyear,
            "quarter": quarter,
        }
        return self._post_request('fr_data', params)

    def fr_show(self): # Get a list of report names
        params = {
            "token": self.token
        }
        return self._post_request('fr_show', params)