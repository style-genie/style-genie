import json

def process_for_pinecone(input_file, output_file):
    """Transforms data.json into a Pinecone-compatible format."""
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {input_file}: {e}")
        return

    pinecone_records = []
    for item_id, item in data.items():
         #"_id": str(item_id),
        record = {
           
            **item  # Include all other fields from the original item
        }
        pinecone_records.append(record)

    with open(output_file, "w") as outfile:
        json.dump(pinecone_records, outfile, indent=2)

if __name__ == "__main__":
    process_for_pinecone("data.json", "pinecone_data.json")
    print("Successfully processed data for Pinecone and saved to pinecone_data.json")
