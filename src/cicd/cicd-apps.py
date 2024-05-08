#!/usr/bin/env python
import argparse
import logging
import os
from domino import Domino
import requests
from utils import read_config, parse_evn_var, parse_args

env_variables = {}


def get_owner_id(domino_url, user_api_key):
    logging.info(f"Getting Owner Id for the api key {user_api_key}")
    url = f"https://{domino_url}/v4/users/self"
    headers = {"X-Domino-Api-Key": user_api_key}
    response = requests.get(url, headers=headers)
    return response.json()


def get_project_id(domino_url, project_name, user_api_key):
    owner_id = get_owner_id(domino_url, user_api_key).get("id")
    logging.info(f"Getting project id for owner id: {owner_id}")
    url = f"https://{domino_url}/v4/projects"
    params = {"name": project_name, "ownerId": owner_id}
    headers = {"X-Domino-Api-Key": user_api_key}
    response = requests.get(url, params=params, headers=headers)
    return response.json()


def get_hardware_tier_id(domino_url, user_api_key, hardware_tier_name):
    owner_id = get_owner_id(domino_url, user_api_key).get("id")
    logging.info(f"Getting hardware tier id for owner id: {owner_id}")
    url = f"https://{domino_url}/v4/hardwareTier"
    headers = {"X-Domino-Api-Key": user_api_key}
    hardware_tier_list = requests.get(url, headers=headers).json()
    tier_id = next(
        (
            tier["id"]
            for tier in hardware_tier_list.get("hardwareTiers")
            if tier["name"] == hardware_tier_name
        ),
        None,
    )
    return tier_id


def app_publish(domino, hardwareTierId=None):
    response = domino.app_publish(
        unpublishRunningApps=True, hardwareTierId=hardwareTierId
    )
    if response.status_code == 200:
        logging.info(f"{response.status_code}: {response.reason}")


def app_unpublish(domino):
    response = domino.app_unpublish()
    if response.status_code == 200:
        logging.info(f"{response.status_code}: {response.reason}")


def main():
    inputs = parse_args()
    parse_evn_var(env_variables, inputs.DOMINO_ENV)

    logging.basicConfig(level=logging.INFO)

    logging.info(env_variables["DOMINO_PROJECT_NAME"])
    logging.info(inputs.DOMINO_USER_API_KEY)
    logging.info(env_variables["DOMINO_API_HOST"])

    project = f"{env_variables['DOMINO_PROJECT_OWNER']}/{env_variables['DOMINO_PROJECT_NAME']}"
    domino = Domino(
        project,
        api_key=inputs.DOMINO_USER_API_KEY,
        host=f"https://{env_variables['DOMINO_API_HOST']}",
    )

    hardware_tier_id = get_hardware_tier_id(
        env_variables["DOMINO_API_HOST"],
        inputs.DOMINO_USER_API_KEY,
        env_variables["DOMINO_HARDWARE_TIER_NAME"],
    )

    if env_variables["DOMINO_APP_OP"] == "publish":
        app_publish(domino, hardware_tier_id)
    elif env_variables["DOMINO_APP_OP"] == "unpublish":
        app_unpublish(domino)


if __name__ == "__main__":
    main()
