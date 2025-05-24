import json

def manual_json_extraction(response_content):

    try:
        start_index = response_content.find('{')
        end_index = response_content.rfind('}')
        if start_index != -1 and end_index != -1 and start_index < end_index:
            json_string = response_content[start_index:end_index + 1]
            return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Manual JSON extraction failed: {e}")

    return {}

