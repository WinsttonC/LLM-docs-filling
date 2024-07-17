import os
import warnings

from dotenv import load_dotenv
from langchain_community.chat_models.gigachat import GigaChat

load_dotenv()

warnings.filterwarnings("ignore")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")
BATCH_SIZE = 4

chat = GigaChat(
    credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False, streaming=True
)  # model='GigaChat-Pro'
