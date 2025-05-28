from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            imgbb_api_key = os.environ.get('IMGBB_API_KEY')
            if not imgbb_api_key:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'IMGBB_API_KEY environment variable not set.'}).encode('utf-8'))
                return

            imgbb_upload_url = "https://api.imgbb.com/1/upload"

            response_data = {
                "upload_service_name": "ImgBB",
                "upload_url": imgbb_upload_url,
                "api_key": imgbb_api_key,
                "instructions": "Make a POST request to the upload_url with 'key' (your API key) and 'image' (base64 encoded image or URL) as form-data."
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return

        except:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'An unexpected error occurred: {str(e)}'}).encode('utf-8'))
            return