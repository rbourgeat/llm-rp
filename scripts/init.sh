
cd llama.cpp

if [[ $(uname) == "Darwin" ]] && [[ $(uname -m) == "arm64" ]]; then

make clean && LLAMA_METAL=1 make

else

make clean && make

fi