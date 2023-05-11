from chatbot import chatbot, save_conversation, restore_previous_conversation
import os
import socket
import threading

HEADER = 64 #check for this
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) # replace this with the server we're hosting on
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() -1}")

def send_response(response, conn, addr):
    message = response.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    '''
    getting videoID from the client side below
    '''
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        videoID = conn.recv(msg_length).decode(FORMAT)
    '''
    get summary using the videoIDand send it to the client
    query the database first -> if not found then run summarize function from summarize script
    '''


    restore_previous_conversation(addr, videoID)

    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            if msg == DISCONNECT_MESSAGE:
                connected = False
                ''' 
                store entire current messages object in databse 
                (indexed by addr, videoID) 
                using save_conversation(addr, videoID) function from chatbot script
                '''
                save_conversation(addr,videoID,msg)
            else:
                print(f"[{addr}]: {msg}")
                reply = chatbot(msg, addr, videoID)
                send_response(reply, conn, addr)
    
    conn.close()




print("[STARTING] server is starting...")
start()












messages = [
    {"role": "system", "content": "Hi, you're YT-GPT now. Your role is to answer questions ONLY from the text provided by the user. This text will be the transcript of a youtube video. First provide the summary of that video through that transcript and then answer the question according to that asked by the user. ALWAYS STAY IN CHARACTER. If user asks questions that are not related to the video or beyond the knowledge provided in the transcript, reply with, \"This question is beyond the scope of the video, please change your query. Thank you.\" And remember to stay in character! "},
]




# Change this code below by learning how JS and Python will interact without losing context and running the script again and again
while True:
    query = str(input())
    print("User: ", query)
    if query == "exit":
        break
    chatbot(query)
    print("AI: ", messages[len(messages)-1]["content"])

    