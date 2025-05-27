from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import requests
import base64
import os
import mimetypes

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            image_url = query_params.get('image_url')[0]

            if not image_url:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing "image_url" query parameter.'}).encode('utf-8'))
                return
            
            if "dropbox.com" in image_url:
                if "dl=0" in image_url:
                    image_url = image_url.replace("dl=0","dl=1")
                elif "?" not in image_url:
                    image_url = image_url + "?dl=1"

            image_mime_type = "application/octet-stream"
            try:
                img_res = requests.get(image_url, stream=True, timeout=10)
                img_res.raise_for_status()
                image_bytes = img_res.content

                if 'Content-Type' in img_res.headers:
                    image_mime_type = img_res.headers['Content-Type'].split(';')[0].strip()
                else:
                    path = urlparse(image_url).path
                    mime_type, _ = mimetypes.guess_type(path)
                    if mime_type:
                        image_mime_type = mime_type

                if not image_mime_type.startswith("image/"):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': f'Unsupported content type detected: {image_mime_type}. Must be an image.'}).encode('utf-8'))
                    return
                
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
            except requests.exceptions.RequestException as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Failed to download image from URL: {str(e)}'}).encode('utf-8'))
                return
            
            OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
            if not OPENROUTER_API_KEY:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'OPENROUTER_API_KEY missing.'}).encode('utf-8'))
                return
            
            headers = {
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'HTTP-Referer': 'image-processor-ai-tool.vercel.app', #optional
                'Content-Type': 'application/json'
            }

            model_name = "meta-llama/llama-4-maverick:free"

            fixed_prompt = """Analyze this blueprint.
            1.  **Identify the overall machine or operation** that these parts are intended to build or perform. Provide a concise name.
            2.  For **each individual part** shown in the blueprint:
                a.  **Label** it clearly with a descriptive name.
                b.  Provide a brief **description** of its visual characteristics and potential function.
                c.  **Identify the manufacturing classification** (e.g., "circular", "rectangular", "sheet metal", "cast", "machined", "assembled") and the **primary manufacturing process name** (e.g., "Turning", "Milling", "Stamping", "Injection Molding", "Welding", "Forging") used to create this part.
            3.  **Return all information in a single, comprehensive JSON object.** The structure should be exactly as follows:
                ```json
                {
                  "machine_or_operation_name": "string",
                  "parts": [
                    {
                      "label": "string",
                      "description": "string",
                      "manufacturing_process": {
                        "classification": "string",
                        "process_name": "string"
                      }
                    },
                    // ... (add more part objects as needed)
                  ]
                }
                ```
                Ensure the JSON is correctly formatted and parseable. Avoid any introductory or concluding text outside the JSON object itself, and do not wrap the JSON in markdown code blocks (e.g., ```json ... ```).
            """

            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": fixed_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{image_mime_type};base64,{base64_image}"}}
                        ]
                    }
                ],
                "max_tokens": 4000
            }

            try:
                openrouter_response = requests.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=120
                )

                openrouter_response.raise_for_status()
                llm_output = openrouter_response.json()
            except  requests.exceptions.RequestException as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'LLM model API failed'}).encode('utf-8'))
                return

            if llm_output and llm_output.get('choices'):
                llm_content = llm_output['choices'][0]['message']['content']
                try:
                    processed_response = json.loads(llm_content)
                except json.JSONDecodeError:
                    processed_response = {"raw_llm_response": llm_content, "note": "LLM output was not perfectly valid JSON."}
            else:
                processed_response = {"error": "Unexpected LLM response format", "full_response": llm_output}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(processed_response).encode('utf-8'))
            return

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'An unexpected error occurred: {str(e)}'}).encode('utf-8'))
            return