#!/usr/bin/env python3
"""
Mock Redis Server for Forensic Tool
模拟 Redis 服务，支持基本的内存操作
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time
import hashlib

class MockRedis:
    def __init__(self):
        self.data = {}
        self.expiry = {}

    def set(self, key, value):
        self.data[key] = value
        return True

    def setex(self, key, seconds, value):
        self.data[key] = value
        self.expiry[key] = time.time() + seconds
        return True

    def get(self, key):
        if key in self.expiry and time.time() > self.expiry[key]:
            del self.data[key]
            del self.expiry[key]
            return None
        return self.data.get(key)

    def keys(self, pattern):
        import fnmatch
        return [k for k in self.data.keys() if fnmatch.fnmatch(k, pattern)]

    def delete(self, *keys):
        count = 0
        for key in keys:
            if key in self.data:
                del self.data[key]
                if key in self.expiry:
                    del self.expiry[key]
                count += 1
        return count

    def memory_purge(self):
        pass

    def config_set(self, key, value):
        return True

redis = MockRedis()

class MockRedisHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return

        if self.path == '/set':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            key, value = body.split('\r\n', 1)
            redis.set(key, value)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'+OK')

        elif self.path == '/setex':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            parts = body.split('\r\n')
            key = parts[0]
            seconds = int(parts[1])
            value = parts[2]
            redis.setex(key, seconds, value)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'+OK')

        elif self.path == '/del':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            keys = body.split('\r\n')
            count = redis.delete(*keys)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f":{count}".encode())

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return

        key = self.path[1:]

        if self.path.startswith('/get/'):
            key = self.path[5:]
            value = redis.get(key)
            if value:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(value)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'nil')

        elif self.path.startswith('/keys/'):
            pattern = self.path[6:]
            keys = redis.keys(pattern)
            response = '\r\n'.join(keys).encode() if keys else b''
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response)

        else:
            value = redis.get(key)
            if value:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(value)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'nil')

def run_server(port=6379):
    server = HTTPServer(('localhost', port), MockRedisHandler)
    print(f"Mock Redis Server running on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
