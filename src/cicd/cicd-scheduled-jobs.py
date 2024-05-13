#!/usr/bin/env python
import argparse
import logging
import os
import requests
from domino import Domino
from utils import read_config as read_config
from utils import parse_evn_var as parse_evn_var
from utils import parse_args as parse_args

env_variables = {}

def get_user_id(domino, username_or_email):
    userid = domino.get_user_id(username_or_email)
    return userid

def get_project_id(domino_url, project_name, owner_id, user_api_key):
    logging.info(f"Getting project id for owner id: {owner_id}")
    url = f"https://{domino_url}/v4/projects"
    params = {"name": project_name, "ownerId": owner_id}
    headers = {"X-Domino-Api-Key": user_api_key}
    response = requests.get(url, params=params, headers=headers)
    print(response)
    return response.json()


def create_scheduled_job(domino_url, project_id, user_api_key, job_details):
    url = f"https://{domino_url}/v4/projects/{project_id}/scheduledjobs"
    headers = {"X-Domino-Api-Key": user_api_key, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=job_details)
    logging.info("HTTP Status Code: %s", response.status_code)
    logging.info("Response Body: %s", response.text)
    return response.json()


def main():
    inputs = parse_args()
    parse_evn_var(env_variables, inputs.DOMINO_ENV)

    logging.info(env_variables["DOMINO_PROJECT_NAME"])
    logging.info(inputs.DOMINO_USER_API_KEY)
    logging.info(env_variables["DOMINO_API_HOST"])

    domino_url = env_variables["DOMINO_API_HOST"]
    user_api_key = inputs.DOMINO_USER_API_KEY
    project = env_variables["DOMINO_PROJECT_OWNER"] + "/" + env_variables["DOMINO_PROJECT_NAME"]
    
    domino = Domino(
        project,
        api_key=inputs.DOMINO_USER_API_KEY,
        host=f"https://{env_variables['DOMINO_API_HOST']}",
    )
    owner_id = get_user_id(domino, env_variables["DOMINO_PROJECT_OWNER"])
    project_id = get_project_id(
        domino_url, env_variables["DOMINO_PROJECT_NAME"], owner_id, user_api_key
    )
    test_id = project_id[0].get("id")

    cron_string = env_variables["DOMINO_JOB_CRON"]
    job_command = env_variables["DOMINO_JOB_COMMAND"]

    job_details = {
        "title": "scheduled Job",
        "command": job_command,
        "schedule": {
            "cronString": cron_string,
            "isCustom": True,
        },
        "timezoneId": "UTC",
        "isPaused": False,
        "allowConcurrentExecution": True,
        "hardwareTierIdentifier": env_variables["DOMINO_HARDWARE_TIER_NAME"],
        "overrideEnvironmentId": env_variables["DOMINO_ENVIRONMENT_ID"],
        "scheduledByUserId": "66151350631ba025af570cf2",
        "notifyOnCompleteEmailAddresses": ["ben.wolstenholme+test@dominodatalab.com"],
        "environmentRevisionSpec": "ActiveRevision",
    }

    response = create_scheduled_job(domino_url, test_id, user_api_key, job_details)
    print("Scheduled job created:", response)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
