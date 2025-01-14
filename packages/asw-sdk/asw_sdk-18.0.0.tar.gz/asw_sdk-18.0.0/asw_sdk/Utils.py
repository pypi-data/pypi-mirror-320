from asw_sdk.ConfigurationManager import ConfigurationManager
from asw_sdk.WebClient import WebClient
from enum import Enum

import os
import json
from datetime import datetime, timezone


class LogLevel(Enum):
    INFO = 1900
    FAILED = 1800
    SUCCESS = 2000


def generate_json_parseable_message(message):
    message = message.replace('\\', '\\\\')
    message = message.replace('\b', '\\b')
    message = message.replace('\f', '\\f')
    message = message.replace('\n', '\\n')
    message = message.replace('\r', '\\r')
    message = message.replace('\t', '\\t')
    message = message.replace('"', '\\"')
    return message


class Utils:
    def __init__(self, override_config=None, overriden_config_node=None):
        self._config_manager = None
        if overriden_config_node and override_config:
            self._config_manager = ConfigurationManager(overriden_config_node, override_config)
        else:
            self._config_manager = ConfigurationManager(os.environ['PYTHON_CONFIG_NODE'])
        self._web_client = WebClient("exec", self._config_manager)
        self._web_client.refresh_token()

    def print(self, message, level=LogLevel.INFO):
        log_request_body = self.generate_log_request_body()
        if type(message) is dict:
            message = json.dumps(message)
        message = generate_json_parseable_message(message)
        if log_request_body["operations_key"] is None:
            print(message)
            return
        filter_log_request_body_as_string = f'{{"displayMessage": null, "filterId": {log_request_body["filter_id"]}, "filterName": "{log_request_body["filter_name"]}", "filterProgressStatusValue": {level.value}, "id": null, "jobId": {log_request_body["job_id"]}, "logDate": "{log_request_body["now"]}", "messageError": "{message}", "operationsKey": "{log_request_body["operations_key"]}"}}'
        print('filter_log_request_body_as_string', filter_log_request_body_as_string)
        filter_progress_log_endpoint = f'/job-stream/external-filter-progress'
        filter_log_request_body_as_json = json.loads(filter_log_request_body_as_string)
        print('filter_log_request_body_as_json', filter_log_request_body_as_json)
        self._web_client.post_entity(filter_progress_log_endpoint, json_data=filter_log_request_body_as_json, headers={})

    def generate_log_request_body(self):
        properties = {
            "operations_key": self._config_manager.get_operations_key(),
            "now": datetime.now(timezone.utc).isoformat(),
            "filter_id": self._config_manager.get_filter_id() if self._config_manager.get_filter_id() is not None else "null",
            "job_id": self._config_manager.get_currently_executing_job_id() if self._config_manager.get_currently_executing_job_id() is not None else "null",
            "filter_name": self._config_manager.get_currently_executing_step_name()
        }
        return properties


