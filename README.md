# Project Kiwi
Project Kiwi is a fork of Just Rayen's Project Riko.

I saw their YouTube video and wanted to look through the code. 

I found it... interesting.

Here is my attempt at making it more modular and easier to understand, while keeping the core functionality generally 
intact.

I should mention, however, that I did literally tear the entire original project apart at the seams and reassemble it 
in a way that made more sense to me, so there are significant changes to the code structure and organisation.

**Tested with Python 3.12 on Linux Mint 22.2 (Zara)**


## Design Philosophy
- **Run everything locally.** I want this to be able to run fully offline with zero external dependencies.
- **Keep it modular.** Within reason, each component should be able to run independently for testing and development 
purposes.
- **Simple & Working > Complex & Broken.** I want to have a functional version of the project as soon as possible, 
and then build on it from there.
- **Leading from that, clarity > cool tricks.**  I want my code to be easy to understand and follow. 


## Features
- **LLM-based Dialogue** using Ollama. (configurable system prompt)
- **JSON-based Conversation Memory** to keep context during interactions.
- **YAML-based Config** for personality configuration.
- **Voice Activity Detection** using Silero VAD.
- **Speech Recognition** using Faster-Whisper.
- **Voice Generation** using Resemble AI's Chatterbox.


### Pipeline
Currently:
1. Takes in a user input from the console
2. Passes it to LLM model (with history)
3. Generates a response
4. Prints the output back to the console

Technical capability:
(The code I've written works, I just don't have enough VRAM on my RTX 3060Ti to run the full pipeline)
1. Listens to your voice via microphone (Voice Activity Detection with Silero VAD)
2. Transcribes it with Faster-Whisper
3. Passes it to GPT (with history)
4. Generates a response
5. Synthesises a voice reply using Resemble AI's Chatterbox
6. Plays the output back to you

Pre-fork (original project):
1. ~~Riko listens to your voice via microphone (push to talk)~~
2. ~~Transcribes it with Faster-Whisper~~
3. ~~Passes it to GPT (with history)~~
4. ~~Generates a response~~
5. ~~Synthesises Riko's voice using GPT-SoVITS~~
6. ~~Plays the output back to you~~


Voice Generation and Speech Recognition are currently unused due to personally not having the hardware to run them, 
but the code is there and should work if you have the necessary resources.

JSON-based Conversation Memory is a placeholder, and will be replaced with a more robust solution like a vector 
database.


## Configuration
All prompts and parameters are stored in `character_config.yaml`.

You can define personalities by modifying the config file.


## Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```


## Usage

### 1. Run the main script:

```bash
python main.py
```

Each module is technically designed to be capable of independent operation, mostly for testing purposes, but the main 
script will run the full application, and is the recommended way to experience the full functionality of the project.


## TODO / Future Improvements
My own to-do list:
* [x] Remove all the external API calls and make everything run locally
* [x] Reorganise code structure, with better modularity and separation of concerns
* [x] Re-implement voice generation and speech recognition modules.
* [ ] Replace JSON-based conversation memory with a vector database (probably ChromaDB)
* [ ] Implement a dynamic emotional modelling system to hook into the LLM and voice synthesis to allow for more 
expressive and emotionally varied responses.

From the original project:
* [ ] GUI or web interface
* [x] Live microphone input support
* [ ] ~~Emotion or tone control in speech synthesis~~ (edited and yoinked over to my own to-do list)
* [ ] VRM model frontend


## Credits
- **Just Rayen's Project Riko** (https://github.com/rayenfeng/riko_project)
- **Ollama** for the local LLM hosting solution
- **Chatterbox-TTS** by Resemble AI (https://github.com/resemble-ai/chatterbox)
- **Faster-Whisper** by SYSTRAN (https://github.com/SYSTRAN/faster-whisper)
- **Silero VAD** by Silero AI (https://github.com/snakers4/silero-vad)


## License
MIT — feel free to clone, modify, and build your own voice companion.


