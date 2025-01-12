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
        for k,v in params.items():
            url +=  f"{k}={v}&"
        # print(url)

        response = requests.get(url, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            response_text = json.loads(response.text)
            if response_text['ret'] != 0:
                df = pd.DataFrame([response_text])
            else:
                df = pd.DataFrame(response_text['E_T_DATA']['data']) 
            return df
        else:
            raise Exception(f"API request failed with status code: {response.status_code}")

    def fr_data(self, com_code, frname, syear, eyear, quarter, unit = '元'): # 获取报表数据
        params = {
            "token": self.token,
            "com_code": com_code,
            "unit": unit,
            "frname": frname,
            "syear": syear,
            "eyear": eyear,
            "quarter": quarter,
        }
        return self._post_request('fr_data', params)

    def fr_show(self): # 获取报表名称列表
        params = {
            "token": self.token,
        }
        return self._post_request('fr_show', params)