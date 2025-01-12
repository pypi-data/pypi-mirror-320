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
        response = requests.post(url, headers = headers, data=json.dumps(params))

        if response.status_code == 200:
            response_text = json.loads(response.text)
            if response_text['ret'] != 0:
                df = pd.DataFrame([response_text])
            else:
                df = pd.DataFrame(response_text['E_T_DATA']['data']) 
            return df
        else:
            raise Exception(f"API request failed with status code: {response.status_code}")

    def fr_data(self, com_code, frname, syear, eyear='', quarter=[1,2,3,4], unit = '元'): # Get report data
        params = {
            "token": self.token,
            "com_code": com_code,
            "unit": unit,
            "frname": frname,
            "syear": syear,
            "eyear": syear if eyear=='' else eyear,
            "quarter": quarter,
        }
        return self._post_request('fr_data', params)

    def fr_show(self): # Get a list of report names
        params = {
            "token": self.token
        }
        return self._post_request('fr_show', params)