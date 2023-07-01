
prompt_file="RolePlayV1.txt"
# model_file="WizardLM-30B-Uncensored/ggml-model-q4_0.bin"
model_file="WizardLM-13B-V1.0-Uncensored/ggml-model-q4_0.bin"

if [[ $(uname) == "Darwin" ]] && [[ $(uname -m) == "arm64" ]]; then

echo "Running on Mac Silicon with Metal GPU:"
# ./llama.cpp/main -m "./llama.cpp/models/$model_file" -ngl 1 --repeat_penalty 1.1 --color -i -f prompts/$prompt_file -r "USER: "
# ./llama.cpp/server -m "./llama.cpp/models/$model_file" -c 2048
python3 webui/app.py

else

echo "Running on CPU:"
# ./llama.cpp/main -m "./llama.cpp/models/$model_file" --repeat_penalty 1.1 --color -i -f prompts/$prompt_file -r "USER: "

fi