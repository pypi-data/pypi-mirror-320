import requests
import backoff
import base64
from http.cookies import SimpleCookie

def should_retry(response_or_exception):
    print(f'Checking if the GET request should be retried. Received response: {response_or_exception}')
    if isinstance(response_or_exception, requests.Response):
        return response_or_exception.status_code == 560
    elif isinstance(response_or_exception, requests.exceptions.RequestException):
        return True
    return False

def backoff_handler(details):
    print ("Backing off {wait:0.1f} seconds after {tries} tries "
           "calling function {target} with args {args} and kwargs "
           "{kwargs}".format(**details))

class WebClient:
    AUTHORIZATION = "Authorization"
    QUERY_PARAM_FOR_APP_INSTANCE_ID = "appInstanceId"
    QUERY_PARAM_BITEMPORAL_PROPS = "biTemporalProps"
    QUERY_PARAM_TIME_LABEL_PROP = "timeLabel"
    QUERY_PARAM_CURRENTLY_EXECUTING_JOB_ID = "currentJobId"
    ML_CODE_PROP = "mlCode"
    GROUP_ID = "groupId"
    AGI_ID = "agiId"

    def __init__(self, base_url, config_manager, use_app_instance_session_code=False):
        self.auth_token = ""
        self.configManager = config_manager
        self._host_name = self.configManager.get_host_name()
        self._session_code = self.configManager.get_app_instance_session_code() if use_app_instance_session_code \
            else self.configManager.get_session_code()
        self._base_url = self._host_name + "/" + base_url + "/" + self._session_code

    def _attach_headers(self, headers):
        if headers is None:
            headers = {}
        # headers[self.AUTHORIZATION] = self.auth_token
        headers["cookie"] = 'auth="'+self.auth_token+'"'
        if self.configManager.get_currently_executing_job_id() is not None:
            headers[self.QUERY_PARAM_CURRENTLY_EXECUTING_JOB_ID] = str(self.configManager.get_currently_executing_job_id())
        if self.configManager.get_current_app_instance_id() is not None:
            headers[self.QUERY_PARAM_FOR_APP_INSTANCE_ID] = self.configManager.get_current_app_instance_id()

    @backoff.on_predicate(backoff.expo, should_retry, max_tries=5, on_backoff=backoff_handler)
    def get_entity(self, endpoint, params=None, headers=None, set_headers=True):
        if set_headers:
            self._attach_headers(headers=headers)
            url = self._base_url + endpoint
        else:
            url = endpoint
        try:
            response = requests.get(url, params=params, headers=headers, verify=True)
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"An HTTP error occurred: {e}")

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
    def post_entity(self, endpoint, params=None, json_data=None, headers=None):
        self._attach_headers(headers=headers)
        url = self._base_url + endpoint
        try:
            response = requests.post(url, params=params, json=json_data, headers=headers, verify=False)
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"An HTTP error occurred: {e}")

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
    def put_entity(self, endpoint, params=None, json_data=None, headers=None):
        self._attach_headers(headers=headers)
        url = self._base_url + endpoint
        try:
            response = requests.put(url, params=params, json=json_data, headers=headers, verify=False)
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"An HTTP error occurred: {e}")

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
    def delete_entity(self, endpoint, params=None, data=None, headers=None):
        self._attach_headers(headers=headers)
        url = self._base_url + endpoint
        try:
            response = requests.delete(url, params=params, data=data, headers=headers, verify=False)
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"An HTTP error occurred: {e}")

    def refresh_token(self):
        headers = {"refresh": self.configManager.get_refresh_token()}
        response = requests.get(self._host_name + "/" + "orgs/auth/refresh", headers=headers, verify=False)
        refresh_cookies = response.headers["set-cookie"]
        cookie = SimpleCookie()
        cookie.load(refresh_cookies)
        authorization_token = cookie.get("auth").value
        self.auth_token = authorization_token
