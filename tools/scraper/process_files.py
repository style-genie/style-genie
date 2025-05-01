import json
import os

def extract_metadata(filename):
    """Extracts gender and chunk information from the filename."""
    if "women" in filename:
        gender = "women"
    elif "men" in filename:
        gender = "men"
    else:
        gender = "unknown"
    
    try:
        chunk = int(filename.split("_")[-1].split(".")[0])
    except ValueError:
        chunk = None
    return gender, chunk

def process_json_files(directory):
    """Processes JSON files in a directory and combines them into a single JSON file."""
    combined_data = {}
    item_id = 0
    for filename in os.listdir(directory):
        if filename.endswith(".json") and (filename.startswith("women_output") or filename.startswith("men_output")):
            filepath = os.path.join(directory, filename)
            gender, chunk = extract_metadata(filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    for item in data:
                        item["gender"] = gender
                        item["chunk"] = chunk
                        item_id += 1
                        item["_id"] = item_id
                        item["id"] = item_id
                        combined_data[item_id] = item
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {filename}: {e}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    with open("data.json", "w") as outfile:
        json.dump(combined_data, outfile, indent=2)

if __name__ == "__main__":
    process_json_files("raw_data")
    print("Successfully processed and combined JSON files into data.json")
