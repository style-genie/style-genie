# fashion_agent/agent.py
# This file will contain the main logic for the AI agent.

import google.generativeai as genai
import json
import os
import time

# Replace with your actual Gemini API key
GEMINI_API_KEY = "AIzaSyC2pgSkdovwkpQgBLuWTpb-JMruxXXJIeM"
genai.configure(api_key=GEMINI_API_KEY)

def generate_description(item_name, brand, price=None):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"Write a short, engaging description for a {brand} {item_name}."
    if price:
        prompt += f" The price is ${price}."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating description: {e}")
        return ""

async def process_json_files(directory="ssense_data"):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                data = None
                with open(filepath, "r") as f:
                    data = json.load(f)
                if data is not None:
                    for item in data:
                        description = item.get("description", "") #  <-- Änderung hier
                        if description is None or description == "": # <-- kann man nun auch zu if not description: kürzen.
                            description = generate_description(item["name"], item["brand"], item.get("price"))
                            item["description"] = description.strip()
                            print(item)
                            #time.sleep(1)
                        else:
                            print(item["name"] + " already has a description")
                            print(item["description"])

                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Processed {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

async def main():
    await process_json_files()
    print("Finished processing JSON files.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
