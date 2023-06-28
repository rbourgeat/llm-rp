
prompt_file="RPG_NSFW.txt"
model_file="ggml-vic13b-q4_0.bin"

if [[ $(uname) == "Darwin" ]] && [[ $(uname -m) == "arm64" ]]; then

echo "Running on Mac Silicon with Metal GPU:"
./llama.cpp/main -m "./llama.cpp/models/$model_file" -ngl 1 --repeat_penalty 1.1 --color -i -f prompts/$prompt_file -r "USER: "

else

echo "Running on CPU:"
./llama.cpp/main -m "./llama.cpp/models/$model_file" --repeat_penalty 1.1 --color -i -f prompts/$prompt_file -r "USER: "

fi