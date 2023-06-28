
cd llama.cpp

if [[ $(uname) == "Darwin" ]] && [[ $(uname -m) == "arm64" ]]; then

LLAMA_METAL=1 make

else

make

fi