from flask import Flask, render_template, request, jsonify, after_this_request
import subprocess
import threading
from queue import Queue, Empty
import os
import platform
import sys

app = Flask(__name__)
output_queue = Queue()
input_queue = Queue()
process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    command = request.form['command']

    def run_script():
        global process
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, universal_newlines=True)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            output_queue.put(line.strip())
        process.wait()

    thread = threading.Thread(target=run_script)
    thread.start()
    return jsonify(result='started')

@app.route('/get_output')
def get_output():
    try:
        output = output_queue.get(timeout=1.0)
        output = '<p>' + output + '</p>'
        if "USER:" in output:
            output = ''
    except Empty:
        output = ''
    return jsonify(output=output)

@app.route('/send_input', methods=['POST'])
def send_input():
    input_text = request.form['input']
    input_queue.put(input_text + '\n')
    output_queue.put('<p id="user-message">' + input_text + '</p>')
    return jsonify(result='success')

@app.route('/check_llama_cpp', methods=['GET'])
def check_llama_cpp():
    filename = 'llama.cpp/main'
    exists = os.path.exists(filename)
    if not exists:
        compile(filename)
    return jsonify(exists=exists)

def compile(filename):
    if filename == "llama.cpp/main":
        system = platform.system()
        if system == 'Darwin':
            print("Build on macOS with METAL for GPU")
            bash_command = 'make -C llama.cpp/ clean && LLAMA_METAL=1 make -C llama.cpp/'
        elif system == 'Linux':
            print("Build on Linux for CPU")
            bash_command = 'make -C llama.cpp/ clean && make -C llama.cpp/'
        else:
            print("Running on an unsupported operating system")
            sys.exit()
        subprocess.run(bash_command, shell=True, check=True, capture_output=True)

def process_input():
    global process
    while True:
        if process is not None:
            input_text = input_queue.get()
            process.stdin.write(input_text)
            process.stdin.flush()

if __name__ == '__main__':
    input_thread = threading.Thread(target=process_input)
    input_thread.start()
    app.run()