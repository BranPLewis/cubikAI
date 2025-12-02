from smolagents import OpenAIServerModel
import os

def getenv(var:str)->str:
    return os.getenv(var)

def get_api_key(keyname):
    api_key = getenv(keyname)
    if not api_key:
        msg = (f"{keyname} not set. "
               f"Be sure .env has {keyname}. "
               f"Be sure dotenv.load_dotenv() is called at initialization.")
        raise ValueError(msg)
    return api_key

def google_build_reasoning_model(model_id = "gemini-2.5-flash"):
    key_name = "GEMINI_API_KEY"
    api_base = "https://generativelanguage.googleapis.com/v1beta/openai/"
    api_key = get_api_key(key_name)
    model = OpenAIServerModel(
        model_id = model_id,
        api_base = api_base,
        api_key = api_key,
        client_kwargs={"max_retries": 8})
    return model