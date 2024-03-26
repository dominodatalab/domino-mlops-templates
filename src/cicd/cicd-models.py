#!/usr/bin/env python
import argparse, os
import logging
from domino import Domino
import requests


def parse_args():
    parser = argparse.ArgumentParser(description="a script to publish Domino Models")
    parser.add_argument("DOMINO_MODEL_OP", type=str, help="create, list or update.")
    parser.add_argument("DOMINO_PROJECT_OWNER", type=str, help="Domino Project Owner.")
    parser.add_argument("DOMINO_PROJECT_NAME", type=str, help="Domino Project Name.")
    parser.add_argument("DOMINO_USER_API_KEY", type=str, help="Domino user API Key.")
    parser.add_argument(
        "DOMINO_API_HOST",
        type=str,
        help="Domino URL for external or http://nucleus-frontend.domino-platform:80 from a workspace.",
    )
    parser.add_argument("DOMINO_MODEL_NAME", type=str, help="Name of the model.")
    parser.add_argument("DOMINO_MODEL_DESC", type=str, help="Description of the model.")
    parser.add_argument("DOMINO_MODEL_FILE", type=str, help="Name of the model file.")
    parser.add_argument(
        "DOMINO_MODEL_FUNC", type=str, help="Name of the model function."
    )
    parser.add_argument(
        "DOMINO_MODEL_CE", type=str, help="ID of the model compute environment."
    )
    parser.add_argument(
        "DOMINO_HARDWARE_TIER_NAME", type=str, help="Name of the hardware tier."
    )
    parser.add_argument(
        "DOMINO_ENVIRONMENT_ID", type=str, help="ID of the model  environment id."
    )
    args = parser.parse_args()
    return args


def list_environments(domino):
    all_available_environments = domino.environments_list()
    global_environments = list(
        filter(
            lambda x: x.get("visibility") == "Global",
            all_available_environments["data"],
        )
    )
    print(
        "This Domino deployment has \
         {} global environments".format(
            len(global_environments)
        )
    )


def list_models(domino):
    logging.info(f"{domino.models_list()}")


def model_exist(domino, model_name):
    models = domino.models_list()
    for i in models["data"]:
        if i["name"] == model_name:
            return True


def get_owner_id(domino_url, user_api_key):
    logging.info(f"Getting Owner Id for the api key {user_api_key}")
    url = f"https://{domino_url}/v4/users/self"
    headers = {"Authorization": f"Bearer {user_api_key}"}
    response = requests.get(url, headers=headers)
    return response.json()


def get_project_id(domino_url, project_name, user_api_key):
    owner_id = get_owner_id(domino_url, user_api_key).get("id")
    logging.info(f"Getting project id for owner id: {owner_id}")
    url = f"https://{domino_url}/v4/projects"
    params = {"name": project_name, "ownerId": owner_id}
    headers = {"Authorization": f"Bearer {user_api_key}"}
    response = requests.get(url, params=params, headers=headers)
    return response.json()


def get_hardware_tier_id(domino_url, user_api_key, hardware_tier_name):
    owner_id = get_owner_id(domino_url, user_api_key).get("id")
    logging.info(f"Getting hardware tier id for owner id: {owner_id}")
    url = f"https://{domino_url}/v4/hardwareTier"
    headers = {"Authorization": f"Bearer {user_api_key}"}
    hardware_tier_list = requests.get(url, headers=headers).json()
    tier_id = next(
        (
            tier["id"]
            for tier in hardware_tier_list
            if tier["name"] == hardware_tier_name
        ),
        None,
    )
    return tier_id


def model_start(
    start_job_url,
    user_api_key,
    project_id,
    model_name,
    model_desc,
    model_file,
    model_func,
    hardware_tier_name,
    isAsync=False,
):
    payload = {
        "projectId": project_id,
        "name": model_name,
        "description": model_desc,
        "file": model_file,
        "function": model_func,
        "hardwareTierId": get_hardware_tier_id(hardware_tier_name),
        "isAsync": isAsync,
    }

    headers = {"Authorization": f"Bearer {user_api_key}"}
    response = requests.post(start_job_url, headers=headers, json=payload)
    print(response.text)


def create_model(domino, model_name, model_desc, model_file, model_func, model_ce):
    # Publish a brand new model
    published_model = domino.model_publish(
        file=model_file,
        function=model_func,
        environment_id=model_ce,
        name=model_name,
        description=model_desc,
    )
    published_model_id = published_model.get("data", {}).get("_id")
    logging.info("Model {} published, details below:".format(published_model_id))
    logging.info(published_model)


def publish_revision(domino, model_name, model_desc, model_file, model_func, model_ce):
    models = domino.models_list()
    for i in models["data"]:
        if i["name"] == model_name:
            published_model_id = i["id"]
    another_model_version = domino.model_version_publish(
        model_id=published_model_id,
        file=model_file,
        function=model_func,
        environment_id=model_ce,
        description=model_desc,
    )


def main():
    inputs = parse_args()
    logging.info(inputs.DOMINO_MODEL_NAME)

    start_model_url = f"https://{inputs.DOMINO_API_HOST}/v1/models"
    domino_url = inputs.DOMINO_API_HOST
    project = inputs.DOMINO_PROJECT_OWNER + "/" + inputs.DOMINO_PROJECT_NAME
    user_api_key = inputs.DOMINO_USER_API_KEY
    
    project_id = get_project_id(domino_url, project, user_api_key)

    
    domino = Domino(
        project,
        api_key=inputs.DOMINO_USER_API_KEY,
        host=inputs.DOMINO_API_HOST,
    )

    if inputs.DOMINO_MODEL_OP == "list":
        list_models(domino)
    elif inputs.DOMINO_MODEL_OP == "create":
        model_start(
            start_model_url,
            project_id,
            inputs.DOMINO_MODEL_NAME,
            inputs.DOMINO_MODEL_DESC,
            inputs.DOMINO_MODEL_FILE,
            inputs.DOMINO_MODEL_FUNC,
            inputs.DOMINO_MODEL_CE,
            inputs.DOMINO_HARDWARE_TIER_NAME,
            inputs.DOMINO_ENVIRONMENT_ID,
            inputs.DOMINO_USER_API_KEY,
        )
    elif inputs.DOMINO_MODEL_OP == "update":
        publish_revision(
            domino,
            inputs.DOMINO_MODEL_NAME,
            inputs.DOMINO_MODEL_DESC,
            inputs.DOMINO_MODEL_FILE,
            inputs.DOMINO_MODEL_FUNC,
            inputs.DOMINO_MODEL_CE,
        )
    elif inputs.DOMINO_MODEL_OP == "publish":
        if model_exist(domino, inputs.DOMINO_MODEL_NAME):
            publish_revision(
                domino,
                inputs.DOMINO_MODEL_NAME,
                inputs.DOMINO_MODEL_DESC,
                inputs.DOMINO_MODEL_FILE,
                inputs.DOMINO_MODEL_FUNC,
                inputs.DOMINO_MODEL_CE,
            )
        else:
            create_model(
                domino,
                inputs.DOMINO_MODEL_NAME,
                inputs.DOMINO_MODEL_DESC,
                inputs.DOMINO_MODEL_FILE,
                inputs.DOMINO_MODEL_FUNC,
                inputs.DOMINO_MODEL_CE,
            )


if __name__ == "__main__":
    main()
