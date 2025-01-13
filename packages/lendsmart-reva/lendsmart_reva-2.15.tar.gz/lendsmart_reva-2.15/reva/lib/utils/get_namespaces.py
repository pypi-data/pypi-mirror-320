"""
    This module will find all the namespaces
"""
import os
from reva.lib.utils.constants import DEVELOPMENT, PRODUCTION, UAT

def get_all_namespaces(env_path: str):
    """
    This function returns all the namespaces list
    """
    all_namespace = os.listdir(env_path)
    unwanted_ns = [".md"]
    filtered_namespace = [ns for ns in all_namespace if ns[-3:] not in unwanted_ns]
    return filtered_namespace


def get_all_dev_namespaces(costumization_path: str):
    """
    This function nevigates to development directory in customization folder
    and return all development namespaces
    """
    dev_env_path = costumization_path + f"{DEVELOPMENT}/"
    all_namespaces = get_all_namespaces(dev_env_path)
    return all_namespaces

def get_all_uat_namespaces(costumization_path: str):
    """
    This function nevigates to uat directory in customization folder
    and return all uat namespaces
    """
    dev_env_path = costumization_path + f"{UAT}/"
    all_namespaces = get_all_namespaces(dev_env_path)
    return all_namespaces

def get_all_tao_namespaces(costumization_path: str):
    """
    This function will return the list of all tao namespaces
    """
    all_namespace = get_all_namespaces(costumization_path)
    dev_identifier = ["breakoutfinanceuat"]
    dev_namespace = [
        ns for ns in all_namespace if ns[-3:] in dev_identifier or ns in dev_identifier
    ]
    return dev_namespace

def get_all_apiprod_namespaces(costumization_path: str):
    """
    This function will return the list of apiprod namespaces
    """
    all_namespace = get_all_namespaces(costumization_path)
    dev_identifier = ["dev", "uat", "app", "apptest","breakoutfinance"]
    aoi_prod_namespace = [
        ns
        for ns in all_namespace
        if ns[-3:] not in dev_identifier and ns not in dev_identifier
    ]
    return aoi_prod_namespace

def get_all_prod_namespaces(costumization_path: str):
    """
    This function nevigates to production directory in customization folder
    and return all production namespaces
    """
    dev_env_path = costumization_path + f"{PRODUCTION}/"
    all_namespaces = get_all_namespaces(dev_env_path)
    return all_namespaces


def get_namespace_by_argument_and_path(args, customization_path: str):
    """
    This function will return the namespace based on the environment
    """
    # ns = rsnt
    if args.namespace == "all":
        if args.env == "dev":
            namespaces = get_all_dev_namespaces(customization_path)
        if args.env == "prod":
            namespaces = get_all_prod_namespaces(customization_path)
        if args.env == "apiprod":
            namespaces = get_all_apiprod_namespaces(customization_path)
        if args.env == "tao":
            namespaces = get_all_tao_namespaces(customization_path)
        if args.env == "uat":
            namespaces = get_all_uat_namespaces(customization_path)
    else:
        namespaces = [args.namespace]

    return namespaces
