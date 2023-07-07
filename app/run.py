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
import shutil
import string
from queue import Queue, Empty
import random
import numpy as np
import psutil
from flask import Flask, render_template, request, jsonify
import git
from git import Git, GitCommandError
# pylint: disable=import-error
from python_coreml_stable_diffusion.pipeline import get_coreml_pipe
from diffusers import StableDiffusionPipeline

app = Flask(__name__)
output_queue = Queue()
input_queue = Queue()

PROCESS = None
COREML_PIPE = None

MODEL_7B = 'llama.cpp/models/WizardLM-7B-V1.0-Uncensored/ggml-model-q4_0.bin'
MODEL_13B = 'llama.cpp/models/WizardLM-13B-V1.0-Uncensored/ggml-model-q4_0.bin'
MODEL_33B = 'llama.cpp/models/WizardLM-33B-V1.0-Uncensored/ggml-model-q4_0.bin'
SD_MODEL_VERSION = "stabilityai/stable-diffusion-2-1-base"

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
    model = "WizardLM-7B-V1.0-Uncensored"
    if os.path.exists(MODEL_13B):
        model = "WizardLM-13B-V1.0-Uncensored"
    if os.path.exists(MODEL_33B):
        model = "WizardLM-33B-V1.0-Uncensored"
    print(f"Loading {model} model...")

    command = ""
    system = platform.system()
    if system == 'Darwin':
        command = f'./llama.cpp/main -m llama.cpp/models/{model}/ggml-model-q4_0.bin \
            -ngl 1 --repeat_penalty 1.1 --color -i -f app/prompts/RolePlay.txt -r "USER: "'
    elif system == 'Linux':
        command = f'./llama.cpp/main -m llama.cpp/models/{model}/ggml-model-q4_0.bin \
            --repeat_penalty 1.1 --color -i -f app/prompts/RolePlay.txt -r "USER: "'
    else:
        sys.exit()

    def run_script():
        """
        Runs the script in a separate thread.
        """
        global PROCESS # pylint: disable=global-statement
        with subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            universal_newlines=True,
        ) as PROCESS:
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
    exists_7b = os.path.exists(MODEL_7B)
    exists_13b = os.path.exists(MODEL_13B)
    exists_30b = os.path.exists(MODEL_33B)
    if not exists_7b and not exists_13b and not exists_30b:
        install_model_rp()
    if not os.path.exists("app/models/stable-diffusion-2-1"):
        install_model_sd()
    else:
        threading.Thread(target=load_stable_diffusion_model).start()

    filename = 'llama.cpp/main'
    exists = os.path.exists(filename)
    if not exists:
        compile_file(filename)
    return jsonify(exists=exists)


def convert_and_quantize(path):
    """
    Convert and quantize a model using llama.cpp.

    Args:
        path (str): The path to the model.

    Raises:
        subprocess.CalledProcessError: If any of the subprocess commands fail.

    """
    print("Installing llama.cpp requirements...")
    command = "python3 -m pip install -r llama.cpp/requirements.txt"
    subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    print("Converting model...")
    command = "python3 llama.cpp/convert.py " + path
    subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    print("Quantizing model...")
    command = f"./llama.cpp/quantize {path}/ggml-model-f16.bin {path}/ggml-model-q4_0.bin q4_0"
    subprocess.run(command, shell=True, capture_output=True, text=True, check=True)


