from fastapi import FastAPI
from pydantic import BaseModel

# --- Pydantic Models ---
class TextInput(BaseModel):
    text: str

class TextOutput(BaseModel):
    cleaned_text: str

# --- FastAPI App Instance ---
app = FastAPI()

# --- Character Stripping Logic ---

# Rule 1: Hidden/control chars (to be removed)
# Includes: U+00AD, U+180E, U+200B–U+200F, U+202A–U+202E, U+2060–U+206F, U+FE00–U+FE0F, U+FEFF
_hidden_chars_to_remove = set([
    '\u00AD', '\u180E', '\u200B', '\u200C', '\u200D', '\u200E', '\u200F',
    '\u202A', '\u202B', '\u202C', '\u202D', '\u202E', '\u2060', '\uFEFF'
] + [chr(i) for i in range(0x2061, 0x206F + 1)]  # U+2061–U+206F (NB: range upper bound is exclusive)
  + [chr(i) for i in range(0xFE00, 0xFE0F + 1)]) # U+FE00–U+FE0F (NB: range upper bound is exclusive)

# Rule 2: Space characters -> standard space " "
# Covers: U+00A0, U+1680, U+2000–U+200A, U+202F, U+205F, U+3000
_space_map = {
    '\u00A0': ' ', '\u1680': ' ', '\u2000': ' ', '\u2001': ' ', '\u2002': ' ',
    '\u2003': ' ', '\u2004': ' ', '\u2005': ' ', '\u2006': ' ', '\u2007': ' ',
    '\u2008': ' ', '\u2009': ' ', '\u200A': ' ', '\u202F': ' ', '\u205F': ' ',
    '\u3000': ' '
}

# Rule 3: Dashes -> hyphen "-"
# Covers: U+2012–U+2015, U+2212
_dash_map = {
    '\u2012': '-', '\u2013': '-', '\u2014': '-', '\u2015': '-', '\u2212': '-'
}

# Rule 4: Quotes/Apostrophes -> standard ASCII (' and ")
# Covers: U+2018–U+201F, U+2032–U+2036, U+00AB, U+00BB
_quote_map = {
    '\u2018': "'", '\u2019': "'", '\u201A': "'", '\u201B': "'",
    '\u201C': '"', '\u201D': '"', '\u201E': '"', '\u201F': '"',
    '\u2032': "'", # Prime
    '\u2033': '"', # Double Prime
    '\u2034': '',  # Triple Prime (removed as not directly mappable to ' or ")
    '\u2035': "'", # Reversed Prime
    '\u2036': '"', # Reversed Double Prime
    '\u00AB': '"', # Left-Pointing Double Angle Quotation Mark
    '\u00BB': '"'  # Right-Pointing Double Angle Quotation Mark
}

# Rule 5: Ellipsis & Misc -> standard punctuation
# Covers: U+2026, U+2022, U+00B7
_misc_map = {
    '\u2026': '...',  # Horizontal Ellipsis
    '\u2022': '*',    # Bullet
    '\u00B7': '.'     # Middle Dot
}

def strip_non_human_chars(input_text: str) -> str:
    """
    Applies a series of rules to strip non-human characters from text.
    Preserves standard ASCII characters and common single-character emojis.
    Note: Compound emojis using ZWJ or specific variation selectors might be
    altered due to Rule 1 (removal of hidden/control chars).
    """
    processed_chars = []
    for char_val in input_text:
        # Rule 1: Hidden/control chars (remove)
        if char_val in _hidden_chars_to_remove:
            continue

        # Rule 2: Space characters
        replacement = _space_map.get(char_val)
        if replacement is not None:
            processed_chars.append(replacement)
            continue

        # Rule 3: Dashes
        replacement = _dash_map.get(char_val)
        if replacement is not None:
            processed_chars.append(replacement)
            continue

        # Rule 4: Quotes/Apostrophes
        if char_val in _quote_map:
            replacement = _quote_map[char_val]
            if replacement:  # Append only if replacement is not an empty string (e.g., for U+2034)
                processed_chars.append(replacement)
            continue

        # Rule 5: Ellipsis & Misc
        replacement = _misc_map.get(char_val)
        if replacement is not None:
            processed_chars.append(replacement)
            continue

        # Rule for Full-width punctuation (U+FF01–U+FF5E)
        char_code = ord(char_val)
        if 0xFF01 <= char_code <= 0xFF5E: # Fullwidth Forms
            processed_chars.append(chr(char_code - 0xFEE0)) # Convert to basic Latin equivalent
            continue
        
        # Rule 6: Keyboard-only Filter (Keep standard ASCII and Emojis)
        # This step filters for standard ASCII characters (0-127) or common emojis.
        # Non-ASCII characters not handled by previous rules and not in emoji ranges will be removed.
        
        if 0 <= char_code <= 127: # Standard ASCII
            processed_chars.append(char_val)
            continue

        # Check for common emoji ranges if not ASCII and not handled by other rules.
        # These are processed *after* Rule 1 might have removed ZWJ, ZWNJ, Variation Selectors.
        is_emoji = False
        # Emoticons (U+1F600–U+1F64F)
        if 0x1F600 <= char_code <= 0x1F64F: is_emoji = True
        # Miscellaneous Symbols and Pictographs (U+1F300–U+1F5FF)
        elif 0x1F300 <= char_code <= 0x1F5FF: is_emoji = True
        # Transport and Map Symbols (U+1F680–U+1F6FF)
        elif 0x1F680 <= char_code <= 0x1F6FF: is_emoji = True
        # Supplemental Symbols and Pictographs (U+1F900–U+1F9FF)
        elif 0x1F900 <= char_code <= 0x1F9FF: is_emoji = True
        # Dingbats (U+2700–U+27BF) - e.g., ✔️ ✨ ☀️ ☎️ ❤
        elif 0x2700 <= char_code <= 0x27BF: is_emoji = True
        # Symbols and Pictographs Extended-A (U+1FA70–U+1FAFF)
        elif 0x1FA70 <= char_code <= 0x1FAFF: is_emoji = True
        # Regional Indicator Symbols (U+1F1E6-U+1F1FF) - for flags
        elif 0x1F1E6 <= char_code <= 0x1F1FF: is_emoji = True
        # Miscellaneous Symbols (U+2600–U+26FF) - e.g., ☀ ☁ ☂ ☃ ★ ☆ ☹ ☺
        elif 0x2600 <= char_code <= 0x26FF: is_emoji = True

        if is_emoji:
            processed_chars.append(char_val)
        # Else: character is non-ASCII, not an emoji from the defined ranges, 
        # and not covered by specific transformation, so it's dropped.

    return "".join(processed_chars)

