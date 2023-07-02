"""
LLM RP
by rbourgeat
"""

import os
import platform
import sys
import webbrowser
import subprocess
import threading
from queue import Queue, Empty
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
output_queue = Queue()
input_queue = Queue()
PROCESS = None


@app.route('/')
def index():
    """
    Renders the index.html template.

    Returns:
        Rendered template.
    """
    return render_template('index.html')


@app.route('/execute', methods=['POST'])
def execute():
    """
    Executes a command.

    Returns:
        JSON response indicating that the command execution has started.
    """
    command = request.form['command']

    def run_script():
        """
        Runs the script in a separate thread.
        """
        global PROCESS # pylint: disable=global-statement
        PROCESS = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            universal_newlines=True,
        )
        current_word = ''
        while True:
            char = PROCESS.stdout.read(1)
            if not char:
                break
            if char == '\n':
                output_queue.put(current_word + '<br>')
                current_word = ''
            elif char.isspace():
                if current_word:
                    output_queue.put(current_word)
                    output_queue.put(' ')
                current_word = ''
            else:
                current_word += char
        PROCESS.wait()

    thread = threading.Thread(target=run_script)
    thread.start()
    return jsonify(result='started')


@app.route('/get_output')
def get_output():
    """
    Retrieves the output from the output queue.

    Returns:
        JSON response with the output.
    """
    try:
        output = output_queue.get(timeout=1.0)
        if 'USER:' in output:
            output = ''
    except Empty:
        output = ''
    return jsonify(output=output)


@app.route('/send_input', methods=['POST'])
def send_input():
    """
    Sends input to the input queue.

    Returns:
        JSON response indicating the success of sending the input.
    """
    input_text = request.form['input']
    input_queue.put(input_text + '\n')
    output_queue.put('<p id="user-message">' + input_text + '</p><br>')
    return jsonify(result='success')


@app.route('/check_llama_cpp', methods=['GET'])
def check_llama_cpp():
    """
    Checks if the llama.cpp/main file exists and compiles it if necessary.

    Returns:
        JSON response indicating the existence of the file.
    """
    filename = 'llama.cpp/main'
    exists = os.path.exists(filename)
    if not exists:
        compile_file(filename)
    return jsonify(exists=exists)


def compile_file(filename):
    """
    Compiles the specified file.

    Args:
        filename: llama.cpp binary.
    """
    if filename == 'llama.cpp/main':
        system = platform.system()
        if system == 'Darwin':
            print('Build on macOS with METAL for GPU')
            bash_command = 'make -C llama.cpp/ clean && LLAMA_METAL=1 make -C llama.cpp/'
        elif system == 'Linux':
            print('Build on Linux for CPU')
            bash_command = 'make -C llama.cpp/ clean && make -C llama.cpp/'
        else:
            print('Running on an unsupported operating system')
            sys.exit()
        subprocess.run(bash_command, shell=True, check=True, capture_output=True)


def process_input():
    """
    Processes input from the input queue and sends it to the running process.
    """
    global PROCESS # pylint: disable=global-variable-not-assigned, global-statement
    webbrowser.open('http://127.0.0.1:5000')
    while True:
        if PROCESS is not None:
            input_text = input_queue.get()
            PROCESS.stdin.write(input_text)
            PROCESS.stdin.flush()


if __name__ == '__main__':
    input_thread = threading.Thread(target=process_input)
    input_thread.start()
    app.run()
