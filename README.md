# PromptTune

A Flask-based web application that generates AI prompts using Claude 3.7 Sonnet. This tool helps users create effective prompts for various tasks.

## Features

- **Prompt Generation**: Generate AI prompts based on user-defined tasks
- **Thinking Mode**: Option to use Claude's thinking mode for more detailed prompt generation
- **Real-time Updates**: Server-sent events for live status updates during prompt generation
- **Modern UI**: Clean and intuitive web interface

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- Anthropic API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd prompt_gen
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file in the root directory and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask application:
```bash
poetry run python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:61188
```

3. Use the web interface to:
   - Generate prompts by entering your task description
   - Toggle thinking mode for more detailed prompt generation

## Project Structure

```
prompt_gen/
├── app.py              # Main Flask application
├── core/               # Core functionality
│   ├── llmservice.py   # LLM service implementation
│   ├── model_config.py # Model configuration
│   ├── tools.py        # Utility tools
│   └── prompt/         # Prompt templates and logic
├── templates/          # HTML templates
├── poetry.lock         # Poetry dependency lock file
├── pyproject.toml      # Poetry project configuration
└── .env               # Environment variables
```

## API Endpoints

- `GET /`: Main application page
- `GET /generate-prompt`: Generate a prompt based on task description
- `GET /health`: Health check endpoint

## Development

The project uses Poetry for dependency management. To add new dependencies:

```bash
poetry add package_name
```

## Testing

Run the smoke test to verify basic functionality:

```bash
poetry run python offline_smoke_test.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Acknowledgments

- Built with Flask
- Powered by Claude 3.7 Sonnet
- Uses Poetry for dependency management 