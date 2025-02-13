import requests
import Globals as gs
import os.path
from Tools.fileTools import CreateNewTempCodeFile


## Discord Webhook, reused code from my bsky bot, test
def SendWebhook(i_date, i_code):

    # This will be our temp file to send, discord has a 2000 characters limit, so it has to be as a txt file
    fileName = CreateNewTempCodeFile(gs._FOLDER_TEMP, i_date + '_TEMP.txt', i_code)

    payload = {
        "content": f'New code found: {i_date}',
    }

    try:
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
        print(f"Error during webhook upload: {e}")