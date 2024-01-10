from chatBot.tele_bot.DBPipeline import DBInstance
from rich import print
import time
from datetime import datetime
from dotenv import load_dotenv
from telepot import Bot
import os
from chatBot.tele_bot.Response import Response
load_dotenv()

DATABASE:DBInstance = None
llmmodel = Response()
WAIT_FOR_RESPONSE = 30  # in Seconds
WAIT_FOR_FOLLOW_UP = 300  # in seconds
FOLLOW_UP_DURATIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # in days


def organize_conversation(messages):
    conversation = []
    current_role = None
    current_message = ""
    last_id = None

    for message in messages:
        role = message['role']
        content = message['content']
        message_id = message['id']
        created_on = message['createdon']
        tag = message['tag']

        if role == current_role:
            current_message += " " + content
            last_id = message_id
        else:
            if current_message:
                conversation.append({'id': last_id, 'role': current_role, 'content': current_message.strip(),
                                     'createdon': created_on, 'tag': tag})
            current_role = role
            current_message = content
            last_id = message_id

    if current_message:
        conversation.append({'id': last_id, 'role': current_role, 'content': current_message.strip(),
                             'createdon': created_on, 'tag': tag})

    return conversation


def compare_conversations(before, after):
    missing_ids = []
    updated_ids = []

    before_dict = {message['id']: message['content'] for message in before}
    after_dict = {message['id']: message['content'] for message in after}

    for message_id, content_before in before_dict.items():
        if message_id in after_dict:
            content_after = after_dict[message_id]
            if content_before.strip() != content_after.strip():
                updated_ids.append(message_id)
        else:
            missing_ids.append(message_id)

    return missing_ids, updated_ids


def get_content_by_id(messages, target_id):
    for message in messages:
        if message['id'] == target_id:
            return message['content']
    return None


def last_reply_timing(datetime_string):
    date_time_obj = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    time_difference_seconds = (current_time - date_time_obj).total_seconds()

    if time_difference_seconds < 86400:
        return int(time_difference_seconds), 0
    else:
        days = int(time_difference_seconds / 86400)
        seconds_remaining = int(time_difference_seconds % 86400)
        return days, seconds_remaining


def respond_for_query(userid, organized_chat_history):
    print("[+] Responding")
    username = DATABASE.get_username_by_userid(userid)
    response=llmmodel.getResponseFromLLM(userid,organized_chat_history)
    DATABASE.insertChatHistory(userid, username, 'assistant', response)


def take_follow_up(userid, organized_chat_history, prompt):
    username = DATABASE.get_username_by_userid(userid)
    response=llmmodel.getFollowUpFromLLM(userid,organized_chat_history,prompt)
    DATABASE.insertChatHistory(userid, username, 'assistant', response, tag='followup')


def main():
    global DATABASE
    DATABASE = DBInstance()
    print("[+] Starting Responding Script")
    while True:
        for userid in DATABASE.getUserIds():
            user_chat_history = DATABASE.getChatHistoryByUserID(userid)
            organized_chat_history = organize_conversation(user_chat_history)
            to_delete, to_update = compare_conversations(user_chat_history, organized_chat_history)

            for id in to_delete:
                DATABASE.deleteChatHistoryById(id)
            for id in to_update:
                DATABASE.updateChatHistoryContentById(id, get_content_by_id(organized_chat_history, id))

            final_response = organized_chat_history[-1]

            seconds, day = last_reply_timing(final_response['createdon'])
            print(final_response)
            if final_response['role'] == 'user':
                print(f"[+] Waiting for More Msgs : {WAIT_FOR_RESPONSE - seconds}")
                if seconds > WAIT_FOR_RESPONSE:
                    print(final_response)
                    respond_for_query(userid, organized_chat_history)
            elif final_response['role'] == 'assistant':
                if seconds > WAIT_FOR_FOLLOW_UP and 'followup' != final_response['tag']:
                    minutes = seconds / 60
                    prompt = f"In the last {minutes} minute{'s' if minutes > 1 else ''}, " \
                             f"I haven't been responsive or shown interest. " \
                             f"Please send a message to persuade me."
                    take_follow_up(userid, organized_chat_history, prompt)
                elif day in FOLLOW_UP_DURATIONS:
                    prompt = f"In the last {day} day{'s' if day > 1 else ''}, " \
                             f"I haven't been responsive or shown interest. " \
                             f"Please send a message to persuade me."
                    take_follow_up(userid, organized_chat_history, prompt)
                else:
                    if seconds > WAIT_FOR_FOLLOW_UP:
                        print(f"[+] Waiting for Follow-up Day {day}")
                    else:
                        print(f"[+] Waiting for Follow-up Second {WAIT_FOR_FOLLOW_UP - seconds}")

        time.sleep(1)


if __name__ == "__main__":
    main()
