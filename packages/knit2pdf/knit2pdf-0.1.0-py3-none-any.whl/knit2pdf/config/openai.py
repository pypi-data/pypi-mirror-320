import os
from openai import OpenAI

OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))