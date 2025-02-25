import requests
import Globals as gs
import os.path
import webbrowser
from tkinter import messagebox
from Tools.fileTools import CreateNewTempCodeFile
from Tools.errorHandler import ErrorLogging
from Tools.updateHandler import WarningHandler
from Tools.Items.Killer import DecodeNote


## Discord Webhook, reused code from my bsky bot
def SendWebhook(i_date, i_note, i_code):
    try:
        note = DecodeNote(i_note)

        # This will be our temp file to send, discord has a 2000 characters limit, so it has to be as a txt file
        fileName = CreateNewTempCodeFile(gs._FOLDER_TEMP, i_date + '_TEMP.txt', i_code)

        payload = {
            "content": f'New code found: {i_date}, Notes: {note}',
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
                latestNotes = latestJson['body']
                print(f"Connected, latest release: {latestVersion}")
                if latestVersion != gs._VERSION:
                    if gs.configList['check-updates-warned'] == '0' or i_checkForcedUpdate == True:
                        result = 1  #ModifyNode(gs._CONFIG_FILE, 'check-updates-warned', '1')
                        answer = messagebox.askyesno("New Update", f"A new version was released [{latestVersion}], visit GitHub to download the latest release?\n\n{latestNotes}")
                        if answer:
                            print("Opening GitHub link")
                            webbrowser.open(urlLatest)
                        else:
                            print("Not opening GitHub link")
                    else:
                        result = 3  
                        print("User was already alerted, don't show promt again")
                else:
                    print("No new update, no need to prompt anything")
                    if i_checkForcedUpdate == True:
                        messagebox.showinfo("New Update", "You currently have the latest version.")
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
