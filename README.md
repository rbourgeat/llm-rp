# 📖 LLM RP

Your Custom Offline Role Play with AI on Mac and Linux (for now).

![LLM RP](llm-rp.png)

## 📝 Requirement

For now:
- Python >= 3.8
- Mac: `pip install -r requirements.txt && pip install coremltools`
- Linux: `pip install -r requirements.txt`
- Install `git lfs`

## 👉🏻 Start

Each time you want to run the game:

```bash
python3 app/run.py
```

The first time you load the app you will wait a while,
because the program will download, export and quantize 
the better llama model for your config.

Next open your browser at http://127.0.0.1:5000

Click on the 🗑️ for reset le Role Play

You can customize the prompt `prompts/RolePlay.txt`

## 📝 Todo

- 💾 Create a persistent role play (with save system)
- 🖼️ Adding Stable Diffusion
- 🛠️ Compile for GPU Linux / GPU Windows
- 🎤 Adding [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- 🔉 Adding [Bark](https://github.com/suno-ai/bark) or an other Text-Prompted Generative Audio Model
- 🔥 Doing a better interface
- 🔒 Lock user input when model generating response

## 🔎 Sources

- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [WizardLM](https://huggingface.co/ehartford/)
