# OpenAI Automation Finance

## Project Structure

- `answers.py`: Core financial calculation functions.
- `generate_questions.py`: Functions to generate finance questions and expected answers.
- `run_ai_tests.py`: Script to run AI models on generated questions and compare their answers.
- `requirements.txt`: Python dependencies.

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Set up your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

- To generate and test AI answers to finance questions, run:
  ```
  python run_ai_tests.py
  ```
  This will generate questions, run them through selected AI models, and save results to `ai_responses.json`.
