from http.server import BaseHTTPRequestHandler
import json
import random
import os
import base64
import mimetypes

MEMES_DIR_NAME = "memes"
script_dir = os.path.dirname(os.path.abspath(__file__))
project_base_dir = os.path.dirname(script_dir)
memes_path = os.path.join(project_base_dir, MEMES_DIR_NAME)

print(f"Scanning for memes in: {memes_path}")

SANATIZED_MEME_PATHS = []
if os.path.isdir(memes_path):
    for filename in os.listdir(memes_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            SANATIZED_MEME_PATHS.append(f"/{MEMES_DIR_NAME}/{filename}")
    print(f"Found {len(SANATIZED_MEME_PATHS)} memes.")
else:
    print(f"Warning: Memes directory not found at {memes_path}. List will be empty.")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not SANATIZED_MEME_PATHS:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
            self.end_headers()
            response_data = {'error': 'No sanitized meme paths configured or found.'}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return

        selected_meme_path = random.choice(SANATIZED_MEME_PATHS)

        with open(selected_meme_path, "rb") as image_file:
                encoded_image_data = base64.b64encode(image_file.read()).decode('utf-8')

        content_type, _ = mimetypes.guess_type(encoded_image_data)
        if content_type is None:
            content_type = "application/octet-stream"

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
        self.end_headers()
        response_data = {
            'image_data': encoded_image_data,
            'content_type': content_type
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'https://blueprint-upload-ui.vercel.app')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()