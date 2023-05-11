from summarize import summarize
from bottle import Bottle, post, request, run, response, static_file, route, abort
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket
from chatting import get_response
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json, os

app = Bottle()

uri = "mongodb+srv://YTgpt:YTgpt16@cluster0.38q95ct.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tls=True, tlsAllowInvalidCertificates=True)


db = client['YTgptdb']
gpt_collection = db['Collectgpt']


def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors


client_dict = {}
@app.route('/checkHistory', method=['OPTIONS', 'POST'])
@enable_cors
def checkHistory():
    videoId = request.json.get('videoId')
    userId = request.json.get('userId')
    if not (videoId and userId):
        print('No video id or userId')
        response.status = 500
        return 'Internal server error\n'
    try: 
        query = {"userId": userId, 'videoId': videoId}
        result = gpt_collection.find_one(query)
        if result is not None:
            response.status = 200
            messages = result['messages']
            ##sending previous conversation to user
            return messages
        else:
            response.status = 201
            return []
    except Exception as e:
        print(e)
        response.status = 500
        return 'Internal server error\n'
    

@app.route('/test', method=['OPTIONS', 'GET'])
@enable_cors
def test():
    return "Hello World";
     


@app.route('/websocket/', apply=[websocket])
def handle_websocket(client_socket):
    # client_socket = request.environ.get('wsgi.websocket')  # type:WebSocket
    if not client_socket:
        abort(400, 'Expected WebSocket request.')
    message_from_client = client_socket.receive()

    userId = json.loads(message_from_client).get('userId')
    client_dict[userId] = client_socket
    videoId = json.loads(message_from_client).get('videoId')
    messages = []
    print(f'{userId}  {videoId}')

    # get messages from dB (userId, videoId) else initiate messages by default value
    try:
        query = {"userId": userId, 'videoId': videoId}
        result = gpt_collection.find_one(query)
        if result is not None:
            messages = result['messages']
            ##sending previous conversation to user
            #client_socket.send(messages)
        else:
            messages = [
                {"role": "system", "content": "Hi, you're YT-GPT now. Your role is to answer questions ONLY from the text provided by the user. This text will be the transcript of a youtube video. First provide the summary of that video through that transcript and then answer the question according to that asked by the user. ALWAYS STAY IN CHARACTER. If user asks questions that are not related to the video or beyond the knowledge provided in the transcript, reply with, \"This question is beyond the scope of the video, please change your query. Thank you.\" And remember to stay in character! "},
                ]
    except Exception as e:
        print(e)
        messages = [
            {"role": "system", "content": "Hi, you're YT-GPT now. Your role is to answer questions ONLY from the text provided by the user. This text will be the transcript of a youtube video. First provide the summary of that video through that transcript and then answer the question according to that asked by the user. ALWAYS STAY IN CHARACTER. If user asks questions that are not related to the video or beyond the knowledge provided in the transcript, reply with, \"This question is beyond the scope of the video, please change your query. Thank you.\" And remember to stay in character! "},
        ]

    #assuming summary will be there in the database, as the first request will be fore summary before the user starts asking questions
    summary = gpt_collection.find_one({'videoId': videoId})["Summary"]
    messages.append({
        "role": "system", "content": "Here is the summary of the video you'll build your current context upon\n"+summary
    })

    while True:
        try:
            message_from_client = client_socket.receive()
            if message_from_client:
                message = json.loads(message_from_client).get('message')
                messages, response = get_response(messages, message)
                print("AI: ", response)
                client_socket.send(response)

        except Exception as e:
            print(e)
            # store current messages[] in dB (userId, videoId)
            try:
                document = {"userId": userId, "videoId": videoId, "messages": messages}
                gpt_collection.insert_one(document)
            except Exception as e:
                print("Error while storing data in database: ", e)
            break


@app.route('/api/v1/summarize', method=['OPTIONS', 'POST'])
@enable_cors
def post_summarize():
    videoId = request.json.get('videoId')
    if not videoId:
        print('No video id')
        response.status = 500
        return 'Internal server error\n'
    try:
        print(f'Received request to summarize "{videoId}"')
        if gpt_collection.find_one({'videoId': videoId}) is not None:
            print("summary found in database.")
            summary = gpt_collection.find_one({'videoId': videoId})["Summary"]
        else:
            summary = summarize(videoId)
            data = {
                "videoId": videoId,
                "Summary": summary.strip()
            }
            gpt_collection.insert_one(data)

    except Exception as e:
        print(e)
        response.status = 500
        return 'Internal server error\n'
    summary = summary.strip()
    summary, clickbait = summary.split('$')
    print(f'Summary of "{videoId}":\n{summary.strip()}')
    # Save summary in database against a videoId
    

    return {'summary': summary.strip(), 'clickbait': clickbait.strip()}


run(app, host='0.0.0.0', port=8080, server=GeventWebSocketServer)

# Create a api call for checking if the video is clickbait or not

# Create socket for chat feature


# print(summarize('juD99_sPWGU'))
# print(summarize('UIy-WQCZd4M'))
# print(summarize('-wIt_WsJGfw'))
# print(summarize('5eK5A_43pkE'))
