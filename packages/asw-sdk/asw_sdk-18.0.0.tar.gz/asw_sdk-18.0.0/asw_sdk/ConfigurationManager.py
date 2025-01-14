import json
import os
import base64


class ConfigurationManager:
    AUTHORIZATION = "Authorization"
    INVOKING_APP_INSTANCE_ID = "invokingAppInstanceId"
    CURRENTLY_EXECUTING_JOB_ID = "currentlyExecutingJobId"
    AGI_ID = "applicationGroupId"
    ML_CODE_PROP = "mlCode"
    GROUP_ID = "groupId"
    EP_ID = "executionProfileId"
    EP_OBJECT_NAME = "executionProfileObjectName"
    ML_MODEL_API_NAME = "mlModelApiName"
    ML_MODEL_OBJECT_NAME = "mlModelObjectName"
    CURRENT_RUN_ID = "runId"
    CURRENTLY_EXECUTING_STEP_NAME = "filterName"
    ML_MODEL_VERSIONS_OBJECT_NAME = "mlModelVersionObjectName"
    ML_MODEL_VERSIONS_API = "mlModelVersionApi"
    ML_MODEL_VERSION_METRICS_OBJECT_NAME = "mlModelVersionMetricsObjectName"
    ML_MODEL_VERSION_METRICS_API = "mlModelVersionMetricsApi"
    JOB_CODE = "jobCode"
    SESSION_CODE = "sessionCode"
    TOKEN = "TOKEN"
    HOST_NAME = "hostName"
    PYTHON_CONFIG = "PYTHON_CONFIG"
    AGENT = "cittaAgent"
    LAUNCHER = "launcher"
    PIPELINE_CONF = "pipelineConf"
    TENANT_DATA_FOLDER = "tenantDataFolder"
    REFRESH = "refreshToken"
    OPERATIONS_KEY = "operationsKey"
    FILTER_ID = "currentFilterId"
    APP_SESSION_CODE = "appSessionCode"

    def __init__(self, step_code, override_config=None):

        # Load configuration from environment variable and parse JSON
        cleaned_json_string = ""
        if override_config:
            cleaned_json_string = override_config.replace("\\\"", "\"")
        else:
            cleaned_json_string = os.environ[self.PYTHON_CONFIG].replace("\\\"", "\"")
        self._all_node_config = json.loads(cleaned_json_string)
        self._step_code = step_code
        self._json_config = self._all_node_config["nodes"][step_code]

        pipeline_conf = self._json_config.get("%s" % self.AGENT, {}).get("%s" % self.LAUNCHER, {}).get("%s" % self.PIPELINE_CONF, {})
        self._filter_id = self._json_config[self.FILTER_ID] if self.FILTER_ID in self._json_config else None
        self._currently_executing_job_id = self._json_config[self.CURRENTLY_EXECUTING_JOB_ID] if self.CURRENTLY_EXECUTING_JOB_ID in self._json_config else None
        self._session_code = self._json_config[self.SESSION_CODE]
        self._app_session_code = self._json_config[self.APP_SESSION_CODE] if self.APP_SESSION_CODE in self._json_config else None
        self._agiId = str(self._json_config[self.AGI_ID]) if self.AGI_ID in self._json_config else None

        token_decoded = base64.b64decode(self._all_node_config[self.TOKEN])
        token_obj = json.loads(token_decoded)
        self._token = token_obj[self.REFRESH]
        self._host_name = token_obj[self.HOST_NAME]
        self.tenant_data_folder = self._all_node_config[self.TENANT_DATA_FOLDER]
        self.operations_key = self._all_node_config[self.OPERATIONS_KEY] if self.OPERATIONS_KEY in self._all_node_config else None

        # Extract properties from JSON configuration
        self._app_instance_id = str(self._json_config[self.INVOKING_APP_INSTANCE_ID]) if self.INVOKING_APP_INSTANCE_ID in self._json_config else None

        # Extract properties from pipeline configuration
        self._pipeline_conf_props = self.extract_pipeline_props(pipeline_conf)

    def extract_pipeline_props(self, pipeline_conf):
        properties = {
            "ml_code": pipeline_conf.get(self.ML_CODE_PROP, None),
            "group_id": int(pipeline_conf.get(self.GROUP_ID, None)) if pipeline_conf.get(self.GROUP_ID, None) else None,
            "ep_id": str(pipeline_conf.get(self.EP_ID, None)) if pipeline_conf.get(self.EP_ID, None) else None,
            "ep_object_name": str(pipeline_conf.get(self.EP_OBJECT_NAME, None)) if pipeline_conf.get(self.EP_OBJECT_NAME, None) else None,
            "ml_model_object_name": str(pipeline_conf.get(self.ML_MODEL_OBJECT_NAME, None)) if pipeline_conf.get(self.ML_MODEL_OBJECT_NAME, None) else None,
            "ml_model_api": str(pipeline_conf.get(self.ML_MODEL_API_NAME, None)) if pipeline_conf.get(self.ML_MODEL_API_NAME, None) else None,
            "run_id": str(pipeline_conf.get(self.CURRENT_RUN_ID, None)) if pipeline_conf.get(self.CURRENT_RUN_ID, None) else None,
            "current_step_name": str(pipeline_conf.get(self.CURRENTLY_EXECUTING_STEP_NAME, None)) if pipeline_conf.get(self.CURRENTLY_EXECUTING_STEP_NAME, None) else None,
            "ml_model_versions_object": str(pipeline_conf.get(self.ML_MODEL_VERSIONS_OBJECT_NAME, None)) if pipeline_conf.get(self.ML_MODEL_VERSIONS_OBJECT_NAME, None) else None,
            "ml_model_versions_object_api": str(pipeline_conf.get(self.ML_MODEL_VERSIONS_API, None)) if pipeline_conf.get(self.ML_MODEL_VERSIONS_API, None) else None,
            "ml_model_version_metrics_object_name": str(pipeline_conf.get(self.ML_MODEL_VERSION_METRICS_OBJECT_NAME, None)) if pipeline_conf.get(self.ML_MODEL_VERSION_METRICS_OBJECT_NAME, None) else None,
            "job_code": str(pipeline_conf.get(self.JOB_CODE, None)) if pipeline_conf.get(self.JOB_CODE, None) else None,
            "ml_model_version_metrics_api": str(pipeline_conf.get(self.ML_MODEL_VERSION_METRICS_API, None)) if pipeline_conf.get(self.ML_MODEL_VERSION_METRICS_API, None) else None
        }
        return properties

    def get_tenant_data_folder(self):
        return self.tenant_data_folder

    def get_ml_model_versions_object(self):
        return self._pipeline_conf_props["ml_model_versions_object"]

    def get_ml_model_versions_api(self):
        return self._pipeline_conf_props["ml_model_versions_object_api"]

    def get_currently_executing_step_name(self):
        return self._pipeline_conf_props["current_step_name"]

    def get_ep_object_name(self):
        return self._pipeline_conf_props["ep_object_name"]

    def get_ml_model_object_name(self):
        return self._pipeline_conf_props["ml_model_object_name"]

    def get_ml_model_api(self):
        return self._pipeline_conf_props["ml_model_api"]

    def get_current_run_id(self):
        return self._pipeline_conf_props["run_id"]

    def get_ml_model_version_metrics_object_name(self):
        return self._pipeline_conf_props["ml_model_version_metrics_object_name"]

    def get_ml_model_version_metrics_api(self):
        return self._pipeline_conf_props["ml_model_version_metrics_api"]

    def get_job_code(self):
        return self._pipeline_conf_props["job_code"]

    def get_object_from_app_config(self, key):
        return self._pipeline_conf_props[key]

    def does_app_config_contain_key(self, key):
        return key in self._pipeline_conf_props

    def get_object_from_base_config(self, key):
        return self._json_config[key]

    def does_base_config_contain_key(self, key):
        return key in self._json_config

    def get_current_execution_profile_id(self):
        return self._pipeline_conf_props["ep_id"]

    def get_ml_code(self):
        return self._pipeline_conf_props["ml_code"]

    def get_currently_executing_job_id(self):
        return self._currently_executing_job_id

    def get_app_instance(self):
        return self._app_instance_id

    def get_current_group_id(self):
        return self._pipeline_conf_props["group_id"]

    def get_current_agi_id(self):
        return self._agiId

    def get_host_name(self):
        return self._host_name

    def get_session_code(self):
        return self._session_code

    def get_app_instance_session_code(self):
        if self._app_session_code is not None:
            return self._app_session_code
        parts = self._session_code.split("_")
        parts[0] = "zpsa"
        parts[-1] = self._app_instance_id
        app_instance_session_code = "_".join(parts)
        return app_instance_session_code

    def get_refresh_token(self):
        return self._token

    def get_current_app_instance_id(self):
        return self._app_instance_id

    def get_step_code(self):
        return self._step_code

    def get_operations_key(self):
        return self.operations_key

    def get_filter_id(self):
        return self._filter_id
