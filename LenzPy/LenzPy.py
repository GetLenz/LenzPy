import random
from time import perf_counter_ns as pc
import requests
import os

def _flatten_obj(obj):
    flattened = {}
    def recursive(item, prefix):
        if isinstance(item, dict):
            for key in item:
                recursive(item[key], prefix + key + '_')
        elif isinstance(item, (list, tuple)):
            for i in range(len(item)):
                recursive(item[i], prefix + str(i) + '_')
        else:
            flattened[prefix[:-1]] = item
    recursive(obj, "")
    return flattened

def _handle_args_or_res(obj, should_flatten, included):
    if should_flatten:
        obj = _flatten_obj(obj)
    if included:
        obj = {i: obj[i] for i in obj if i in included}
    return obj

def _prepare_body(args, ret, elapsed_nano):
    args = {("arg_" + i): args[i] for i in args}
    if isinstance(ret, dict):
        ret = {("return_" + i): ret[i] for i in ret}
    else:
        ret = {"return": ret}
    combined_dict = {"elapsed_ms": elapsed_nano / 1_000_000}
    combined_dict.update(args)
    combined_dict.update(ret)
    return combined_dict

def submit_report(event_name, body, api_key=None):
    """
    Submits a report to Lenz.

    Args:
        event_name (str): The name of the event or report.
        body (dict): The body of the report containing relevant data.
        api_key (str, optional): The API key for authentication. If not provided, it's fetched from the environment variable.

    Returns:
        dict: A dictionary containing the response from the API or an error message in case of failure.
    """
    url = "https://api.getle.nz/report-api"
    if not api_key:
        api_key = os.getenv("LENZ_API_KEY")
    if not api_key:
        raise ValueError("API key is missing. Please provide an API key.")

    
    data = {
        "api_key": api_key,
        "name": event_name,
        "body": body
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def instrument(report_name, api_key=None, flatten_args=False, included_args=None, flatten_res=False, included_res=None, mock=False):
    """
    Decorator for instrumenting functions with Lenz reporting.

    Args:
        report_name (str): The name of the report or event.
        api_key (str, optional): The API key for authentication. If not provided, it's fetched from the environment variable.
        flatten_args (bool, optional): Whether to flatten function arguments before reporting.
        included_args (list or None, optional): List of keys to be included in the reported arguments. If not provided, no filtering is performed.
        flatten_res (bool, optional): Whether to flatten the return value before reporting.
        included_res (list or None, optional): List of keys to be included in the reported return value. If not provided, no filtering is performed.
        mock (bool, optional): Whether to print the prepared report without actually submitting it.

    Returns:
        function: The decorated function.

    Usage:
        @instrument(report_name="lambda_invoke")
        def handler(evt, ctx):
            ...
    """
    def get_wrapper(func):
        def wrapper_lenz(*args, **kwargs):
            args_dict = {f"{i}": args[i] for i in range(len(args))}
            args_dict.update(kwargs)
            args_dict = _handle_args_or_res(args_dict, flatten_args, included_args)

            start_time = pc()
            ret = func(*args, **kwargs)
            end_time = pc()
            
            handled_ret = _handle_args_or_res(ret, flatten_res, included_res)

            if mock:
                print("Event:", report_name, "Body:", _prepare_body(args_dict, handled_ret, end_time - start_time))
            else:
                submit_report(report_name, _prepare_body(args_dict, handled_ret, end_time - start_time), api_key)

            return ret
        return wrapper_lenz
    return get_wrapper