
import re
import json
import sys
from datetime import datetime


def extract_hotkeys_from_lua(lua_content):
    user_key_map_pattern = r'UserKeyMap\s*=\s*{(.*?)}'
    user_key_map_content = re.search(user_key_map_pattern, lua_content, re.DOTALL).group(1)
    pattern = r'(\[[\'"]?[\w\-\+\s]+[\'"]?\]|[\w\-]+)\s*=\s*\'([^\']+)\''
    return re.findall(pattern, user_key_map_content)


lua_to_json_format = {
    "[": "",
    "]": "",
    "'": "",
    "\"": "",
    "-": " + ",
    "LeftBracket": "[",
    "RightBracket": "]",
    "Equals": "=",
    "NumStar": "*",
    "Quote": "'",
    "NumSlash": "/",
    "Slash": "/",
    "Tilde": "`",
    "Backslash": "\\",
    "Semicolon": ";",
    "Period": "."
}


def convert_lua_to_json_format(key, format):
    for lua_key_part, json_key_part in format.items():
        key = key.replace(lua_key_part, json_key_part)
    return key


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def main():
    year_month_day = datetime.now().strftime('%Y-%m-%d')
    game_prefs_filepath = sys.argv[1]
    keymap_name = replace_all(
        game_prefs_filepath,
        {"_Game": "",
         ".prefs": "",
         ".": "",
         "\\": ""
         }
    )
    output_filename = keymap_name + "_" + year_month_day + ".json"

    # Extract hotkeys from the .prefs file and print them
    with open(game_prefs_filepath, 'r') as f:
        prefs_content = f.read()
    extracted_hotkeys = extract_hotkeys_from_lua(prefs_content)

    # print("Extracted Hotkeys:")
    # for hotkey in extracted_hotkeys:
    #     print(hotkey)

    # Translate lua to json hotkey format and print the updated list
    updated_hotkeys = {}
    for key, action in extracted_hotkeys:
        key = convert_lua_to_json_format(key, lua_to_json_format)
        updated_hotkeys[action] = [key, ""]

    # print("\nUpdated Hotkeys:")
    # for action, keys in updated_hotkeys.items():
    #     print(f"{action} -> {keys[0]}")

    # Insert the updated hotkeys into the JSON structure and print the resulting JSON
    output_data = {
        "name": keymap_name,
        "version": year_month_day,
        "default_context": "Global Context",
        "os": [
            "windows"
        ],
        "contexts": {"Global Context": updated_hotkeys}}

    with open(output_filename, "w") as out_file:
        json.dump(output_data, out_file, indent=4)

    print(f"JSON data saved to {output_filename}")


if __name__ == "__main__":
    main()
