from flask import Flask, render_template, request, jsonify
import requests
import tiktoken
import json

chatbot = Flask(__name__) 
modelConfig = None

@chatbot.route('/model-config', methods=['GET'])
def get_model_config():
   global modelConfig
   if modelConfig is None:
      with open('model.config', 'r') as file:
         modelConfigStr = file.read()
         modelConfig = json.loads(modelConfigStr)
         print("Loaded model config from file")
   else:
      modelConfigStr = json.dumps(modelConfig)
   return modelConfigStr, 200

@chatbot.route('/model-config', methods=['POST'])
def set_model_config():
   global modelConfig
   modelConfigStr = request.get_data(as_text=True)
   modelConfig = json.loads(modelConfigStr)
   with open('model.config', 'w') as f:
      f.write(modelConfigStr)
   return jsonify({"status": "success"}), 200

def getModeInformation(model):
   global modelConfig
   get_model_config()
   
   if model == "GPT-3.5-turbo":
      gpt_config = next((item for item in modelConfig if item['name'] == 'gpt35'), None)
      url = gpt_config['url']
      api_key = gpt_config['key']
   if model == "GPT4":
      gpt_config = next((item for item in modelConfig if item['name'] == 'gpt4'), None)
      url = gpt_config['url']
      api_key = gpt_config['key']
   if model == "GPT4-turbo":
      gpt_config = next((item for item in modelConfig if item['name'] == 'gpt4t'), None)
      url = gpt_config['url']
      api_key = gpt_config['key']
   if model == "GPT4 Vision":
      gpt_config = next((item for item in modelConfig if item['name'] == 'gpt4v'), None)
      url = gpt_config['url']
      api_key = gpt_config['key']
   return url, api_key

def num_tokens_from_string(string: str, encoding_name: str) -> int:
   encoding = tiktoken.get_encoding(encoding_name)
   num_tokens = len(encoding.encode(string))
   return num_tokens

@chatbot.route('/chat', methods=['POST'])
def chat():
   data = request.get_json()
   
   model = data['model']
   if model == "Other":
      url =  data['otherResourceURL']
      api_key =  data['otherApiKey']
   else:
      url, api_key = getModeInformation(model)

   prompt = data['prompt'].strip()
   context = data['context'].strip()
   examples = data['examples']
   examples_json = None
   if examples:
      examples = examples.strip()
      try:
         examples_json = json.loads(examples)
      except json.JSONDecodeError:
         print("Failed to decode the example string into JSON")
      except Exception as e:
         print(f"An unexpected error occurred: {e}")

   history = data['history']
   question = data['question'].strip()
   temperature = float(data['temperature'])
   topP = float(data['topP'])
   maxTokens = int(data['maxTokens'])
   frequencyPenalty = float(data['frequencyPenalty'])
   presencePenalty = float(data['presencePenalty'])
   stop = data['stop']
   
   headers = {
    "Content-Type": "application/json",
    "api-key": api_key,
   }
   messages = []
   messages.append({"role": "system", "content": prompt + "\n" + context})
   if examples_json:
      for example in examples_json:
         messages.append(example)
   if history:
      for entry in history:
         messages.append({"role": entry["role"], "content": entry["content"]})
   messages.append({"role": "user", "content": question})
   data_json = {
         "messages": messages,
         "max_tokens": maxTokens,
         "temperature": temperature,
         "frequency_penalty": frequencyPenalty,
         "presence_penalty": presencePenalty,
         "top_p": topP,
         "stop": stop
   }
   
   response = requests.post(url, headers=headers, json=data_json)
   response_json = response.json()
   if 'error' in response_json:
      return jsonify({'error': response_json['error']['message']}), 400
   
   model_response = response_json['choices'][0]['message']['content']
   total_tokens = num_tokens_from_string(str(data_json) + model_response, "cl100k_base")
   return jsonify({'response': model_response, 'total_tokens': total_tokens}), 200

@chatbot.route('/')       
def index(): 
   return render_template("index.html") 
  
if __name__=='__main__': 
   chatbot.debug = True
   chatbot.run()
