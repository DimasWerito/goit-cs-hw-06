import os
import socket
import multiprocessing
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pymongo import MongoClient
import json

# MongoDB setup
client = MongoClient('mongodb://mongodb:27017/')
db = client['messages_db']
messages_collection = db['messages']

# HTTP server setup
class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/message':
            self.path = '/message.html'
        elif self.path.endswith('.css') or self.path.endswith('.png'):
            self.path = self.path
        else:
            self.path = '/error.html'
            self.send_response(404)
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)

            # Send data to the socket server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(('localhost', 5000))
                sock.sendall(post_data.encode('utf-8'))

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b'Message submitted')

def run_http_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, CustomHandler)
    print("HTTP Server running on port 3000...")
    httpd.serve_forever()

def run_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))
    server.listen(5)
    print("Socket Server running on port 5000...")

    while True:
        client_socket, addr = server.accept()
        data = client_socket.recv(1024)
        if data:
            message_data = json.loads(data.decode('utf-8'))
            message_data["date"] = datetime.now().isoformat()
            messages_collection.insert_one(message_data)
            print("Message saved to MongoDB:", message_data)
        client_socket.close()

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=run_http_server)
    p2 = multiprocessing.Process(target=run_socket_server)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
