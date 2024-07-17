from prompts import extraction_prompt
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
from dotenv import load_dotenv
load_dotenv()
warnings.filterwarnings("ignore")


GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET_B64")

chat = GigaChat(
    credentials=GIGACHAT_CLIENT_SECRET, verify_ssl_certs=False
)  # model='GigaChat-Pro'

def find_fields(prompt):
    messages = [SystemMessage(content=extraction_prompt)]
    messages.append(HumanMessage(content=input_text))
    res = chat(messages)