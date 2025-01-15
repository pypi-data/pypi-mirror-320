import json
import logging
import re

logger = logging.getLogger(__name__)


def safe_decode_json(input_str):
    """Safely decodes a string that may or may not be JSON."""
    try:
        # Try to decode the whole string as JSON
        decoded_json = json.loads(input_str)
        return decoded_json
    except json.JSONDecodeError:
        # If that fails, look for a JSON part in the string
        json_found = re.search(r"```json(.*)```", input_str, re.DOTALL)
        if json_found is None:
            json_found = re.search(r"```(.*)```", input_str, re.DOTALL)

        if json_found is not None:
            json_part = json_found.group(1)
            if json_part != "":
                try:
                    decoded_json = json.loads(json_part)
                    return decoded_json
                except json.JSONDecodeError:
                    raise Exception("Error: JSON part found but not in valid JSON format")
        else:
            raise Exception("Error: No JSON part found")
