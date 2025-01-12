# morph_extractor/cli.py

import logging
import json
from .config import logger
from .lang_code import unimorph_dict
from .wiktionary_loader import fetch_wiktionary_page_playwright
from .token_utils import get_num_tokens, chunk_text_by_tokens
from .morphology_extractor import (
    extract_morphology_from_wiktionary,
    generate_morphology_fallback,
    find_missing_keys,
    fetch_additional_morphology,
)
from .json_utils import (
    extract_json_from_response,
    safe_parse_json_with_retries,
    combine_json_objects
)

def main():
    word = input("Enter a word: ").strip().lower()
    part_of_speech = input("Enter part of speech (e.g., 'noun', 'verb', etc.): ").strip().lower()
    lang_code = input("Enter language code (e.g., 'hun', 'nob', etc.): ").strip().lower()

    # Validate language code
    language_name = unimorph_dict.get(lang_code)
    if not language_name:
        logger.error(f"Language code '{lang_code}' not found in unimorph_dict. Exiting.")
        return

    # Step A) Fetch Wiktionary content
    logger.info(f"Fetching Wiktionary page for '{word}'...")
    page_text = fetch_wiktionary_page_playwright(word)
    if not page_text:
        logger.warning("No Wiktionary data found or an error occurred while loading the page.")
        page_text = ""

    # Step B) Break into chunks if large
    total_tokens = get_num_tokens(page_text)
    logger.info(f"Approximate token count: {total_tokens}")
    MAX_TOKENS_PER_CHUNK = 3000

    if total_tokens > MAX_TOKENS_PER_CHUNK:
        logger.info(f"Text exceeds {MAX_TOKENS_PER_CHUNK} tokens, chunking it.")
        chunks = chunk_text_by_tokens(page_text, MAX_TOKENS_PER_CHUNK)
    else:
        chunks = [page_text]

    # Step C) Extract from Wiktionary chunks
    final_data = {}
    got_any_data = False
    for i, chunk in enumerate(chunks, start=1):
        logger.info(f"Extracting morphology from chunk {i}/{len(chunks)}...")
        raw_json_like = extract_morphology_from_wiktionary(chunk, word, part_of_speech, language_name)
        extracted_str = extract_json_from_response(raw_json_like)
        parsed = safe_parse_json_with_retries(extracted_str)

        # If we got something valid, combine
        if parsed and parsed != {} and parsed != []:
            got_any_data = True
            if isinstance(parsed, dict):
                final_data = combine_json_objects(final_data, parsed)
            elif isinstance(parsed, list):
                final_data = combine_json_objects(final_data, {"data_list": parsed})

    # Step D) If Wiktionary data is empty, do a full fallback
    if not got_any_data:
        logger.info("No morphological data from Wiktionary. Falling back to direct generation.")
        fallback_raw = generate_morphology_fallback(word, part_of_speech, language_name)
        fallback_extracted = extract_json_from_response(fallback_raw)
        final_data = safe_parse_json_with_retries(fallback_extracted)

    # Step E) Try to fill in missing top-level keys
    expected_keys = [
        "part_of_speech",
        "plural_form",
        "declension",
        "possessive_forms",
        "morphological_components",
        "gender",
        "case",
        "number"
    ]
    missing_keys = find_missing_keys(final_data, expected_keys)
    if missing_keys:
        logger.info(f"Missing keys: {missing_keys}. Querying model for additional data.")
        addition_raw = fetch_additional_morphology(word, part_of_speech, language_name, missing_keys)
        final_data = combine_json_objects(final_data, addition_raw)

    # Step F) Print final combined JSON
    logger.info("=== COMBINED JSON OUTPUT ===")
    print(json.dumps(final_data, indent=2, ensure_ascii=False))
