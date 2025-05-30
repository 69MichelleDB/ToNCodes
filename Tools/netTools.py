import requests
import Globals as gs
import os.path
import webbrowser
import asyncio
import websockets
import json
from time import sleep
from tkinter import messagebox
from Tools.fileTools import CreateNewTempCodeFile, GetAllFiles
from Tools.errorHandler import ErrorLogging
from Tools.updateHandler import WarningHandler
from Tools.Items.Encounters import DecodeNote
from pythonosc import udp_client


# region Discord

## Discord Webhook, reused code from my bsky bot
def SendWebhook(i_date, i_note, i_code):
    try:
        note = DecodeNote(i_note)

        # This will be our temp file to send, discord has a 2000 characters limit, so it has to be as a txt file
        fileName = CreateNewTempCodeFile(gs._FOLDER_TEMP, i_date + '_TEMP.txt', i_code)

        payload = {
            "content": gs.localeDict['Discord-Webhook-Message'].format(i_date=i_date, note=note),
        }

        with open(fileName, "rb") as file:
            response = requests.post(
                        gs.configList['discord-webhook'], 
                        data=payload, 
                        files={'file': (fileName, file)}
                        )

        if response.status_code == 200:
            print("File sent successfully!")
        else:
            print(f"Failed to send the file. Status code: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in SendWebhook: {e}")


# region Updates

# Check for updates on github and alert the user there's something available
def CheckForUpdates(i_checkForcedUpdate=False):
    try:
        result = 0
        # Only check for updates if the user wants
        if gs.configList['check-updates']=='1' or i_checkForcedUpdate == True:
            
            print('Checking for updates...')
            urlLatest = f"{gs._GITHUB}/releases/latest"
            url = urlLatest.replace('github.com/','api.github.com/repos/')
            print(f'Connecting to {url}')

            response = requests.get(url)

            if response.status_code == 200:
                latestJson = response.json()
                latestVersion = latestJson['tag_name']
                #latestNotes = latestJson['body']
                print(f"Connected, latest release: {latestVersion}")
                if latestVersion != gs._VERSION:
                    if gs.configList['check-updates-warned'] == '0' or i_checkForcedUpdate == True:
                        result = 1  #ModifyNode(gs._CONFIG_FILE, 'check-updates-warned', '1')
                        answer = messagebox.askyesno(gs.localeDict['Update-New-Head'], gs.localeDict['Update-New-Body'].format(latestVersion=latestVersion))
                        if answer:
                            print("Opening GitHub link")
                            webbrowser.open_new_tab(urlLatest)
                        else:
                            print("Not opening GitHub link")
                    else:
                        result = 3  
                        print("User was already alerted, don't show promt again")
                else:
                    print("No new update, no need to prompt anything")
                    if i_checkForcedUpdate == True:
                        messagebox.showinfo(gs.localeDict['Update-NoNew-Head'], gs.localeDict['Update-NoNew-Body'])
                    if gs.configList['check-updates-warned'] == '1':
                        print ("Reseting new version warning")
                        result = 2 #ModifyNode(gs._CONFIG_FILE, 'check-updates-warned', '0')
            else:
                print(f"Failed to GitHub. Status code: {response.status_code}")
                print(response.text)

        WarningHandler(result)
        
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CheckForUpdates: {e}")


# region Websocket server

connected_clients = set()

# Handles incoming messages
async def handler(websocket):
    print("Client connected.")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received: {message}")
            # Parse the received message as JSON if needed
            try:
                data = json.loads(message)
                if data.get("event") == "TONCODES":         # Message from ToNCodes ws client, the args have the message
                    args = data.get("args")
                    print(f"Args received: {args}")
                    gs.lastWSMessage = json.dumps(args)
                    await asyncio.gather(*(client.send(gs.lastWSMessage) for client in connected_clients))
                elif data.get("event") == "pools":          # tontrack connected
                    gs.lastWSMessage = json.dumps({"event": "ws_connect", "args": []})
                    await asyncio.gather(*(client.send(gs.lastWSMessage) for client in connected_clients))
            except json.JSONDecodeError:
                await websocket.send("Invalid JSON format")

    except websockets.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)

# Start the WebSocket server
async def BootWSServer():
    try:
        server = await websockets.serve(handler, gs._WSURL, gs._WSPORT)         # Start the server
        gs.wsFlag = True                                                        # This flag prevents messages before server is up
        print(f"WebSocket server started on ws://{gs._WSURL}:{gs._WSPORT}")
        await server.wait_closed()                                              # And keep it running
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in BootWSServer: {e}")

# Run the WebSocket server
def WSstart():
    asyncio.run(BootWSServer())


# region Websocket Client

# Send messages from ToNCodes to the Websocket server to communicate with tontrack.me
async def SendMessageAsync(i_event, i_args):
    try:
        async with websockets.connect(f"ws://{gs._WSURL}:{gs._WSPORT}") as websocket:       # Make a connection
            message = {"event": "TONCODES", "args": {"event": i_event, "args": i_args}}     # Build the message
            await websocket.send(json.dumps(message))                                       # And send it away
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in SendMessage: {e}")

