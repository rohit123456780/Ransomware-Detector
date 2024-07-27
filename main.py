from flask import Flask, render_template, request, jsonify
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib
import json
from threading import Thread

# Configuration
CONFIG_FILE = 'config.json'
LOG_FILE = 'logs/ransomware_detector.log'
MONITOR_DIRECTORY = 'C:/Users/dashi'  # Change this to your desired directory

# Flask app initialization
app = Flask(__name__)

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Read configuration
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    return config

# File hash calculation
def calculate_file_hash(file_path):
    hash_alg = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_alg.update(chunk)
    return hash_alg.hexdigest()

# Watchdog event handler
class RansomwareEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.config = load_config()
    
    def on_created(self, event):
        if not event.is_directory:
            file_hash = calculate_file_hash(event.src_path)
            if file_hash in self.config['ransomware_hashes']:
                logging.info(f'Ransomware detected: {file_hash} at {event.src_path}')
                # For demonstration, this would update the result in the web interface
                app.config['DETECTED'] = True

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start_monitoring():
    # Start monitoring in a separate thread
    thread = Thread(target=start_monitoring_thread)
    thread.start()
    return jsonify({"status": "Monitoring started."})

@app.route('/stop')
def stop_monitoring():
    # Placeholder for stopping monitoring
    # Implement stopping logic if required
    return jsonify({"status": "Monitoring stopped."})

@app.route('/status')
def status():
    detected = app.config.get('DETECTED', False)
    return jsonify({"status": "Monitoring directory: " + MONITOR_DIRECTORY, "detected": detected})

def start_monitoring_thread():
    event_handler = RansomwareEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=MONITOR_DIRECTORY, recursive=True)
    observer.start()
    observer.join()

if __name__ == '__main__':
    app.config['DETECTED'] = False
    app.run(debug=True)



