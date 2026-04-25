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
- **Keep it modular.** Within reason, each component should be able to run independently for testing and development purposes.
- **Simple & Working > Complex & Broken.** I want to have a functional version of the project as soon as possible, and then build on it from there.
- **Leading from that, clarity > cool tricks.**  I want my code to be easy to understand and follow. 


## Features
- **LLM-based Dialogue** using Ollama. (configurable system prompt)
- **JSON-based Conversation Memory** to keep context during interactions.
- **YAML-based Config** for personality configuration.
- ~~**Voice Generation** via GPT-SoVITS API~~
- ~~**Speech Recognition** using Faster-Whisper~~ 

Voice Generation and Speech Recognition are currently removed, and scheduled for re-implementation.

JSON-based Conversation Memory is a placeholder, and will be replaced with a more robust solution like a vector database.


## Configuration
All prompts and parameters are stored in `character_config.yaml`.

You can define personalities by modifying the config file.


## Setup

### Install Dependencies
need to write this out at a later time, cba rn


## Usage

### 1. Run the main script:

```bash
python main.py
```

Each module is technically designed to be capable of independent operation, mostly for testing purposes, but the main 
script will run the full application, and is the recommended way to experience the full functionality of the project.

The flow:

Currently...
1. Takes in a user input from the console
2. Passes it to LLM model (with history)
3. Generates a response
4. Prints the output back to the console

Old flow:
1. ~~Riko listens to your voice via microphone (push to talk)~~
2. ~~Transcribes it with Faster-Whisper~~
3. ~~Passes it to GPT (with history)~~
4. ~~Generates a response~~
5. ~~Synthesizes Riko's voice using GPT-SoVITS~~
6. ~~Plays the output back to you~~


## TODO / Future Improvements
My own to-do list:
* [x] Remove all the external API calls and make everything run locally
* [x] Reorganise code structure, with better modularity and separation of concerns
* [ ] Replace JSON-based conversation memory with a vector database (probably ChromaDB)
* [ ] Re-implement voice generation and speech recognition modules (need to research locally-hostable options)
* [ ] Implement a dynamic emotional modelling system to hook into the LLM and voice synthesis, to allow for more 
expressive and emotionally varied responses.

From the original project:
* [ ] GUI or web interface
* [ ] Live microphone input support
* [ ] ~~Emotion or tone control in speech synthesis~~ (edited and yoinked over to my own to-do list)
* [ ] VRM model frontend


## Credits
- Just Rayen's original Project Riko
- Ollama for the local LLM hosting solution


## License
MIT — feel free to clone, modify, and build your own voice companion.


