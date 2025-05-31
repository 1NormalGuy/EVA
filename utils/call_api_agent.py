import requests
import time
import json
import os
import base64
import cv2
from typing import Dict, Union, List, Any, Optional

API_KEYS = {
   # FILL HERE
}

def encode_image(image_path):
    if not os.path.exists(image_path):
        print(f"错误: 图像文件不存在: {image_path}")
        return None

    try:
        img = cv2.imread(image_path)
        retval, buffer = cv2.imencode('.jpg', img)
        img_str = base64.b64encode(buffer).decode('utf-8')
        return img_str
    except Exception as e:
        print(f"图像编码失败: {e}")
        return None

def call_api_vllm(api, model, text_content, image_path=None, image_base64=None, 
                 system_prompt="a helpful assistant", generation_args={}, max_retries=3):
    if image_path and not image_base64:
        image_base64 = encode_image(image_path)
        if not image_base64:
            print("图像处理失败，无法继续API调用")
            return None
    
    if api == 'zhipu' or api == 'zp':
        try:
            from zhipuai import ZhipuAI
            
            client = ZhipuAI(api_key=API_KEYS['zhipu'])
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到智谱API，模型: {model}")
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": text_content},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]}
                    ]
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=generation_args.get("max_tokens", 512),
                        temperature=generation_args.get("temperature", 0.7)
                    )
                    
                    return response.choices[0].message.content
                    
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
            
            print("智谱API多次请求失败")
            return None
            
        except ImportError:
            print("智谱AI库未安装，请使用 'pip install zhipuai' 安装")
            return None
    
    elif api == 'openai':
        try:
            from openai import OpenAI
            
            api_key = API_KEYS["openai"]
            if not api_key or not api_key.startswith("sk-"):
                print("OpenAI API密钥格式错误或为空")
                return None
                
            client = OpenAI(api_key=api_key, base_url="https://4.0.wokaai.com/v1")
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到OpenAI API，模型: {model}")
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": text_content},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]}
                    ]
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=generation_args.get("max_tokens", 512),
                        temperature=generation_args.get("temperature", 0.7)
                    )
                    
                    print(f"Response type: {type(response)}")
                    
                    if isinstance(response, str):
                        print("API返回了字符串类型响应")
                        return response
                    else:
                        try:
                            response_summary = {
                                "choices": [{"message": {"content": response.choices[0].message.content[:100] + "..."}}]
                            }
                            print(f"Attempt {attempt + 1} - API Response:", json.dumps(response_summary, indent=4, ensure_ascii=False))
                            
                            return response.choices[0].message.content
                        except AttributeError as ae:
                            print(f"无法正常读取响应: {ae}")
                            print(f"响应内容: {response}")
                            if hasattr(response, "__str__"):
                                return str(response)
                            return None
                        
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
            
            print("OpenAI API多次请求失败")
            return None
            
        except ImportError:
            print("OpenAI库未安装，请使用 'pip install openai>=1.0.0' 安装")
            return None
    elif api == 'claude' or api == 'anthropic':
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=API_KEYS["anthropic"])
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到Claude API，模型: {model}")
                    
                    message = anthropic.Message(
                        role="user",
                        content=[
                            {
                                "type": "text",
                                "text": text_content
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    )
                    
                    response = client.messages.create(
                        model=model,
                        max_tokens=generation_args.get("max_tokens", 2048),
                        system=system_prompt,
                        messages=[message],
                        temperature=generation_args.get("temperature", 0.7)
                    )
                    
                    return response.content[0].text
                    
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
            
            print("Claude API多次请求失败")
            return None
            
        except ImportError:
            print("Anthropic库未安装，请使用 'pip install anthropic' 安装")
            return None

    elif api == 'qwen':
        try:
            from openai import OpenAI
            
            api_key = API_KEYS["qwen"]
            if not api_key or not api_key.startswith("sk-"):
                print("千问API密钥格式错误或为空")
                return None

            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到千问API (OpenAI兼容模式)，模型: {model}")

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": text_content},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]}
                    ]
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=generation_args.get("max_tokens", 512),
                        temperature=generation_args.get("temperature", 0.7)
                    )

                    return response.choices[0].message.content
                    
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    elif attempt == max_retries - 1:
                        error_msg = f"API调用失败: {str(e)}"
                        print(error_msg)
                        return error_msg
            
            error_msg = "千问API多次请求失败"
            print(error_msg)
            return error_msg
            
        except ImportError:
            print("OpenAI库未安装，请使用 'pip install openai>=1.0.0' 安装")
            return None

    elif api == 'google' or api == 'gemini':
        try:
            import google.generativeai as genai
            from PIL import Image
            import io
            import base64
            
            genai.configure(api_key=API_KEYS["google"])
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到Google API，模型: {model}")
                    
                    image_bytes = base64.b64decode(image_base64)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    generation_config = {
                        "temperature": generation_args.get("temperature", 0.7),
                        "top_p": generation_args.get("top_p", 1.0),
                        "top_k": generation_args.get("top_k", 32),
                        "max_output_tokens": generation_args.get("max_tokens", 2048),
                    }
                    
                    model_obj = genai.GenerativeModel(
                        model_name=model,
                        generation_config=generation_config,
                        system_instruction=system_prompt
                    )

                    response = model_obj.generate_content([text_content, image])
                    
                    return response.text
                    
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
            
            print("Google API多次请求失败")
            return None
            
        except ImportError:
            print("Google Generative AI库未安装，请使用 'pip install google-generativeai' 安装")
            return None

    elif api in ['ui-tars', 'seeslick', 'os-atlas']:
        host = generation_args.get("host", "127.0.0.1")
        port = generation_args.get("port", "8006")  
        timeout = generation_args.get("timeout", 30)
        
        api_url = f"http://{host}:{port}/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json"
        }
        messages = [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_content
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": generation_args.get("max_tokens", 1024),
            "temperature": generation_args.get("temperature", 0.2)
        }
        
        if api == 'os-atlas' and generation_args.get("gui_agent_mode") == "multi_step":
            data["mode"] = "multi_step"

        for attempt in range(max_retries):
            try:
                print(f"发送请求到 {api} API，模型: {model}")
                
                response = requests.post(api_url, headers=headers, json=data, timeout=timeout)

                if response.status_code == 200:
                    try:
                        return response.json()["choices"][0]["message"]["content"]
                    except (KeyError, IndexError) as e:
                        print(f"解析响应失败: {e}")
                        print(f"原始响应: {response.text}")
                        if attempt == max_retries - 1:
                            return f"响应解析错误: {str(e)}"
                else:
                    print(f"API错误: {response.status_code} - {response.text}")
                    if attempt == max_retries - 1:
                        return f"API错误: {response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1})")
                if attempt == max_retries - 1:
                    return "API请求超时"
            except Exception as e:
                print(f"尝试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                elif attempt == max_retries - 1:
                    return f"API调用失败: {str(e)}"
        
        return "所有请求尝试失败"

    else:
        print(f"不支持的API类型: {api}")
        return None