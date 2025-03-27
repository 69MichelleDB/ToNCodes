import asyncio
import websockets
import json
import Globals as gs
from Tools.errorHandler import ErrorLogging

'''
- WSRecvBind("ws_connect", () => {
- WSRecvBind("ws_disconnect", () => roundHistorySessionFinish());
WSRecvBind("pools", (_pools, clean = false) => {
- WSRecvBind("opt_in", () => {
- WSRecvBind("opt_out", () => {
- WSRecvBind("round_start", () => {
- WSRecvBind("round_map", function(name, id, round) {
WSRecvBind("round_map_swap", function(id) {
WSRecvBind("round_custom_post", () => {
WSRecvBind("round_killers_post", (round, ...killers) => {
WSRecvBind("round_unknown", (round) => {
WSRecvBind("round_custom", () => {
WSRecvBind("round_saboteur", (username) => {
WSRecvBind("round_possessed", () => {
WSRecvBind("page_collected", (page_count) => {
WSRecvBind("item_player", (player, item_id) => {
- WSRecvBind("round_killers", (killerA, killerB, killerC, round) => {
WSRecvBind("is_neo_pilot", () => {
WSRecvBind("is_meatball_man", () => {
WSRecvBind("is_hungry_home_invader", () => {
WSRecvBind("is_atrached", () => {
WSRecvBind("is_glorbo", () => {
WSRecvBind("is_wild_yet_bloodthirsty_creature", () => {
WSRecvBind("enemy_spawned", (end_of_round = false) => {
WSRecvBind("enemy_enraged", (name, level = 1) => {
WSRecvBind("is_joy_awake", () => {
- WSRecvBind("round_lost", () => {
- WSRecvBind("round_won", () => {
WSRecvBind("achievement", (name) => {
WSRecvBind("player_afk", () => {
WSRecvBind("player_died", (username) => {
WSRecvBind("__behaviour__world_joining", (world_id, instance_id, instance_details = "") => {
WSRecvBind("__behaviour__world_joined", () => {
WSRecvBind("__behaviour__world_left", () => rh_round_finish("skipped"));
WSRecvBind("__behaviour__player_self", (username, user_id) => {
WSRecvBind("__behaviour__player_avatar", (avatar) => {
WSRecvBind("__behaviour__player_join", (username) => {
WSRecvBind("__behaviour__player_left", (username) => {
'''


# region WS server

connected_clients = set()

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
                    response = json.dumps(args)
                    await asyncio.gather(*(client.send(response) for client in connected_clients))
                elif data.get("event") == "pools":          # tontrack connected
                    response = json.dumps({"event": "ws_connect", "args": []})
                    await asyncio.gather(*(client.send(response) for client in connected_clients))
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




# region WS Client

# Send messages from ToNCodes to the Websocket server to communicate with tontrack.me
async def SendMessageAsync(i_event, i_args):
    try:
        async with websockets.connect(f"ws://{gs._WSURL}:{gs._WSPORT}") as websocket:       # Make a connection
            message = {"event": "TONCODES", "args": {"event": i_event, "args": i_args}}     # Build the message
            print(f"Sending WS message: {message}")
            await websocket.send(json.dumps(message))                                       # And send it away
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in SendMessage: {e}")

# Since we need to send messages async, this function will do intermediary work
def SendWSMessage(i_event, i_args):
    if gs.wsFlag:                                                                           # Only send messages if the WS server is on
        asyncio.run(SendMessageAsync(i_event, i_args))