def install_model_rp():
    """
    Downloads and installs the appropriate WizardLM model based on the available VRAM.
    """
    vram = get_vram()
    print(f"Available VRAM: {vram:.2f} GB")
    print("Downloading WizardLM model...")
    local_path = "llama.cpp/models/"
    if vram >= 30:
        repo_url = "https://huggingface.co/ehartford/WizardLM-33B-V1.0-Uncensored.git"
        folder_path = local_path + "/WizardLM-33B-V1.0-Uncensored"
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        git.Git().clone(repo_url, folder_path)
        git_repo = Git(local_path)
        git_repo.lfs("fetch")
        git_repo.checkout("HEAD", "--", ".")
        convert_and_quantize(folder_path)
    elif vram >= 15:
        repo_url = "https://huggingface.co/ehartford/WizardLM-13B-V1.0-Uncensored.git"
        folder_path = local_path + "/WizardLM-13B-V1.0-Uncensored"
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        git.Git().clone(repo_url, folder_path)
        git_repo = Git(local_path)
        git_repo.lfs("fetch")
        git_repo.checkout("HEAD", "--", ".")
        convert_and_quantize(folder_path)
    else:
        repo_url = "https://huggingface.co/ehartford/WizardLM-7B-V1.0-Uncensored.git"
        folder_path = local_path + "/WizardLM-7B-V1.0-Uncensored"
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        git.Git().clone(repo_url, folder_path)
        git_repo = Git(local_path)
        git_repo.lfs("fetch")
        git_repo.checkout("HEAD", "--", ".")
        convert_and_quantize(folder_path)


def install_model_sd():
    """Downloads and installs Stable Diffusion 2.1.

    Returns:
        None
    """
    try:
        print("Downloading Stable Diffusion 2.1 model...")
        repo_url = "https://huggingface.co/apple/coreml-stable-diffusion-2-1-base-palettized"
        folder_path = "app/models/stable-diffusion-2-1"
        local_path = "app/models/"

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        git.Git().clone(repo_url, folder_path)
        git_repo = git.Git(local_path)
        git_repo.lfs("fetch")
        git_repo.checkout("HEAD", "--", ".")

    except GitCommandError as error:
        print("Error when running Git command:", str(error))

    except OSError as error:
        print("Error when accessing file or directory:", str(error))

    finally:
        print("Stable Diffusion 2.1 model downloaded here: ", folder_path)


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
        elif system == 'Windows':
            print('Build on Windows for CPU')
            bash_command = 'cd llama.cpp;mkdir build;cd build;cmake ..;\
                cmake --build . --config Release'
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


def get_vram():
    """
    Calculates the available VRAM by subtracting the available system memory
    from the total system memory.
    
    Returns:
        float: Available VRAM in gigabytes (GB).
    """
    mem_info = psutil.virtual_memory()
    total_memory = mem_info.total
    ram_size = psutil.virtual_memory().available
    vram_size = total_memory - ram_size
    vram_size_gb = vram_size / (1024 ** 3)  # Convert bytes to GB
    return vram_size_gb


def generate_random_name(length):
    """
    Generate a random name consisting of lowercase letters.

    Args:
        length (int): The length of the random name to generate.

    Returns:
        str: A randomly generated name of the specified length.
    """
    letters = string.ascii_lowercase
    random_name = ''.join(random.choice(letters) for _ in range(length))
    return random_name


@app.route('/generate_image', methods=['POST'])
def generate_image():
    """
    Generate an image based on the provided prompt.

    Args:
        None

    Returns:
        A JSON response containing the generated file name.
    """
    prompt = request.form['prompt']

    # pylint: disable=not-callable
    image = COREML_PIPE(
        prompt=prompt,
        height=COREML_PIPE.height,
        width=COREML_PIPE.width,
        num_inference_steps=50,
        guidance_scale = 8
    )

    random_file_name = generate_random_name(10) + '.png'

    image['images'][0].save(str("app/images/" + random_file_name))

    return jsonify({'file_name': random_file_name})


def load_stable_diffusion_model():
    """Load the Stable Diffusion model pipeline."""
    print("Loading Stable Diffusion pipeline...")
    global COREML_PIPE

    np.random.seed(42)
    pytorch_pipe = StableDiffusionPipeline.from_pretrained(SD_MODEL_VERSION,
                                                        use_auth_token=True)
     # pylint: disable=redefined-outer-name, unused-variable
    COREML_PIPE = get_coreml_pipe(pytorch_pipe=pytorch_pipe,
                                mlpackages_dir="app/models/stable-diffusion-2-1/original/packages",
                                model_version=SD_MODEL_VERSION,
                                compute_unit="CPU_AND_NE")
    print("Stable Diffusion pipeline loaded !")


if __name__ == '__main__':
    threading.Thread(target=process_input).start()
    app.run()
