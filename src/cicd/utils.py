import configparser
import os
import argparse


def parse_args():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="A script to publish Domino Apps")
    parser.add_argument("DOMINO_ENV", type=str, help="Domino Environment")
    parser.add_argument("DOMINO_USER_API_KEY", type=str, help="Domino user API Key.")

    args = parser.parse_args()
    return args


def read_config(section, key):
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = dir_path + "/" + "env-variables.ini"
    config.read(filepath)
    return config[section][key]


def parse_evn_var(env_variables, section):

    env_variables["DOMINO_PROJECT_OWNER"] = read_config(section, "domino_project_owner")
    env_variables["DOMINO_PROJECT_NAME"] = read_config(section, "domino_project_name")
    env_variables["DOMINO_API_HOST"] = read_config(section, "domino_api_host")
    env_variables["DOMINO_MODEL_OP"] = read_config(section, "domino_model_op")
    env_variables["DOMINO_MODEL_NAME"] = read_config(section, "domino_model_name")
    env_variables["DOMINO_MODEL_DESC"] = read_config(section, "domino_model_desc")
    env_variables["DOMINO_MODEL_FILE"] = read_config(section, "domino_model_file")
    env_variables["DOMINO_MODEL_FUNC"] = read_config(section, "domino_model_func")
    env_variables["DOMINO_MODEL_CE"] = read_config(section, "domino_model_ce")
    env_variables["DOMINO_HARDWARE_TIER_NAME"] = read_config(
        section, "domino_hardware_tier"
    )
    env_variables["DOMINO_ENVIRONMENT_ID"] = read_config(
        section, "domino_environment_id"
    )
    env_variables["DOMINO_REGISTERED_MODEL_NAME"] = read_config(
        section, "domino_registered_model_name"
    )
    env_variables["DOMINO_REGISTERED_MODEL_VERSION"] = read_config(
        section, "domino_registered_model_version"
    )
    env_variables["DOMINO_MODEL_TYPE"] = read_config(section, "domino_model_type")
    env_variables["DOMINO_TARGET_STAGE"] = read_config(section, "domino_target_stage")
    env_variables["DOMINO_REVIEWER"] = read_config(section, "domino_reviewer")

    env_variables["DOMINO_JOB_OP"] = read_config(section, "domino_job_op")
    env_variables["DOMINO_JOB_COMMAND"] = read_config(section, "domino_job_command")
    env_variables["DOMINO_JOB_ID"] = read_config(section, "domino_job_id")
    env_variables["DOMINO_JOB_COMMIT_ID"] = read_config(section, "domino_job_commit_id")
    env_variables["DOMINO_JOB_ENVIRONMENT_ID"] = read_config(
        section, "domino_job_environment_id"
    )
    env_variables["DOMINO_JOB_HARDWARE_TIER_NAME"] = read_config(
        section, "domino_job_hardware_tier_name"
    )

    env_variables["DOMINO_APP_OP"] = read_config(section, "domino_app_op")

    return env_variables
