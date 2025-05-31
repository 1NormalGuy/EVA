import openai
import time
from queue import Queue
import requests
import json
from utils.format_tokens import *
from PIL import Image
import argparse
from utils.format_tokens import append_to_jsonl
from gradio_client import Client

openai_keys = [
    # FILL HERE
]
api_base_url = "https://api.openai.com/v1"

class API:
    def __init__(self,temperature = 0.0) -> None:
        self.t = temperature
        self.client = openai.OpenAI(api_key='', base_url=api_base_url)
        self.key_queue = Queue()
        for k in openai_keys:
            self.key_queue.put(k)

    def models(self):
        k = self.key_queue.get()
        self.client.api_key = k

        return self.client.models.list().data

    def ChatCompletion(self,model,messages,temperature=None,**kwargs) -> str:
        if temperature == None:
            temperature = self.t
        key = self.key_queue.get()

        retry_count = 3
        retry_interval = 0.5

        errormsg=''
        for _ in range(retry_count):
            try:
                self.client.api_key = key
                response = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=temperature,
                            **kwargs
                        )
                reply = response.choices[0].message.content
                if reply == '':
                    raise ValueError('EMPTY RESPONSE CONTENT')
                self.key_queue.put(key)
                return reply

            except (openai.RateLimitError,openai.APIError,openai.OpenAIError,openai.PermissionDeniedError) as e:
                if "quota" in e.message or "exceeded" in e.message or "balance" in e.message:
                    with open('RanOutKeys.txt','a') as f:
                        f.write(f'{key}\n')
                    key = self.key_queue.get()
                else:
                    errormsg=e
                    retry_interval *= 5
                    time.sleep(retry_interval)
            except (ValueError,Exception) as e:
                errormsg=e
                retry_interval *= 5
                time.sleep(retry_interval)
        self.key_queue.put(key)
        raise ConnectionError(f"ChatCompletion Retries Failure {key[-5:]}-{errormsg}")

    def dummyChat(self):
        key = self.key_queue.get()
        print(f"Dummy get [{key[-5:]}] at {time.time()}")
        self.key_queue.put(key)

class vllmAPI:
    def __init__(self, args) -> None:
        self.api_url = f"http://{args.host}:{args.port}/generate"

    def post_http_request(self, prompt, args) -> requests.Response:
        headers = {"User-Agent": "Test Client"}
        pload = {
            "prompt": prompt,
            "n": 1,
            "use_beam_search": False,
            "stop": ["<|im_end|>","</s>","[/INST]","<|user|>","<|assistant|>","<reserved_106>","<reserved_107>"],
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
        }
        response = requests.post(self.api_url, headers=headers, json=pload)
        return response
    
    def ChatCompletion(self, messages, args) -> str:
        if temperature == None:
            temperature = self.t
        if isinstance(messages,list) and isinstance(messages[0],dict):
            if 'yi' in args.model:
                prompt = format_tokens_yi(dialog=messages)
            elif 'mistral' in args.model or 'mixtral' in args.model:
                prompt = format_tokens_mistral(dialog=messages)
            elif 'phi' in args.model:
                prompt = format_tokens_phi(dialog=messages)
            elif 'chatglm' in args.model:
                prompt = format_tokens_chatglm(dialog=messages)
            elif 'qwen' in args.model:
                prompt = format_tokens_qwen(dialog=messages)
            elif 'baichuan2' in args.model:
                prompt = format_tokens_baichuan(dialog=messages)
            else:
                prompt = format_tokens_llama(dialog=messages)
        else:
            prompt = str(messages)
        for _ in range(3):
            response = self.post_http_request(prompt, args)
            if response.status_code == 200:
                reply = json.loads(response.content)["text"][0].removeprefix(prompt).strip()
                return reply
        raise ConnectionError('SERVER DO NOT RESPOND')

def local_generate_cogagent(prompt, image, args):
    client = Client("http://127.0.0.1:7860/")
    result = client.predict(
            prompt,	
            image,
            1,
            True,
            0.01,
            0,
            0,	
            1,
            0,	
            0,	
            0,	
            1,	
            0,	
            -5,
            True,
            "",	
            api_name="/textgen"
    )
    print(result[0])
    return result[0]

def local_generate_autoui(prompt, image, args):
    client = Client(f"http://127.0.0.1:{args.port}/")
    result = client.predict(
            prompt,	
            image,	
            1,	
            True,
            0.01,
            0,	
            0,	
            1,	
            0,
            0,	
            0,
            1,	
            0,
            -5,
            True,
            "",
            api_name="/textgen"
    )
    print(result[0])
    return result[0]

def local_generate_qwenvl(prompt, image, args):
    client = Client("http://127.0.0.1:7860/")
    result = client.predict(
            prompt,
            image,	
            1,	
            True,
            0.01,
            0,
            0,
            1,
            0,	
            0,	
            0,	
            1,
            0,	
            -5,
            True,
            "",
            api_name="/textgen"
    )
    print(result[0])
    return result[0]

def local_generate_yivl(prompt, image, args):
    client = Client("http://127.0.0.1:8111/")
    result = client.predict(
        prompt,
        image,
        "Crop",
        api_name="/add_text"
    )
    result = client.predict(
		0.2,
		0.7,
		128,
        api_name="/predict"
)
    print(result)
    return result[0]

def local_general_llava(data, args):
    pass

