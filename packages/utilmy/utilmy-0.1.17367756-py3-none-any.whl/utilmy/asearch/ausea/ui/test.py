"""
Description:
    This is to verify the test based on different html templates.
    Developers cab add files in to template/answer/<template_folder>/<test>/data_test<#number>.json
    It supports dynamic query mapping to specific JSON data files and includes support for a test mode.

Functions:
    1. read_json(fdata="ui/static/answers/com_describe/data.json"):
       - Reads and parses a JSON file into a dictionary.

    2. get_answer_test(query, meta=None):
       - Retrieves answer data based on a given query string.
       - Maps queries to subdirectories and retrieves the corresponding JSON file.
       - Supports a test mode (controlled via the environment variable `AISEARCH_ISTEST`).
       - Adds test-specific metadata fields (`userid_id`, `session_id`, `query_id`) to the returned data.

Usage:
    - If the query contains 'test', it attempts to load a version-specific file (e.g., `data_test1.json`).
    - Adds default test metadata to the returned dictionary:
        - `userid_id`: "test_userid_id"
        - `session_id`: "test_session_id"
        - `query_id`: "test_query_id"
"""

import json
import os
import time
from utilmy import log


def read_json(fdata="ui/static/answers/com_describe/data.json"):
    try:
        with open(fdata, 'r') as fi:
            json_content = fi.read()

        data_dict = json.loads(json_content)
        return data_dict

    except Exception as e:
        log(f"Unexpected error occurred: {e}")
        raise e


def get_answer_test(query, meta=None):
    istest = 1 if os.environ.get('AISEARCH_ISTEST', "0") == "1" else 0
    if istest > 0: time.sleep(2)

    base_dir = "ui/static/answers/"

    query_map = {
        "com_describe": "com_describe",
        "overview": "indus_overview",
        "search_activity": "search_activity_html",
        "report": "report_v1",
        "data_table": "table_html",
        "answer_v1": "answer_v1",
        "chart": "chart_html",
        "compare_activity": "compare_activity",
        "network": "chart_html_network"
    }

    version = None

    if 'test' in query:
        words = query.split()
        for word in words:
            if 'test' in word:
                version = word
                break

    for key, subdirectory in query_map.items():
        if key in query:
            if version:
                file_path = os.path.join(base_dir, subdirectory, f"test/data_{version}.json")
            else:
                file_path = os.path.join(base_dir, subdirectory, "data.json")
            log(file_path)
            dd = read_json(file_path)
            break
        else:
            dd = read_json()
    dd["userid_id"] = "test_userid_id"
    dd["session_id"] = "test_session_id"
    dd["query_id"] = "test_query_id"

    return dd
