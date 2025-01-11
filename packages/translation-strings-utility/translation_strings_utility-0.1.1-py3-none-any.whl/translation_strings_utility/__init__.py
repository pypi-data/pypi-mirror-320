#!/usr/bin/env python

import os
import json
import glob
from pathlib import Path
from time import sleep
from typing import Optional, Dict, Any

import typer
import anthropic  # pip install anthropic

################################################################################
#                                  CONFIG                                      #
################################################################################

app = typer.Typer(help="CLI tool to unify translations across multiple JSON files.")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # or "sk-ant-xxx"

################################################################################
#                                HELPERS                                       #
################################################################################

def sort_nested(obj: Any) -> Any:
    """
    Recursively sort dictionary keys (and list items if needed).
    """
    if isinstance(obj, dict):
        return {k: sort_nested(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return [sort_nested(item) for item in obj]
    else:
        return obj


def flatten(obj: Any, prefix: str = '', result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Flatten a nested dict or list into dot-notation dict.
    Example:
        { "a": { "b": "val" }} => { "a.b": "val" }
    Lists become zero-based keys, e.g. a.0.something
    """
    if result is None:
        result = {}

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            flatten(v, new_key, result)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{prefix}.{i}" if prefix else str(i)
            flatten(v, new_key, result)
    else:
        result[prefix] = obj

    return result


def unflatten(flat_dict: Dict[str, Any]) -> Any:
    """
    Unflatten a dot-notation dict back into nested dicts/lists.
    Example:
      { "a.b": "val" } => { "a": { "b": "val" } }
    """
    nested = {}

    for flat_key, value in flat_dict.items():
        parts = flat_key.split('.')
        current = nested
        for idx, part in enumerate(parts):
            # Are we at the last part?
            if idx == len(parts) - 1:
                # Final assignment
                if part.isdigit():
                    # part is index in a list
                    part_int = int(part)
                    if isinstance(current, list):
                        while len(current) <= part_int:
                            current.append(None)
                        current[part_int] = value
                    else:
                        # If it's a dict or something else, we have a conflict
                        raise ValueError(
                            f"Cannot unflatten: detected list index where a dict was in use. Key={flat_key}"
                        )
                else:
                    current[part] = value
            else:
                # Not the last part, so we go deeper
                if part.isdigit():
                    part_int = int(part)
                    if not isinstance(current, list):
                        # If it's empty, we might convert it, but let's keep it simple
                        raise ValueError(
                            f"Cannot unflatten: mixing object and list structures at key={flat_key}."
                        )
                    while len(current) <= part_int:
                        current.append({})
                    current = current[part_int]
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

    return nested


def _load_json(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def _write_json(filepath: str, data: Any) -> None:
    """
    Sort keys, then write with indentation and no ASCII escaping.
    """
    sorted_data = sort_nested(data)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
        f.write('\n')


################################################################################
#                               CLAUDE CALL                                    #
################################################################################

def _call_claude_api(prompt: str) -> Optional[str]:
    """
    Real call to Anthropic Claude using the `anthropic` Python client.
    Adjust the model and parameters to your preference.
    """
    if not ANTHROPIC_API_KEY:
        typer.echo("Error: ANTHROPIC_API_KEY not set.")
        return None

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        # The messages API is used for the latest versions of the Anthropic client.
        # Each message is a dict with "role" and "content".
        # content expects a list of dicts for 'text' chunks:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # example model name from your snippet
            max_tokens=8192,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        # message.content is typically a list of text blocks
        # we can combine them into a single string
        response_text = "".join(block.get("text", "") for block in message.content)
        return response_text
    except Exception as e:
        typer.echo(f"Error calling Claude API: {e}")
        return None


################################################################################
#                                 MAIN LOGIC                                   #
################################################################################

@app.command()
def unify(
    messages_path: str = typer.Option(
        "./messages", help="Path to folder containing <lang>.json files."
    ),
    batch_size: int = typer.Option(
        5, help="Batch size for missing translation requests."
    ),
    skip_llm: bool = typer.Option(
        False, help="Skip calling Claude for missing translations."
    ),
):
    """
    Unify translation JSONs:
    1) Load & flatten each language file.
    2) Find missing keys per language.
    3) Build a master dict of translations (keys vs. {lang: translation}).
    4) If not skipped, call Claude to fill in missing translations.
    5) Unflatten & write updated JSON files.
    """

    # 1) Load message files
    typer.echo("Loading message files...")
    paths = glob.glob(f"{messages_path}/*.json")
    if not paths:
        typer.echo("No JSON files found in ./messages. Exiting.")
        raise typer.Exit()

    languages = []
    flattened_dicts = {}

    for filepath in paths:
        lang = Path(filepath).stem
        languages.append(lang)
        data = _load_json(filepath)
        flattened_dicts[lang] = flatten(data)

    # 2) Collect union of all keys across all languages
    all_keys = set()
    for lang in languages:
        all_keys.update(flattened_dicts[lang].keys())

    # 3) Build master dict: { key: { lang: translation_or_missing } }
    typer.echo("Building master translation dictionary...")
    master_translations = {}
    for key in sorted(all_keys):  # sorted for consistent ordering
        per_lang = {}
        for lang in languages:
            val = flattened_dicts[lang].get(key, "[MISSING]")
            per_lang[lang] = val
        master_translations[key] = per_lang

    # 4) If skip_llm is False, we attempt to fill in missing keys by calling Claude
    if not skip_llm:
        # Collect which dictionary entries have missing translations
        missing_items = {
            k: v for k, v in master_translations.items()
            if "[MISSING]" in v.values()
        }
        if missing_items:
            typer.echo(f"Found {len(missing_items)} entries with missing translations.")
            _request_claude_in_batches(missing_items, master_translations, batch_size)
        else:
            typer.echo("No missing translations found. Skipping LLM step.")

    # 5) Unflatten each language's updated translations & write to file
    typer.echo("Writing updated files...")
    for lang in languages:
        # Filter out [MISSING] so we don’t write placeholders
        updated_flattened = {}
        for k, all_lang_vals in master_translations.items():
            val = all_lang_vals[lang]
            if val != "[MISSING]":
                updated_flattened[k] = val

        # Unflatten
        updated_unflattened = unflatten(updated_flattened)
        # Write back out
        outpath = os.path.join(messages_path, f"{lang}.json")
        _write_json(outpath, updated_unflattened)

    typer.echo("Done!")


def _request_claude_in_batches(
    missing_dict: Dict[str, Dict[str, str]],
    master_translations: Dict[str, Dict[str, str]],
    batch_size: int,
):
    """
    Break up missing translations into batches and call Claude for each chunk.
    Merges the responses back into master_translations.
    """
    # Convert missing_dict keys into a list to chunk.
    keys = list(missing_dict.keys())

    for i in range(0, len(keys), batch_size):
        batch_keys = keys[i : i + batch_size]
        batch_data = {k: missing_dict[k] for k in batch_keys}

        # Build prompt instructing Claude how to fill in.
        prompt = (
            "You are a helpful translator. We have some incomplete translations "
            "marked with '[MISSING]'. Please fill them in. Return ONLY JSON, no extra explanation.\n\n"
            "Missing translations:\n"
            f"{json.dumps(batch_data, indent=2, ensure_ascii=False)}\n\n"
            "Please respond in the exact same structure, with missing fields translated "
            "in place of '[MISSING]'."
        )

        response_text = _call_claude_api(prompt)
        if not response_text:
            typer.echo("No response from Claude. Skipping this batch.")
            continue

        # Try to parse the response as JSON
        try:
            # Find the first '{' and the last '}' to isolate JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx == -1 or end_idx == -1:
                typer.echo("Could not find JSON in Claude's response.")
                continue

            json_str = response_text[start_idx : end_idx + 1]
            proposed_fixes = json.loads(json_str)

            # Merge fixes back into master_translations
            for k, v in proposed_fixes.items():
                if k not in master_translations:
                    continue
                for lang, text_val in v.items():
                    if text_val and text_val != "[MISSING]":
                        master_translations[k][lang] = text_val

        except Exception as e:
            typer.echo(f"Error parsing LLM JSON response: {e}")


################################################################################
#                                 CLI ENTRY                                    #
################################################################################

if __name__ == "__main__":
    app()