if __name__ == '__main__':
    # os.environ['PYTHON_CONFIG'] = '{    \\"TOKEN\\" : \\"eyJob3N0TmFtZSI6Imh0dHBzOi8vcWluc3RhbmNlMS10ZW5hbnQxLnFhMS5jaXR0YWRhdGEuY29tIiwicmVmcmVzaFRva2VuIjoicl85TGZHa1EzQnQ3U3ZOdmFHIiwid3NIb3N0TmFtZSI6IndzczovL3FpbnN0YW5jZTEtdGVuYW50MS53cy5xYTEuY2l0dGFkYXRhLmNvbSJ9\\",    \\"nodes\\" : {        \\"65ee6b4abf0743e9988255406c410280\\" : {            \\"applicationDataTypeId\\" : 8657,            \\"applicationGroupId\\" : 5578,            \\"cittaAgent\\" : {                \\"launcher\\" : {                    \\"pipelineConf\\" : {                        \\"executionProfileId\\" : \\"ep1\\",                        \\"executionProfileObjectName\\" : \\"exp_object_name\\",                        \\"filterName\\" : \\"smm-training\\",                        \\"groupId\\" : 1,                        \\"hostName\\" : \\"https://qinstance1-tenant1.qa1.cittadata.com\\",                        \\"jobCode\\" : \\"GVGWFHBMKMJUAGR\\",                        \\"mlCode\\" : \\"ml_code1\\",                        \\"mlModelApiName\\" : \\"ml_model_api\\",                        \\"mlModelObjectName\\" : \\"ml_model\\",                        \\"mlModelVersionApi\\" : \\"ml_model_versions_api\\",                        \\"mlModelVersionMetricsApi\\" : \\"ml_model_version_metrics_api\\",                        \\"mlModelVersionMetricsObjectName\\" : \\"ml_model_version_metrics\\",                        \\"mlModelVersionObjectName\\" : \\"ml_model_versions\\",                        \\"runId\\" : \\"test_runId\\",                        \\"wsHostName\\" : \\"wss://qinstance1-tenant1.ws.qa1.cittadata.com\\"                    }                }            },            \\"currentFilterId\\" : 4094,            \\"currentlyExecutingJobId\\" : 4094,            \\"invokingAppInstanceId\\" : 6238,            \\"rootDagContextId\\" : 7426,            \\"sessionCode\\" : \\"zpss_34_67_7987\\",            \\"versionTagId\\" : 5677        }    },    \\"operationsKey\\" : \\"534313297\\",    \\"tenantDataFolder\\" : \\"alpha.tenant.data/qinstance1-tenant1\\"}'
    os.environ['PYTHON_CONFIG'] = '{    \\"TOKEN\\" : \\"eyJob3N0TmFtZSI6Imh0dHBzOi8vcWluc3RhbmNlMS10ZW5hbnQxLnFhMS5jaXR0YWRhdGEuY29tIiwicmVmcmVzaFRva2VuIjoicl85TGZHa1EzQnQ3U3ZOdmFHIiwid3NIb3N0TmFtZSI6IndzczovL3FpbnN0YW5jZTEtdGVuYW50MS53cy5xYTEuY2l0dGFkYXRhLmNvbSJ9\\",    \\"nodes\\" : {        \\"65ee6b4abf0743e9988255406c410280\\" : {            \\"applicationDataTypeId\\" : 8657,            \\"applicationGroupId\\" : 5578,            \\"cittaAgent\\" : {                \\"launcher\\" : {                    \\"pipelineConf\\" : {                        \\"executionProfileId\\" : \\"ep1\\",                        \\"executionProfileObjectName\\" : \\"exp_object_name\\",                        \\"filterName\\" : \\"smm-training\\",                        \\"groupId\\" : 1,                        \\"hostName\\" : \\"https://qinstance1-tenant1.qa1.cittadata.com\\",                        \\"jobCode\\" : \\"GVGWFHBMKMJUAGR\\",                        \\"mlCode\\" : \\"ml_code1\\",                        \\"mlModelApiName\\" : \\"ml_model_api\\",                        \\"mlModelObjectName\\" : \\"ml_model\\",                        \\"mlModelVersionApi\\" : \\"ml_model_versions_api\\",                        \\"mlModelVersionMetricsApi\\" : \\"ml_model_version_metrics_api\\",                        \\"mlModelVersionMetricsObjectName\\" : \\"ml_model_version_metrics\\",                        \\"mlModelVersionObjectName\\" : \\"ml_model_versions\\",                        \\"runId\\" : \\"test_runId\\",                        \\"wsHostName\\" : \\"wss://qinstance1-tenant1.ws.qa1.cittadata.com\\"                    }                }            },            \\"currentFilterId\\" : 4094,            \\"currentlyExecutingJobId\\" : 4094,            \\"invokingAppInstanceId\\" : 6238,            \\"rootDagContextId\\" : 7426,            \\"sessionCode\\" : \\"zpss_34_67_7987\\",            \\"versionTagId\\" : 5677        }    },    \\"tenantDataFolder\\" : \\"alpha.tenant.data/qinstance1-tenant1\\"}'
    os.environ['PYTHON_CONFIG_NODE'] = '65ee6b4abf0743e9988255406c410280'
    utils = Utils()
    sample_dict = {'data': {'ml_model_api': {'nodes': [{'step_id': 'smm-1', 'ml_model_id': '1', 'ml_code': 'ml_code1', 'job_code': 'GVGWFHBMKMJUAGR', 'is_deleted': False, 'group_id': '1', 'mlModelVersionsApis': {'nodes': [{'additional_params_json': '{}', 'hyperparameter_json': "{name:'x',value:'1', age:20, type:'t1'}", 'is_active': True, 'is_deleted': False, 'ml_model_id': '1', 'ml_model_versions_id': '265', 'model_location': 's3://alpha.tenant.data/qinstance1-tenant1/ml_models/xgboost_on_iris.xgb', 'run_id': 'test_runId', 'run_through': '1', 'target_columns_json': "['abc','cde','efg']", 'training_features_json': "[{name:'x',value:'1'},{name:'y',value:'2'}]", 'version': 9, 'mlModelVersionMetricsByMlModelVersionsId': {'nodes': [{'chart_type': 'line', 'is_deleted': False, 'ml_model_version_metrics_id': '265', 'ml_model_versions_id': '265', 'name': 'char_name', 'value': '[{x:100,y:100}]'}]}, 'description': 'version desc 1'}, {'additional_params_json': '{}', 'hyperparameter_json': "{name:'x',value:'1', age:20, type:'t1'}", 'is_active': True, 'is_deleted': False, 'ml_model_id': '1', 'ml_model_versions_id': '364', 'model_location': 's3://alpha.tenant.data/qinstance1-tenant1/ml_models/xgboost_on_iris.xgb', 'run_id': 'test_runId', 'run_through': '1', 'target_columns_json': "['abc','cde','efg']", 'training_features_json': "[{name:'x',value:'1'},{name:'y',value:'2'}]", 'version': 12, 'mlModelVersionMetricsByMlModelVersionsId': {'nodes': [{'chart_type': 'line', 'is_deleted': False, 'ml_model_version_metrics_id': '364', 'ml_model_versions_id': '364', 'name': 'char_name', 'value': '[{x:100,y:100}]'}]}, 'description': 'version desc 1'}, {'additional_params_json': '{}', 'hyperparameter_json': "{name:'x',value:'1', age:20, type:'t1'}", 'is_active': True, 'is_deleted': False, 'ml_model_id': '1', 'ml_model_versions_id': '397', 'model_location': 's3://alpha.tenant.data/qinstance1-tenant1/ml_models/xgboost_on_iris.xgb', 'run_id': 'test_runId', 'run_through': '1', 'target_columns_json': "['abc','cde','efg']", 'training_features_json': "[{name:'x',value:'1'},{name:'y',value:'2'}]", 'version': 13, 'mlModelVersionMetricsByMlModelVersionsId': {'nodes': [{'chart_type': 'line', 'is_deleted': False, 'ml_model_version_metrics_id': '397', 'ml_model_versions_id': '397', 'name': 'char_name', 'value': '[{x:100,y:100}]'}]}, 'description': 'version desc 1'}]}}]}}}
    utils.print(sample_dict)
    utils.print("Hello World")
    data = '''
    {
      "name": "John Doe",
      "age": 30,
      "isDeveloper": true,
      "languages": [
        "Python",
        "JavaScript",
        "Java"
      ],
      "address": {
        "street": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "postalCode": "62701"
      }
    }
    '''
    utils.print(data)
