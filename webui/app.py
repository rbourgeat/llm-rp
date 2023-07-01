from flask import Flask, render_template, request, jsonify
import subprocess
import threading
from queue import Queue, Empty

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
        if "USER:" in output:
            output = ''
    except Empty:
        output = ''
    return jsonify(output=output)

@app.route('/send_input', methods=['POST'])
def send_input():
    input_text = request.form['input']
    input_queue.put(input_text + '\n')
    output_queue.put(input_text + '\n')
    return jsonify(result='success')

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