# Since we need to send messages async, this function will do intermediary work
def SendWSMessage(i_event, i_args):
    if gs.wsFlag:                                                                           # Only send messages if the WS server is on
        asyncio.run(SendMessageAsync(i_event, i_args))


# region OSC Client

# Small class with a few key attributes to process all OSC calls
class OSCOrder:
    def __init__ (self, i_key, i_attribute, i_values, i_extra=''): 
        self.key = i_key                    # The key the regex was in
        self.attribute = i_attribute        # The name the of the OSC attribute
        self.values = i_values              # The values to send
        self.extraOrders = i_extra          # If there needs something else to be done...

# We are going to make a queue of OSC calls and process them individually
def ExecuteOSCList(i_orderList):
    if gs.configList['osc-enabled'] == '1':             # Only send messages if OSC is enabled
        for order in i_orderList:
            if order.values is not None and OSCParamName(order.attribute)!='':
                SendOSCMessage(order.attribute, order.values)

            match order.extraOrders:            # Some orders may require extra actions like restarting some OSC variables
                case 'diedinround':
                    DiedInRound()
                case 'roundended':
                    RoundEnded()
    return []

def LoadOSCDebug(i_dict):
    for item in i_dict:
        value = None
        aux = i_dict[item]['values']
        if isinstance(aux, bool):
            value = False
        elif isinstance(aux, int):
            value = 255
        elif isinstance(aux, str):
            value = ""
        elif isinstance(aux, float):
            value = 0.0
        else:
            value = 255
        if item in ['round_type','page_collected','landedStuns','missedStuns']:
            value = 0
        gs.oscJsonProfileDEBUG[i_dict[item]['variable'].replace('/avatar/parameters/','')] = value

# Initialize the OSC client
def InitializeOSCClient(i_port, i_file):
    try:
        if gs.configList['osc-enabled'] == '1':                                         # Only if OSC is enabled
            gs.oscClient = udp_client.SimpleUDPClient(gs._OSCURL, int(i_port))          # Connect client
        else:
            gs.oscClient = None

        # Handle different situations for the profile
        if i_file is None or not os.path.exists(i_file):                            # If the profile is not defined or the file doesn't exist, default
            gs.configList['osc-profile'] = gs._FILE_FALLBACKOSCPROFILE
            gs.oscJsonProfile = GetOSCProfileData(gs.configList['osc-profile'])
        else:
            gs.oscJsonProfile = GetOSCProfileData(i_file)

        LoadOSCDebug(gs.oscJsonProfile)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in InitializeClient: {e}")

# Read a given profile json file and return all the data in a dictionary
def GetOSCProfileData(i_file):
    with open(i_file) as file:
        return json.load(file)

# Simple function to send OSC messages
def SendOSCMessage(i_variable, i_value):
    try:
        if gs.configList['osc-enabled'] == '1':             # Only send messages if OSC is enabled
            if gs.oscClient is None:                        # Just in case they change the setting and it didn't have time to initialize
                InitializeOSCClient(gs.configList['osc-in-port'], gs.configList['osc-profile'])
            print(f"OSC: {i_variable}={i_value}")
            gs.lastOSCMessage = f"{i_variable}={i_value}"
            gs.oscClient.send_message(i_variable, i_value)  # Send the message
            #gs.oscJsonProfileDEBUG[i_variable.replace('/avatar/parameters/','')] = i_value
            gs.oscJsonProfileDEBUG[OSCParamName(i_variable)] = i_value
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in SendOSCMessage: {e}")

def OSCParamName(i_name):
    return i_name.replace('/avatar/parameters/','')


def DiedInRound():
    sleep(0.1)
    SendOSCMessage(gs.oscJsonProfile['TONISALIVE']['variable'], True)

def RoundEnded():
    SendOSCMessage(gs.oscJsonProfile['round_map']['variable'], 255)
    SendOSCMessage(gs.oscJsonProfile['round_type']['variable'], 0)

    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['round_killer1']['variable'])]!=255:
        SendOSCMessage(gs.oscJsonProfile['round_killer1']['variable'], 255)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['round_killer2']['variable'])]!=255:
        SendOSCMessage(gs.oscJsonProfile['round_killer2']['variable'], 255)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['round_killer3']['variable'])]!=255:
        SendOSCMessage(gs.oscJsonProfile['round_killer3']['variable'], 255)

    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['round_possessed']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['round_possessed']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['page_collected']['variable'])]!=0:
        SendOSCMessage(gs.oscJsonProfile['page_collected']['variable'], 0)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_joy_asleep']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_joy_asleep']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_joy_awake']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_joy_awake']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_glorbo']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_glorbo']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_wild_yet_bloodthirsty_creature']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_wild_yet_bloodthirsty_creature']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_atrached']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_atrached']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_hungry_home_invader']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_hungry_home_invader']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_meatball_man']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_meatball_man']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_foxy']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_foxy']['variable'], False)
    if gs.oscJsonProfileDEBUG[OSCParamName(gs.oscJsonProfile['is_gigabyte']['variable'])]!=False:
        SendOSCMessage(gs.oscJsonProfile['is_gigabyte']['variable'], False)
