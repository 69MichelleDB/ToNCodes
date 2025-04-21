import Globals as gs
import asyncio
import websockets
import json
from time import sleep
from Tools.errorHandler import ErrorLogging
import logging
import os
import enum
import typing

# region Websocket Client

class ClientStatus(enum.IntEnum):
    CLIENT_UNKNOWN = 0
    CLIENT_CONNECTED = 5
    CLIENT_READY = 10
    CLIENT_PLAYING = 20
    CLIENT_GOAL = 30

class Version():
    def __init__ (self, i_ver : str):
        numbers = i_ver.split('.')
        self.major = numbers[0]
        self.minor = numbers[1]
        self.build = numbers[2]

    def toDict(self) -> str:
        return {'major': self.major, 'minor': self.minor, 'build': self.build, 'class': 'Version'}

def get_unique_identifier():
    import uuid
    uuid = uuid.getnode()
    return uuid


_tags = ['AP']
_item_handling = 0b001
_slot_data = True
_version = Version(gs._AP_VERSION).toDict()

stop_event = asyncio.Event()

def StartAP(i_path, i_server, i_slot, i_pass):
    asyncio.run(ConnectAP(i_path, i_server, i_slot, i_pass))

async def ConnectAP(i_path, i_server, i_slot, i_pass):
    try:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=os.path.join(i_path, 'log.txt'), 
            filemode='a'
        )

        url = f"wss://{i_server}"                           # Fix this, verify that it's built properly
        async with websockets.connect(url) as websocketAP:
            stop_event.clear()
            while not stop_event.is_set():
                try:
                    inMessage = await asyncio.wait_for(websocketAP.recv(), timeout=1)
                    logging.debug(inMessage)
                    messagejson = json.loads(inMessage)

                    packageRecv = messagejson[0]['cmd']
                    
                    match packageRecv:
                        case "RoomInfo":
                            print('First ping to the server, send GetDataPackage')
                            await SendMessageAsync(websocketAP, "GetDataPackage",{})
                    
                        case "DataPackage":
                            print('Attempting to Connect')
                            messageConnect = {
                                #'cmd': 'Connect',
                                'password': i_pass, 'game': 'Terrors of Nowhere', 'name': i_slot,
                                'version': _version,
                                'tags': _tags, 'items_handling' : _item_handling,
                                'uuid': get_unique_identifier(), "slot_data": _slot_data,
                            }
                            await SendMessageAsync(websocketAP, "Connect",messageConnect)
                            #await websocketAP.send(json.dumps(messageConnect)) 

                        case "ConnectionRefused":
                            print("Failed to connect")

                        case "Connected":
                            print("Connected to the server")


                except asyncio.TimeoutError:
                    pass
            print("Closing AP websocket")
            await websocketAP.close()

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ConnectAP: {e}")

def stop_thread():
    stop_event.set()

# Send messages from ToNCodes to the Websocket server to communicate with tontrack.me
async def SendMessageAsync(websocket, i_head ,i_args):
    try:
        message = [{"cmd": i_head, **i_args}]                     # Build the message
        await websocket.send(json.dumps(message))               # And send it away
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in SendMessage: {e}")

# Since we need to send messages async, this function will do intermediary work
def SendWSMessage(i_event, i_args):
    asyncio.run(SendMessageAsync(i_event, i_args))

