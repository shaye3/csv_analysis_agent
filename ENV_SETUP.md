# Environment Setup for CSV Analysis Agent

## Setting up your `.env` file

1. Create a `.env` file in the project root directory
2. Add your environment variables:

```bash
# OpenAI API Key (required for LLM functionality)
OPENAI_API_KEY=your_actual_openai_api_key_here

# Optional: Default model to use
DEFAULT_MODEL=gpt-3.5-turbo

# Optional: Default temperature setting  
DEFAULT_TEMPERATURE=0.1

# Optional: Enable verbose logging
VERBOSE=false
```

## Getting an OpenAI API Key

1. Go to [OpenAI's website](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to the API section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

## Verification

To verify your setup works:

```bash
# Test the CLI
python app/main.py info sample_data.csv

# Test with interactive mode (requires API key)
python app/main.py interactive --csv sample_data.csv
```

## Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Keep your API key secure and rotate it regularly

## Alternative Setup

You can also set environment variables directly:

```bash
export OPENAI_API_KEY="your_key_here"
python app/main.py interactive --csv sample_data.csv
``` 