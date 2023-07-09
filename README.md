# 📖 LLM RP

<p align="center">
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/psf/black"><img src="https://github.com/rbourgeat/llm-rp/actions/workflows/pylint.yml/badge.svg"></a>
</p>

<p align="center">
✨ Your Custom Offline Role Play with AI on Mac and Linux (for now) 🧙‍♂️
</p>

![LLM RP](llm-rp.png)

## 📎 Requirement

For now, Mac & Linux:
- Python >= 3.8
- `pip install -r requirements.txt && python3 -m spacy download en_core_web_sm`
- Install `git lfs`

## 🛠️ Config

You can custom global variables at the top of `app/run.py` as you want.

For increase performance, you can reduce the generated images size,
the number of iterations etc...

🖍️ Note: the output images folder is in `app/images/`

## 👉🏻 Start

Each time you want to run the game:

```bash
python3 app/run.py
```

The first time you load the app you will wait a while,
because the program will download, export and quantize 
the better llama model for your config and install stable diffusion.

Next open your browser at http://127.0.0.1:5000

Click on the 🗑️ for reset le Role Play

You can customize the prompt here: `prompts/RolePlay.txt`

## 📝 Todo

- 💾 Create a persistent role play (with save system)
- 🖼️ Adding Quantized Stable Diffusion
- 🛠️ Compile for GPU Linux / GPU Windows
- 🎤 Adding [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- 🔉 Adding [Bark](https://github.com/suno-ai/bark) or an other Text-Prompted Generative Audio Model
- 🔥 Doing a better interface
- 🔒 Lock user input when model generating response

## 🔎 Resources

- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [WizardLM](https://huggingface.co/ehartford/)
- [Diffusers](https://github.com/huggingface/diffusers)
- [ML Stable Diffusion](https://github.com/apple/ml-stable-diffusion)
- [DreamShaper](https://huggingface.co/Lykon/DreamShaper)
