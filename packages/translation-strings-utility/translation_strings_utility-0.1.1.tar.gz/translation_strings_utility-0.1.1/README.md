# 1. Load and Sort Message JSONs
- Load all JSON files from ./messages/*.json
- Sort them recursively at every level
- Write back sorted JSONs

# 2. Flatten All Language Messages
- Create flatten_messages() function for dot notation
- Load all language JSONs into messages dict
- Flatten each language's messages into keys_{lang} dicts

# 3. Create Union and Find Differences
- Create union set of all keys (all_keys)
- Find missing keys for each language (missing_by_lang)

# 4. Create Master Translation Dictionary
- Build master_translations with all keys and available translations
- Mark missing translations with '[MISSING]'
- Sort master_translations by key

# 5. Get Missing Translations from Claude
- Set up Claude API client
- Process translations in batches
- Update master_translations with responses

# 6. Create Individual Language Files
- Create flattened files for each language
- Unflatten back to nested structure
- Write updated JSONs

