import argparse
from bs4 import BeautifulSoup
import pandas as pd
import json
import importlib.resources

def load_translations(file_name):
    try:
        translations_file = importlib.resources.read_text('checked', file_name)
        translations = json.loads(translations_file) 
        return translations

    except FileNotFoundError:
        print(f"Translation file {file_name} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {file_name}.")
        return {}
    except Exception as e:
        print(f"Error loading translations: {e}")
        return {}


def convert_spreadsheet(file, language, translations):
    columns = translations.get(language, translations['EN'])  # Default to English if language not found

    try:
        with open(file, 'r', encoding='utf-8') as document:
            soup = BeautifulSoup(document, 'html.parser')
    except FileNotFoundError:
        print(f"Error: The file {file} was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    target_paragraphs = soup.find_all('p', style=lambda x: x and 'padding-inline-start: 40px;' in x)
    df = pd.DataFrame(columns=columns)
    rows = []

    for paragraph in target_paragraphs:
        fact = paragraph.get_text(strip=True)
        rows.append({
            columns[0]: '',    # Status
            columns[1]: fact,  # Fact
            columns[2]: '',    # Confirmation
            columns[3]: '',    # Source
            columns[4]: '',    # Notes
            columns[5]: ''     # Revision
        })

    new_df = pd.DataFrame(rows)

    df = pd.concat([df, new_df], ignore_index=True)

    output_file = file + ".ods"
    df.to_excel(output_file, index=False, engine='odf')

    print(f"Spreadsheet saved as {output_file}")

def main():
    parser = argparse.ArgumentParser(description="A simple CLI app to convert HTML files to Spreadsheets, for Fact-Checking")
    parser.add_argument('file', type=str, help='The HTML file to be converted')
    parser.add_argument('-l', '--language', type=str, default='EN', choices=['EN', 'PT'], help='Language for column headers (default: EN)')
    args = parser.parse_args()

    translations = load_translations('translations.json')
    print(f"Converting {args.file} with language {args.language}!")
    convert_spreadsheet(args.file, args.language, translations)

if __name__ == "__main__":
    main()
