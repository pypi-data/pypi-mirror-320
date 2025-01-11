import json
import os
from pathlib import Path
import tiktoken

from atlaz.old_overview.main_overview import gather_repository

def count_tokens(string_inp):
    encc = tiktoken.encoding_for_model("gpt-4")
    encoded_str = encc.encode(string_inp)
    return len(encoded_str)

def build_code_prompt(file_contents: list[dict]):
    output_text = '\n'
    for file in file_contents:
        output_text += f'```{file["name"]}\n{file["content"]}\n```\n\n\n'
    return output_text[:-2]

def manual_overview(focus_directories=list[str], manual_ignore_files=list[str]):
    directory_data, directory_structure = gather_repository(script_path=Path(__file__).resolve().parent, focus_directories=focus_directories, manual_ignore_files=manual_ignore_files)    
    prompt = directory_structure + "\n\n" + build_code_prompt(directory_data)
    return prompt