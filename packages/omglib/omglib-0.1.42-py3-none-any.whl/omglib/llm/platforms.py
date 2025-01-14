from openai import OpenAI as _OPENAI
from .beta.workers import wmap
from mistralai import Mistral
import cohere
import requests


class OpenAI:
    default_model = "gpt-4o-mini"
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.client = _OPENAI(api_key=api_key)
        self.model=OpenAI.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat.completions.create(messages=self.messages,tools=tools,tool_choice='auto',model=self.model).choices[0].message

class CloudFlare:
    default_model = wmap.models.LLAMA_31_70B_INSTRUCT
    def __init__(self,account_id:str,api_key):
        self.api_key = api_key
        self.account_id = account_id
        self.client = _OPENAI(api_key=api_key,base_url=f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1")
        self.model=CloudFlare.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat.completions.create(messages=self.messages,tools=tools,tool_choice='auto',model=self.model).choices[0].message

class Groq:
    default_model = "llama-3.1-70b-versatile"
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.client = _OPENAI(api_key=api_key,base_url=f"https://api.groq.com/openai/v1")
        self.model=Groq.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat.completions.create(messages=self.messages,tools=tools,tool_choice='auto',model=self.model).choices[0].message


class TogetherAI:
    default_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.client = _OPENAI(api_key=api_key,base_url=f"https://api.together.xyz/v1")
        self.model=TogetherAI.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat.completions.create(messages=self.messages,tools=tools,tool_choice='auto',model=self.model).choices[0].message


class AvianAI:
    default_model = "Meta-Llama-3.3-70B-Instruct"
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.client = _OPENAI(api_key=api_key,base_url=f"https://api.avian.io/v1")
        self.model=AvianAI.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat.completions.create(messages=self.messages,tools=tools,tool_choice='auto',model=self.model).choices[0].message


class Cohere:
    default_model = "command-r-plus"
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.client = cohere.ClientV2(api_key=api_key)
        self.model=Cohere.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat(messages=self.messages,tools=tools,model=self.model).message
    

class Mistral:
    default_model = "mistral-large-latest"
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.client = Mistral(api_key=api_key)
        self.model=Mistral.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat.complete(messages=self.messages,tools=tools,tool_choice='any',model=self.model).choices[0].message


class OpenRouter:
    default_model = "google/gemini-2.0-flash-exp:free"
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.client = _OPENAI(api_key=api_key,base_url="https://openrouter.ai/api/v1")
        self.model=OpenRouter.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat.completions.create(messages=self.messages,tools=tools,tool_choice='auto',model=self.model).choices[0].message

class Gemini:
    default_model = "models/gemini-2.0-flash-exp"
    def __init__(self,api_key:str):
        self.api_key = api_key
        self.client = _OPENAI(api_key=api_key,base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.model=Gemini.default_model
        self.messages = []
    def add_message(self,role:str,content:str):
        self.messages.append({'role':role,'content':content})
    def request(self,tools=[]):
        return self.client.chat.completions.create(messages=self.messages,tools=tools,tool_choice='auto',model=self.model).choices[0].message

