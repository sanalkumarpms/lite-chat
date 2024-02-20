# Prerequisites
Dependencies needed for this application can be installed by running the following commands:
- pip install flask
- pip install tiktoken

# Install instructions
1) Git clone the repository (git clone https://github.com/sanalkumarpms/lite-chat.git)
2) Run chat.py (python chat.py). The chat aplication can be access from the URL: http://127.0.0.1:5000
3) Update the gpt model configuration from the settings dialog
   - For each model, update the deployment URL (format: https://\<res-url\>.openai.azure.com/openai/deployments/\<deployment\>/chat/completions?api-version=\<version\>) and API Key.
