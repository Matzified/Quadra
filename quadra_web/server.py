import http.server
import socketserver
import urllib.request
import urllib.error
import json
import urllib.parse
import os

PORT = 8080

class QuadraHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/api/check':
            query = urllib.parse.parse_qs(parsed_path.query)
            username = query.get('name', [''])[0]
            
            if not username:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Missing name"}')
                return

            url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
            
            status_code = 500
            available = False
            msg = "Error"
            
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.getcode() == 200:
                        status_code = 200
                        available = False
                        msg = "Taken"
            except urllib.error.HTTPError as e:
                status_code = e.code
                if e.code == 404:
                    available = True
                    msg = "Available"
                elif e.code == 429:
                    msg = "Rate Limited"
                else:
                    msg = f"Err: {e.code}"
            except Exception as e:
                msg = str(e)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response_data = {
                "username": username,
                "available": available,
                "status": msg,
                "code": status_code
            }
            self.wfile.write(json.dumps(response_data).encode())
            return
            
        # Serve files for other paths
        return super().do_GET()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), QuadraHandler) as httpd:
        print(f"Quadra Web Server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
