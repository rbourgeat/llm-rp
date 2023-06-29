from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

def parse(string):
    split_string = string.split("[end of text]")
    result = split_string[0]
    split_string = result.split("===")
    result = split_string[1]
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-llama', methods=['POST'])
def run_llama():
    try:
        command = './llama.cpp/main -m ./llama.cpp/models/ggml-vic13b-q4_0.bin -ngl 1 --repeat_penalty 1.1 -f prompts/RP_NSFW.txt -r "USER: "'
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        response = parse(output.decode('utf-8'))
        return {'output': response}
    except subprocess.CalledProcessError as e:
        error_message = e.output.decode('utf-8')
        return {'error': error_message}, 500

if __name__ == '__main__':
    app.run(debug=True)
