import json
import glob
from pathlib import Path
import anthropic
from time import sleep

def sort_nested(obj):
    if isinstance(obj, dict):
        return {k: sort_nested(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return [sort_nested(x) for x in obj]
    return obj

def flatten_messages(obj, prefix='', result=None):
    if result is None:
        result = {}
    
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            new_prefix = f"{prefix}{i}." if prefix else f"{i}."
            flatten_messages(item, new_prefix, result)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            new_prefix = f"{prefix}{key}." if prefix else f"{key}."
            flatten_messages(value, new_prefix, result)
    else:
        result[prefix.rstrip('.')] = obj
    
    return result

def unflatten_messages(flat_dict):
    result = {}
    for key, value in flat_dict.items():
        parts = key.split('.')
        current = result
        for part in parts[:-1]:
            if part.isdigit():
                part = int(part)
                # Ensure we have a list of sufficient length
                if isinstance(current, dict):
                    current = current.setdefault(part, {})
                else:
                    while len(current) <= part:
                        current.append({})
                    current = current[part]
            else:
                current = current.setdefault(part, {})
        last = parts[-1]
        if last.isdigit():
            last = int(last)
        current[last] = value
    return result

def get_translations_from_claude(prompt):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=8192,
            temperature=0,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

def process_llm_response(response_text):
    try:
        json_str = response_text[response_text.find('{'):response_text.rindex('}')+1]
        translations = json.loads(json_str)
        
        for key, lang_dict in translations.items():
            if key in master_translations:
                for lang, translation in lang_dict.items():
                    if translation != '[MISSING]':
                        master_translations[key][lang] = translation
                        print(f"Updated translation for {key} [{lang}]")
    except Exception as e:
        print(f"Error processing response: {e}")

def main():
    # 1. Sort all message files
    print("Sorting message files...")
    for filepath in glob.glob('./messages/*.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sorted_data = sort_nested(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)
            f.write('\n')
    
    # 2. Load and flatten messages
    print("Loading and flattening messages...")
    messages = {}
    languages = []
    for filepath in glob.glob('./messages/*.json'):
        lang = Path(filepath).stem
        languages.append(lang)
        with open(filepath, 'r', encoding='utf-8') as f:
            messages[lang] = json.load(f)
    
    # Create flattened versions
    for lang in languages:
        globals()[f'keys_{lang}'] = flatten_messages(messages[lang])
    
    # 3. Create union and find differences
    print("Finding differences...")
    all_keys = set()
    for lang in languages:
        all_keys.update(globals()[f'keys_{lang}'].keys())
    
    missing_by_lang = {}
    for lang in languages:
        lang_keys = set(globals()[f'keys_{lang}'].keys())
        missing_keys = all_keys - lang_keys
        if missing_keys:
            missing_by_lang[lang] = sorted(missing_keys)
    
    # 4. Create master translations
    print("Creating master translations...")
    master_translations = {}
    for key in all_keys:
        translations = {}
        for lang in languages:
            lang_dict = globals()[f'keys_{lang}']
            translations[lang] = lang_dict[key] if key in lang_dict else '[MISSING]'
        master_translations[key] = translations
    
    # 5. Get missing translations
    print("Getting missing translations...")
    def process_translations_in_batches(batch_size=5):
        incomplete_entries = {
            key: translations 
            for key, translations in master_translations.items()
            if '[MISSING]' in translations.values()
        }
        
        keys = list(incomplete_entries.keys())
        for i in range(0, len(keys), batch_size):
            batch_keys = keys[i:i+batch_size]
            batch_entries = {k: incomplete_entries[k] for k in batch_keys}
            
            prompt = "Please complete these translations:\n\nIncomplete:\n"
            prompt += json.dumps(batch_entries, indent=4, ensure_ascii=False)
            prompt += "\n\nPlease write the corrected output in json format. Format your output exactly as the input has been formatted."
            
            response = get_translations_from_claude(prompt)
            if response:
                process_llm_response(response)
            
            sleep(1)
    
    process_translations_in_batches()
    
    # 6. Create updated language files
    print("Creating updated language files...")
    for lang in languages:
        # Create flattened version for this language
        lang_translations = {
            key: translations[lang] 
            for key, translations in master_translations.items()
            if translations[lang] != '[MISSING]'
        }
        
        # Unflatten
        nested_translations = unflatten_messages(lang_translations)
        
        # Write to file
        output_path = f'./messages/{lang}.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(nested_translations, f, ensure_ascii=False, indent=2)
            f.write('\n')
    
    print("Process completed!")

if __name__ == "__main__":
    main()
