import Globals as gs
import asyncio
import websockets
import json
from time import sleep
from Tools.errorHandler import ErrorLogging
from Tools.fileTools import SaveJson
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


class Concepts(enum.IntEnum):
    terrors = 1
    alternates = 2
    unbounds = 3
    locations = 4
    moons = 5

class Moons(enum.IntEnum):
    MYSTIC = 1
    BLOOD = 2
    TWILIGHT = 3
    SOLSTICE = 4

class APwebsocketClient():

    def __init__(self, i_indexJson):
        self.indexJson = i_indexJson
        self.path = os.path.join(gs._FOLDER_AP, i_indexJson['folder'])          # Where the "save file" is going to be
        self.server = i_indexJson['server']     # AP url + port
        self.slot = i_indexJson['slotName']     # Player's name
        self.passw = i_indexJson['passw']       # Room's password

        self.tags = ['AP']          # Client's tags
        self.item_handling = 0b001  # How the client handles the items
        self.slot_data = True       # Receive data slot
        self.version = Version(gs._AP_VERSION).toDict()     # Current AP version
        self.timeout = 1            # Timeout the listener and do another loop after x seconds
        self.stop_event = asyncio.Event()                   # We'll use this to stop the clien from outside

        self.connectedInfo = None        # Will have the game's data

    async def Listen(self):
        self.stop_event.clear()
        while not self.stop_event.is_set():                  # This will allow us to stop it from outside
            try:
                inMessage = await asyncio.wait_for(self.websocketAP.recv(), timeout=self.timeout)
                gs.logger.info(inMessage)
                messagejson = json.loads(inMessage)

                packageRecv = messagejson[0]['cmd']
                
                match packageRecv:
                    # Sent to clients when they connect to an Archipelago server.
                    case "RoomInfo":
                        print('[AP] First ping to the server, send GetDataPackage')
                        await self.Send_GetDataPackage()

                    # Sent to clients to provide what is known as a 'data package' which contains information to enable a client
                    # to most easily communicate with the Archipelago server. Contents include things like location id to name mappings, among others
                    case "DataPackage":
                        print('[AP] Attempting to Connect')
                        await self.Send_Connect()

                    # Sent to clients when the server refuses connection. This is sent during the initial connection handshake.
                    case "ConnectionRefused":
                        print("[AP] Failed to connect")

                    # Sent to clients when the connection handshake is successfully completed.
                    case "Connected":
                        print("[AP] Connected to the server")
                        self.connectedInfo = messagejson[0].copy()
                        if len(self.connectedInfo['slot_data'])==0:
                            print('[AP]: No Slot Data received!')
                            gs.logger.debug('[AP Debug]: No Slot Data received!')

                    # Sent to clients when they receive an item.
                    case "ReceivedItems":
                        print("[AP] Received new items")

                    # Sent to clients to acknowledge a received LocationScouts packet and responds with the item in the location(s) being scouted.
                    case "LocationInfo":
                        print("[AP] Locations scouted")

                    # Sent when there is a need to update information about the present game session.
                    case "RoomUpdate":
                        print("[AP] Data may have changed in RoomInfo and/or Connected")

                    # ent to clients purely to display a message to the player. While various message types provide additional arguments,
                    # clients only need to evaluate the data argument to construct the human-readable message text. All other arguments may be ignored safely.
                    case "PrintJSON":
                        print("[AP] New message for the player")

                    # Sent to clients after a client requested this message be sent to them, more info in the Bounce package.
                    case "Bounced":
                        print("[AP] Someone requested a bounce")

                    # Sent to clients if the server caught a problem with a packet. This only occurs for errors that are explicitly checked for.
                    case "InvalidPacket":
                        print("[AP] Packet had an error")

                    # Sent to clients as a response the a Get package.
                    case "Retrieved":
                        print("[AP] Get response")

                    # Sent to clients in response to a Set package if want_reply was set to true, or if the client has registered to receive updates
                    # for a certain key using the SetNotify package. SetReply packages are sent even if a Set package did not alter the value for the key.
                    case "SetReply":
                        print("[AP] SetReply")


            except asyncio.TimeoutError:
                pass
        print("[AP]: Closing AP websocket")
        await self.websocketAP.close()

    # Starts the client and the logger
    async def ConnectAP(self):
        try:
            url = f"wss://{self.server}"                           # Fix this, verify that it's built properly
            async with websockets.connect(url) as websocket:
                self.websocketAP = websocket
                await self.Listen()

        except Exception as e:
            print(e)
            ErrorLogging(f"Error in ConnectAP: {e}")


    # region Send packages

    async def SendMessageAsync(self, i_head ,i_args):
        try:
            message = [{"cmd": i_head, **i_args}]                           # Build the message
            await self.websocketAP.send(json.dumps(message))                # And send it away
        except Exception as e:
            print(e)
            ErrorLogging(f"Error in SendMessage: {e}")


    async def Send_GetDataPackage(self):
        await self.SendMessageAsync("GetDataPackage",{})

    async def Send_Connect(self):
        messageConnect = {
            'password': self.passw, 'game': 'Terrors of Nowhere', 'name': self.slot,
            'version': self.version,
            'tags': self.tags, 'items_handling' : self.item_handling,
            'uuid': get_unique_identifier(), "slot_data": self.slot_data,
        }
        await self.SendMessageAsync("Connect", messageConnect)

    async def Send_LocationChecks(self, i_location: typing.List[int]):
        messageConnect = {
            'locations': i_location
        }
        await self.SendMessageAsync("LocationChecks", messageConnect)

    async def Send_StatusUpdate(self, i_statusUpd: ClientStatus):
        messageConnect = {
            'status' : i_statusUpd
        }
        await self.SendMessageAsync("StatusUpdate", messageConnect)


    # region Outside calls

    def stop_thread(self):
        self.stop_event.set()

    def StartAP(self):
        asyncio.run(self.ConnectAP())

    def UpdateJson(self):
        SaveJson(os.path.join(gs._FOLDER_AP, self.indexJson['folder'], gs._FILE_AP_INDEX), self.indexJson)

    def VerifyWin(self):
        if self.connectedInfo['slot_data']['nightmare_terrors_index_range']==len(self.indexJson['data'][Concepts.terrors.name]) and \
        self.connectedInfo['slot_data']['nightmare_alternates_index_range']==len(self.indexJson['data'][Concepts.alternates.name]) and \
        self.connectedInfo['slot_data']['nightmare_unbounds_index_range']==len(self.indexJson['data'][Concepts.unbounds.name]) and \
        self.connectedInfo['slot_data']['moon_index_range']==len(self.indexJson['data'][Concepts.moons.name]) and \
        self.connectedInfo['slot_data']['location_index_range']==len(self.indexJson['data'][Concepts.locations.name]):
            asyncio.run(self.Send_StatusUpdate(ClientStatus.CLIENT_GOAL))

    def MapReceived(self, i_map: int):
        if i_map not in self.indexJson['data']['locations'] and \
            self.connectedInfo['slot_data']['location_index_range']>len(self.indexJson['data'][Concepts.locations.name]):
            print(f"[AP]: map {i_map} added")
            self.indexJson['data']['locations'].append(i_map)
            count = 4000 + len(self.indexJson['data']['locations'])-1
            asyncio.run(self.Send_LocationChecks([count]))
            self.UpdateJson()
        else:
            print(f"[AP]: map {i_map} was already found")
        
        self.VerifyWin()

    def KillerReceived(self, i_killers: typing.List[int], i_type):
        print(f"[AP]: Killer {i_killers} {i_type} received, comparing")
        queue = {}
        if i_type in ['Classic','Fog','Punished','Sabotage','Cracked','Ghost']:
            if i_killers[0] not in self.indexJson['data'][Concepts.terrors.name] and \
            self.connectedInfo['slot_data']['nightmare_terrors_index_range']>len(self.indexJson['data'][Concepts.terrors.name]):
                queue[i_killers[0]] = Concepts.terrors
        elif i_type in ['Alternate', 'Fog (Alternate)', 'Ghost (Alternate)']:
            if i_killers[0] not in self.indexJson['data'][Concepts.alternates.name] and \
            self.connectedInfo['slot_data']['nightmare_alternates_index_range']>len(self.indexJson['data'][Concepts.alternates.name]):
                queue[i_killers[0]] = Concepts.alternates
        elif i_type == 'Unbound':
            if i_killers[0] not in self.indexJson['data'][Concepts.unbounds.name] and \
            self.connectedInfo['slot_data']['nightmare_unbounds_index_range']>len(self.indexJson['data'][Concepts.unbounds.name]):
                queue[i_killers[0]] = Concepts.unbounds
        elif i_type in ['Mystic Moon','Blood Moon','Twilight','Solstice']:
            if self.connectedInfo['slot_data']['moon_index_range']>len(self.indexJson['data'][Concepts.moons.name]):
                if i_type=='Mystic Moon' and Moons.MYSTIC.value not in self.indexJson['data'][Concepts.moons.name]:
                    queue[Moons.MYSTIC.value] = Concepts.moons
                if i_type=='Blood Moon' and Moons.BLOOD.value not in self.indexJson['data'][Concepts.moons.name]:
                    queue[Moons.BLOOD.value] = Concepts.moons
                if i_type=='Twilight' and Moons.TWILIGHT.value not in self.indexJson['data'][Concepts.moons.name]:
                    queue[Moons.TWILIGHT.value] = Concepts.moons
                if i_type=='Solstice' and Moons.SOLSTICE.value not in self.indexJson['data'][Concepts.moons.name]:
                    queue[Moons.SOLSTICE.value] = Concepts.moons
        elif i_type == 'Bloodbath':
            queue = {killer : Concepts.terrors for killer in i_killers if killer not in self.indexJson['data'][Concepts.terrors.name] and self.connectedInfo['slot_data']['nightmare_terrors_index_range']>len(self.indexJson['data'][Concepts.terrors.name])}
        elif i_type == 'Double Trouble':
            if i_killers[0] not in self.indexJson['data'][Concepts.terrors.name] and \
            self.connectedInfo['slot_data']['nightmare_terrors_index_range']>len(self.indexJson['data'][Concepts.terrors.name]):
                queue[i_killers[0]] = Concepts.terrors
            if i_killers[1] not in self.indexJson['data'][Concepts.terrors.name] and \
            self.connectedInfo['slot_data']['nightmare_terrors_index_range']>len(self.indexJson['data'][Concepts.terrors.name]):
                queue[i_killers[1]] = Concepts.terrors
        elif i_type == 'Midnight':
            if i_killers[0] not in self.indexJson['data'][Concepts.terrors.name] and \
            self.connectedInfo['slot_data']['nightmare_terrors_index_range']>len(self.indexJson['data'][Concepts.terrors.name]):
                queue[i_killers[0]] = Concepts.terrors
            if i_killers[1] not in self.indexJson['data'][Concepts.terrors.name] and \
            self.connectedInfo['slot_data']['nightmare_terrors_index_range']>len(self.indexJson['data'][Concepts.terrors.name]):
                queue[i_killers[1]] = Concepts.terrors
            if i_killers[2] not in self.indexJson['data'][Concepts.alternates.name] and \
            self.connectedInfo['slot_data']['nightmare_alternates_index_range']>len(self.indexJson['data'][Concepts.alternates.name]):
                queue[i_killers[2]] = Concepts.alternates

        for killerId, killerType in queue.items():
            self.indexJson['data'][killerType.name].append(str(killerId))
            count = killerType.value*1000 + len(self.indexJson['data'][killerType.name])
            asyncio.run(self.Send_LocationChecks([count]))
            self.UpdateJson()

        self.VerifyWin()



