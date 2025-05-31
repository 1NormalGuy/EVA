import requests
import time
import json
import os
from typing import Dict, Union, List, Any, Optional
from openai import OpenAI

API_KEYS = {
    # FILL HERE
}

def call_api(api, model, content='', generation_args={}, max_retries=3):
    
    if api == 'zhipu' or api == 'zp':  
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEYS['zhipu']}",
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}], 
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                response_data = response.json()

                if "error" in response_data:
                    error_code = response_data["error"].get("code", "")
                    error_message = response_data["error"].get("message", "")
                    print(f"API Error {error_code}: {error_message}")

                    if error_code == "500":
                        print("服务器内部错误，等待 5 秒后重试...")
                        time.sleep(5)
                        continue
                    else:
                        return None

                if "choices" in response_data and len(response_data["choices"]) > 0:
                    if "message" in response_data["choices"][0] and "content" in response_data["choices"][0]["message"]:
                        return response_data["choices"][0]["message"]["content"]
            
            except Exception as e:
                print(f"尝试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)

        print("API 多次请求失败")
        return None

    elif api == 'openai':
        try:

            api_key = API_KEYS["openai"]
            if not api_key or not api_key.startswith("sk-"):
                print("OpenAI API密钥格式错误或为空")
                return None
            
            client = OpenAI(api_key=api_key, base_url="https://4.0.wokaai.com/v1")

            if isinstance(content, list) and all(isinstance(item, dict) and "role" in item for item in content):
                messages = content
            else:
                messages = [{"role": "user", "content": content}]
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到OpenAI API，模型: {model}")
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        **generation_args
                    )

                    response_summary = {
                        "choices": [{"message": {"content": response.choices[0].message.content[:] + "..."}}]
                    }
                    print(f"Attempt {attempt + 1} - API Response:", json.dumps(response_summary, indent=4, ensure_ascii=False))
                    
                    return response.choices[0].message.content
                    
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
            
            print("OpenAI API 多次请求失败")
            return None
            
        except ImportError:
            print("OpenAI库未安装或版本不兼容，请使用 'pip install --upgrade \"openai>=1.0.0\"' 安装")
            return None

    elif api == 'claude' or api == 'anthropic':
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=API_KEYS["anthropic"])
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到Claude API，模型: {model}")
                    response = client.messages.create(
                        model=model,
                        max_tokens=2048,
                        messages=[{"role": "user", "content": content}],
                        **generation_args
                    )

                    response_summary = {
                        "choices": [{"message": {"content": response.content[0].text[:100] + "..."}}]
                    }
                    print(f"Attempt {attempt + 1} - API Response:", json.dumps(response_summary, indent=4, ensure_ascii=False))
                    
                    return response.content[0].text
                    
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
            
            print("Claude API 多次请求失败")
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
            
            if isinstance(content, list) and all(isinstance(item, dict) and "type" in item for item in content):
                messages = [{"role": "user", "content": content}]
            else:
                messages = [{"role": "user", "content": content}]
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到千问API (OpenAI兼容模式)，模型: {model}")
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        **generation_args
                    )
                    
                    response_summary = {
                        "choices": [{"message": {"content": response.choices[0].message.content[:100] + "..."}}]
                    }
                    print(f"Attempt {attempt + 1} - API Response:", json.dumps(response_summary, indent=4, ensure_ascii=False))
                    
                    return response.choices[0].message.content
                    
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
            
            print("千问API 多次请求失败")
            return None
            
        except ImportError:
            print("OpenAI库未安装或版本不兼容，请使用 'pip install --upgrade \"openai>=1.0.0\"' 安装")
            return None

    elif api == 'google' or api == 'gemini':
        try:
            import google.generativeai as genai
            genai.configure(api_key=API_KEYS["google"])
            
            for attempt in range(max_retries):
                try:
                    print(f"发送请求到Google API，模型: {model}")
                    model_obj = genai.GenerativeModel(model)
                    response = model_obj.generate_content(content)
                    
                    response_summary = {
                        "choices": [{"message": {"content": response.text[:] + "..."}}]
                    }
                    print(f"Attempt {attempt + 1} - API Response:", json.dumps(response_summary, indent=4, ensure_ascii=False))
                    
                    return response.text
                    
                except Exception as e:
                    print(f"尝试 {attempt + 1} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
            
            print("Google API 多次请求失败")
            return None
            
        except ImportError:
            print("Google Generative AI库未安装，请使用 'pip install google-generativeai' 安装")
            return None
    
    else:
        print(f"不支持的API类型: {api}")
        return None