# --- FastAPI Endpoint ---
@app.post("/", response_model=TextOutput)
async def strip_content_endpoint(payload: TextInput):
    """
    Receives text and strips it of common non-human-generated characters.

    Transformations include:
    - Removing hidden/control characters (affects ZWJ, Variation Selectors for emojis).
    - Normalizing various Unicode space types to standard ASCII spaces.
    - Normalizing dashes, quotes, and apostrophes to ASCII equivalents.
    - Converting ellipsis, bullets to standard ASCII punctuation.
    - Normalizing full-width CJK punctuation to ASCII equivalents.
    - Filtering out remaining non-ASCII characters, while preserving common single-character emojis.
      (Note: Complex emojis might be simplified due to removal of ZWJ/Variation Selectors).
    """
    cleaned_text = strip_non_human_chars(payload.text)
    return TextOutput(cleaned_text=cleaned_text)

# Optional: A small section for local testing when running the script directly
if __name__ == "__main__":
    import uvicorn

    test_cases = [
        ("Hello\u200BWorld", "HelloWorld"),
        ("Text with\u00A0nbsp", "Text with nbsp"),
        ("Em—dash", "Em-dash"), # \u2014
        ("‘Smart’ quotes", "'Smart' quotes"), # \u2018, \u2019
        ("Ellipsis…", "Ellipsis..."), # \u2026
        ("Ｈｅｌｌｏ", "Hello"), # \uFF28 \uFF45 \uFF4C \uFF4C \uFF4F
        ("Text with soft\u00ADhyphen", "Text with softhyphen"),
        ("dollar $ and euro € symbol", "dollar $ and euro  symbol"), # Euro € (U+20AC) removed
        ("smile 😊 face", "smile 😊 face"), # Emoji 😊 (U+1F60A) kept
        ("test\uFEFFwith\u2060bom", "testwithbom"),
        ("Dashes: \u2012 \u2013 \u2014 \u2015 \u2212", "Dashes: - - - - -"),
        ("Spaces: \u00A0|\u1680|\u2000|\u3000", "Spaces:  | | | "),
        ("Misc: \u2022 \u00B7", "Misc: * ."),
        ("Control: \u200C and \u200D", "Control:  and "), # ZWJ/ZWNJ removed
        ("Variation: text\u2764\uFE0Femoji", "Variation: text❤emoji"), # U+2764 kept, U+FE0F removed
        ("Fullwidth: \uFF01\uFF03\uFF21\uFF41", "Fullwidth: !#Aa"),
        ("Copyright © symbol", "Copyright  symbol"), # Copyright © (U+00A9) removed
        ("Triple prime \u2034 test", "Triple prime  test"), # U+2034 removed
        ("Angled quotes: \u00ABtext\u00BB", 'Angled quotes: "text"'),
        ("Family emoji: 👨\u200D👩\u200D👧\u200D👦", "Family emoji: 👨👩👧👦"), # ZWJ removed, individual emojis kept
        ("Flag: 🇺🇸", "Flag: 🇺🇸") # Regional indicators U+1F1FA U+1F1F8 kept
    ]

    print("Running test cases for strip_non_human_chars:")
    all_passed = True
    for i, (original_raw, expected) in enumerate(test_cases):
        # Need to decode unicode escapes in test case strings
        original = original_raw.encode('latin-1', 'backslashreplace').decode('unicode-escape')
        actual = strip_non_human_chars(original)
        status = "PASSED" if actual == expected else "FAILED"
        if status == "FAILED":
            all_passed = False
        print(f"Test {i+1}: {original_raw[:30]}... -> {status}")
        if status == "FAILED":
            print(f"  Original: '{original}' (raw: '{original_raw}')")
            print(f"  Expected: '{expected}'")
            print(f"  Actual  : '{actual}'")
            # print(f"  Expected (ords): {[ord(c) for c in expected]}")
            # print(f"  Actual   (ords): {[ord(c) for c in actual]}")


    if all_passed:
        print("\nAll internal test cases PASSED.")
    else:
        print("\nSome internal test cases FAILED.")

    print("\nTo run the FastAPI server, use: uvicorn app:app --reload")
    print("Example POST request to / with curl:")
    print("curl -X POST -H \"Content-Type: application/json\" -d '{\"text\": \"Ｈｅｌｌｏ—‘world’…\"}' http://127.0.0.1:8000/strip_content/")
    
    # To actually run the app if script is executed:
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    # Commented out to prevent accidental server start during automated script execution by a tool.
    # If you want to run it directly, uncomment the line above and ensure uvicorn is installed.
