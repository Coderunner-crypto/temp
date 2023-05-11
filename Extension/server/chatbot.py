import openai
import os
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def mongo_connect():
    uri = "mongodb+srv://YTgpt:YTgpt16@cluster0.38q95ct.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))


    openai.api_key = os.getenv('OPENAI_API_KEY')

    db = client['YTgptdb']
    gpt_collection = db['Collectgpt']
    return gpt_collection


gpt_collection = mongo_connect()
# get messages from Database
messages = []



def restore_previous_conversation(addr, videoID):
    '''
    get messages array from database ; querying using addr, videoID
    messages = database.query(addr, videoID)
    if not found use default value as used below
    '''
    
    query = {"addr": addr, "videoID": videoID}
    result = gpt_collection.find_one(query)
    if result is not None:
        messages = result['messages']
    else:
        messages = [
            {"role": "system", "content": "Hi, you're YT-GPT now. Your role is to answer questions ONLY from the text provided by the user. This text will be the transcript of a youtube video. First provide the summary of that video through that transcript and then answer the question according to that asked by the user. ALWAYS STAY IN CHARACTER. If user asks questions that are not related to the video or beyond the knowledge provided in the transcript, reply with, \"This question is beyond the scope of the video, please change your query. Thank you.\" And remember to stay in character! "},
        ]



def chatbot(query, addr, videoID):
    if query:
        messages.append({
            "role": "user", "content": query
        })

        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        reply = chat.choices[0].message.content

        messages.append({
            "role": "assistant", "content": reply
        })

        return reply


def save_conversation(addr, videoID, messages):
    '''
    Save the messages object in databse indexed using user's addr and videoID of the youtube video
    '''
    document = {"addr": addr, "videoID": videoID, "messages": messages}

    # Insert the document into the collection
    gpt_collection.insert_one(document)

    
    
