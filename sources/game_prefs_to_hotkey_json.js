const fs = require('fs');

function extractHotkeysFromLua(luaContent) {
    // Extract the content between UserKeyMap = { and the closing }
    const userKeyMapPattern = /UserKeyMap\s*=\s*{(.*?)}/s;
    const userKeyMapMatch = luaContent.match(userKeyMapPattern);

    if (!userKeyMapMatch) {
        return [];
    }

    const userKeyMapContent = userKeyMapMatch[1];

    // Extract key-value pairs from userKeyMapContent
    // Ignore the IDE warnings of the regex string, it seems to be correct
    const pattern = /(\[[\'"]?[\w\-\+\s]+[\'"]?\]|[\w\-]+)\s*=\s*'([^\']+)'/g;

    const matches = [...userKeyMapContent.matchAll(pattern)];

    // Convert matches to desired format
    return matches.map(match => [match[1], match[2]]);
}

const luaToJsonFormat = {
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
};

function convertLuaToJsonFormat(key) {
    for (let luaKeyPart in luaToJsonFormat) {
        while (key.includes(luaKeyPart)) {
            key = key.replace(luaKeyPart, luaToJsonFormat[luaKeyPart]);
        }
    }
    return key;
}

function convertAllKeys(hotkeysArray) {
    return hotkeysArray.map(([key, value]) => {
        const convertedKey = convertLuaToJsonFormat(key);
        return [value, [convertedKey, ""]];
    });
}

// Read the content of the .prefs file
const luaContent = fs.readFileSync('./CheeseBerry_Game.prefs', 'utf8');

// Extract hotkeys
const extractedHotkeys = extractHotkeysFromLua(luaContent);

// Convert hotkeys
const updated_hotkeys = convertAllKeys(extractedHotkeys);

const updatedHotkeysObject = {};
updated_hotkeys.forEach(([key, value]) => {
    updatedHotkeysObject[key] = value;
});

// Print results
//console.log(extractedHotkeys);
//console.log(extractedHotkeys.length);
console.log(updated_hotkeys);

const keymapName = "CheeseBerryJS"; // Replace with your desired keymap name
const yearMonthDay = "2023-10-19"; // Replace with the desired date or dynamically generate it
const outputFilename =`CheeseBerry_${yearMonthDay}_js.json`; // Replace with your desired output filename

const outputData = {
    name: keymapName,
    version: yearMonthDay,
    default_context: "Global Context",
    os: ["windows"],
    contexts: {"Global Context": updatedHotkeysObject}
};

const jsonContent = JSON.stringify(outputData, null, 4);
fs.writeFileSync(outputFilename, jsonContent);
