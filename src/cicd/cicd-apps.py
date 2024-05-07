#!/usr/bin/env python
import argparse
import logging
from domino import Domino
import requests


def parse_args():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="A script to publish Domino Apps")
    parser.add_argument("DOMINO_APP_OP", type=str, help="Domino App Operation")
    parser.add_argument("DOMINO_PROJECT_OWNER", type=str, help="Domino Project Owner.")
    parser.add_argument("DOMINO_PROJECT_NAME", type=str, help="Domino Project Name.")
    parser.add_argument("DOMINO_USER_API_KEY", type=str, help="Domino user API Key.")
    parser.add_argument(
        "DOMINO_API_HOST",
        type=str,
        help="Domino URL for external or http://nucleus-frontend.domino-platform:80 from a workspace.",
    )
    parser.add_argument(
        "DOMINO_HARDWARE_TIER", type=str, help="Domino hardware tier for the app"
    )
    args = parser.parse_args()
    return args


def app_publish(domino, hardwareTierId=None):
    """
    Publish a brand new app.

    Args:
        domino (Domino): Domino object.
        hardwareTierId (str): Hardware tier ID.
    """

    response = domino.app_publish(
        unpublishRunningApps=True, hardwareTierId=hardwareTierId
    )

    if response.status_code == 200:
        logging.info(f"{response.status_code}: {response.reason}")


def app_unpublish(domino):
    """
    Unpublish app.

    Args:
        domino (Domino): Domino object.
    """
    # Unpublish app
    response = domino.app_unpublish()

    if response.status_code == 200:
        logging.info(f"{response.status_code}: {response.reason}")


def get_owner_id(domino_url, user_api_key):
    logging.info(f"Getting Owner Id for the api key {user_api_key}")
    url = f"https://{domino_url}/v4/users/self"
    headers = {"X-Domino-Api-Key": user_api_key}
    response = requests.get(url, headers=headers)
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


def main():
    """
    Main function to execute the script.
    """
    inputs = parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    logging.info(inputs.DOMINO_PROJECT_NAME)
    logging.info(inputs.DOMINO_USER_API_KEY)
    logging.info(inputs.DOMINO_API_HOST)

    project = f"{inputs.DOMINO_PROJECT_OWNER}/{inputs.DOMINO_PROJECT_NAME}"
    domino = Domino(
        project,
        api_key=inputs.DOMINO_USER_API_KEY,
        host=f"https://{inputs.DOMINO_API_HOST}",
    )

    hardware_tier_id = get_hardware_tier_id(
        inputs.DOMINO_API_HOST, inputs.DOMINO_USER_API_KEY, inputs.DOMINO_HARDWARE_TIER
    )

    if inputs.DOMINO_APP_OP == "publish":
        app_publish(domino, hardware_tier_id)
    elif inputs.DOMINO_APP_OP == "unpublish":
        app_unpublish(domino)


if __name__ == "__main__":
    main()
