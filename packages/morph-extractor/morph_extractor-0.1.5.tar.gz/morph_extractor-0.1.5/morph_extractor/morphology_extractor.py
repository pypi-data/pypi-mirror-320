# morph_extractor/morphology_extractor.py

import logging
from typing import Any, Dict, List

from tenacity import retry, wait_random_exponential, stop_after_attempt

from .config import client, logger
from .json_utils import extract_json_from_response, safe_parse_json_with_retries, combine_json_objects

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def extract_morphology_from_wiktionary(content: str, word: str, pos: str, lang_name: str) -> str:
    """
    Uses 'Meta-Llama-3.3-70B-Instruct' to parse the chunk content for morphological data.
    Returns raw JSON-like text or an empty string if nothing found.
    """
    prompt_text = f"""
You are a linguistics expert. Extract morphological details for the word "{word}"
(part of speech: "{pos}") from the text below, focusing ONLY on the language "{lang_name}". 

Return the information as valid JSON (object or array). 
If nothing is found, return an empty JSON object: {{}}.

Content:
{content}
"""
    try:
        response = openai.ChatCompletion.create(
            model="Meta-Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text},
            ],
            temperature=0.1,
            top_p=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Extraction from Wiktionary failed: {e}")
        return ""

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_morphology_fallback(word: str, pos: str, lang_name: str) -> str:
    """
    If Wiktionary yields no data, generate morphological details from the model alone.
    Returns JSON or empty string if unknown.
    """
    prompt_text = f"""
You are a linguistics expert. The user found no morphological data for the word "{word}"
(part of speech: "{pos}") in language "{lang_name}" from Wiktionary.

Generate morphological details from your knowledge. Return it as valid JSON.
If nothing is known, return an empty JSON object: {{}}
"""
    try:
        response = openai.ChatCompletion.create(
            model="Meta-Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text},
            ],
            temperature=0.3,
            top_p=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Fallback generation failed: {e}")
        return ""

def find_missing_keys(data: Dict[str, Any], all_keys: List[str]) -> List[str]:
    """
    Return a list of top-level keys that are missing or empty in 'data'.
    """
    missing = []
    for k in all_keys:
        if k not in data or not data[k]:
            missing.append(k)
    return missing

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def fetch_additional_morphology(word: str, pos: str, lang_name: str, keys_needed: List[str]) -> Dict[str, Any]:
    """
    Queries the model for the specified missing morphological keys.
    """
    if not keys_needed:
        return {}

    prompt_text = f"""
You are a linguistics expert. We have partial morphological data for the word "{word}"
(part of speech: "{pos}") in language "{lang_name}".

We still need the following missing morphological keys:
{', '.join(keys_needed)}

Return them as valid JSON. If not found, return an empty JSON object.
"""

    try:
        response = openai.ChatCompletion.create(
            model="Meta-Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text},
            ],
            temperature=0.3,
            top_p=0.3
        )
        raw_output = response.choices[0].message.content
        extracted = extract_json_from_response(raw_output)
        return safe_parse_json_with_retries(extracted)
    except Exception as e:
        logger.error(f"Error fetching additional morphology: {e}")
        return {}
