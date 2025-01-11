import urequests
import ujson

class OpenAI:
    def __init__(self, api_key, model="gpt-3.5-turbo", url="https://api.openai.com/v1/chat/completions"):
        self.api_key = api_key
        self.model = model
        self.url = url
        self.chat_history = []

    def chat(self, message, mode="new"):
        if mode == "continue" and self.chat_history:
            messages = self.chat_history + [{"role": "user", "content": message}]
        else:
            messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": message}]
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        response = urequests.post(self.url, data=ujson.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            self.chat_history = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return self.chat_history
        else:
            return f"Error: {response.status_code} - {response.text}"

class DeepSeek:
    def __init__(self, api_key, model="deepseek-chat", url="https://api.deepseek.com/chat/completions"):
        self.api_key = api_key
        self.model = model
        self.url = url
        self.chat_history = []
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def chat(self, message, mode="continue"):
        if mode == "new":
            self.chat_history = []
            self.chat_history.append({"role": "system", "content": "You are a helpful assistant"})
            self.chat_history.append({"role": "system", "content": "Don't give me emoji."})

        self.chat_history.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": self.chat_history,
            "stream": False
        }
        

        response = urequests.post(self.url, data=ujson.dumps(payload), headers=self.headers)

        if response.status_code == 200:
            self.chat_history.append(ujson.loads(response.text)['choices'][0]['message'])
            print('Bot:')
            print(self.chat_history[-1]["content"])
            print('---------------------------')
        else:
            #print(f"Error: {response.status_code} - {response.text}")
            self.chat_history.pop()
            print('Fail, retry manually.')




  
