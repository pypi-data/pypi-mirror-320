# morph_extractor/json_utils.py
import openai
import re
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def extract_json_from_response(text: str) -> str:
    """
    Attempt to find the FIRST '{...}' or '[...]' block in the text.
    Returns '{}' if no JSON is found.
    """
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    return match.group(0) if match else "{}"

def safe_parse_json_with_retries(json_str: str) -> Any:
    """
    Try to parse the JSON string, removing trailing chars if needed.
    Returns {} or [] if all fails.
    """
    for i in range(len(json_str), 0, -1):
        sub_str = json_str[:i]
        try:
            return json.loads(sub_str)
        except json.JSONDecodeError:
            continue
    return {}

def combine_json_objects(base: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two JSON objects, giving priority to 'base' but filling missing keys from 'new_data'.
    """
    for key, val in new_data.items():
        if key not in base:
            base[key] = val
        else:
            # If both are dict, merge recursively
            if isinstance(base[key], dict) and isinstance(val, dict):
                base[key] = combine_json_objects(base[key], val)
            # If base is a list or scalar, we keep base as is.
    return base
