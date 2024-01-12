import re
from openai import OpenAI
from dotenv import load_dotenv
from telepot import Bot
import os
from chatBot.constants import PROJECT_ROOT_PATH


load_dotenv()

def getSystemPrompt():
    finalPrompt=""
    with open(PROJECT_ROOT_PATH/"DB"/"BotBehaviour.txt", "r") as file:
        finalPrompt+= file.read()
    finalPrompt+="\n"  
    # with open(PROJECT_ROOT_PATH/"DB"/"ServiceDetails.txt", "r") as file:
    #     finalPrompt+= file.read()
    return finalPrompt

def getCommunicationRules():
    return """At the end of Reply, request for my remaining details ( Name, Age, Height, Weight, Phone number). Please request one piece of information at a time. after collecting all details force to complete the payment
""".strip()

def getInitialStaticChat():
    return [{"role": "system", "content": getSystemPrompt()}, {
        "role": "user", "content": "Hii"}]

class Response:
    def __init__(self):
        self.Model = OpenAI(base_url="http://localhost:8001/v1",
               api_key="BridgeSkillz_BikramProject")
        self.Bot = Bot(os.environ["client_tele_bot_token"])
    
    def getResponseFromLLM(self,userid,ChatHistory):
        ChatHistory = getInitialStaticChat()+[{'role':x['role'],'content':x['content']} for x in ChatHistory]
        ChatHistory[-1]['content']+=f"({getCommunicationRules()})"
        Reply=""
        line=""

        Response = self.Model.chat.completions.create(
            model="local-model",
            stream=True,
            messages=ChatHistory,
            temperature=0.7,
        )
        try:
            for partial in Response:
                Response = partial.choices[0].delta.content or ""
                print(Response,end="",flush=True)
                line+=Response
                line=line.replace("Rs.","Rs ").replace('Understood,',"")

                if ". " in line:
                    comp=re.split(r'(?<!Rs)\. ', re.sub(r'\([^)]*\)', '', line))[0]
                    # print("[FS]",comp)
                    if comp.strip():
                        self.Bot.sendMessage(userid, comp+".")
                        line=". ".join(line.split(". ")[1:]).strip()
                if "\n" in line:
                    comp=line.split("\n")[0]
                    # print("[NL]",comp)
                    if comp.strip():
                        self.replyToUserWithUserid(userid,comp)
                        line="\n".join(line.split("\n")[1:]).strip()

                Reply+=re.sub(r'\([^)]*\)', '', Response)
            if line.strip():
                self.replyToUserWithUserid(userid,line)
        except Exception as e:
            print(f"[+] Error : {e}")
        return Reply
    
    def replyToUserWithUserid(self,userid,msg):
        try:
            if msg:
                self.Bot.sendMessage(userid, re.sub(r'\([^)]*\)', '', msg))
        except Exception as e:
            print(f"[+] Sending Msg Error : {e}")


    
    def getFollowUpFromLLM(self,userid,ChatHistory,internalPrompt):
         ChatHistory=ChatHistory+[{"role": "user", "content": internalPrompt}]
         return self.getResponseFromLLM(userid,ChatHistory)