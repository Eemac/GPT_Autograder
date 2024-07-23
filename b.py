import os
import requests
import base64

# Configuration
GPT4V_KEY = "a09bf535a7d5452cb293dc51613cb8db"
IMAGE_PATH = "assignmentData/1307/out0.jpg"
encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
headers = {
    "Content-Type": "application/json",
    "api-key": GPT4V_KEY,
}

# Payload for the request
payload = {
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "What's in the picture."
        },
        {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image}"
                }
        }
      ]
    }
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}

GPT4V_ENDPOINT = "https://call-next-wave.openai.azure.com/openai/deployments/ISIM_Autograder/chat/completions?api-version=2024-02-15-preview"

# Send request
try:
    response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
except requests.RequestException as e:
    raise SystemExit(f"Failed to make the request. Error: {e}")

# Handle the response as needed (e.g., print or process)
print(response.json())