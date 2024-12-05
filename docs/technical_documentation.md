# Technical Documentation

## Overview

This project is an AI agent that calls and talks with leads. It uses Rasa for natural language understanding and dialogue management, SignalWire for telephony integration, and various other tools for audio processing and state management.

## Project Structure

## Key Components

### 1. `actions/`

#### `actions.py`

Contains custom actions for the Rasa chatbot.

### 2. `agent/`

#### `cold_call_agent.py`

Handles telephony integration, audio processing, and interaction with SignalWire.

- `play_audio_from_s3(file_name)`: Plays an audio file from S3 using Vocode.
- `synthesize_speech(text, output_file)`: Synthesizes speech using gTTS.
- `transcribe_audio(audio_file)`: Transcribes audio using OpenAI Whisper.
- `initiate_call(to_phone_number)`: Initiates a call using SignalWire.
- `handle_voice_request()`: Handles the initial voice request using Vocode.
- `handle_conversation()`: Handles the conversation using Rasa.
- `main()`: Main function to run the cold call agent.

#### `tree.py`

Defines the conversation tree and response options.

- `create_service_options()`: Creates options for different services.
- `create_device_options()`: Creates options for different devices.
- `create_industry_response()`: Creates responses for different industries.
- `create_project_response()`: Creates responses for project-related questions.

### 3. `config/`

#### `endpoints.yml`

Configures endpoints for the Rasa server and telephony integration with SignalWire.

#### `credentials.yml`

Stores credentials for external services (if needed).

### 4. `data/`

#### `nlu.yml`

Contains NLU training data.

#### `stories.yml`

Contains stories for training the dialogue management model.

#### `rules.yml`

Contains rules for deterministic conversation paths.

### 5. `models/`

Stores trained models.

### 6. `scripts/`

#### `main.py`

Main script for running the AI agent.

### 7. `tests/`

#### `test_actions.py`

Contains unit tests for custom actions.

#### `test_main.py`

Contains unit tests for the main script.

#### `test_nlu.yml`

Contains test data for NLU.

#### `test_stories.yml`

Contains test stories for dialogue management.

#### `test_upload_to_s3.py`

Contains tests for uploading audio files to S3.

### 8. `domain.yml`

Defines the domain of the assistant, including intents, entities, slots, responses, actions, and forms.

### 9. `config.yml`

Configures the NLU pipeline and dialogue management policies.

### 10. `requirements.txt`

Lists the dependencies required for the project.

## Setup and Installation

1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd my_ai_agent_project
   ```
