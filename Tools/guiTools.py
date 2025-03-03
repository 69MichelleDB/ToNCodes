import tkinter as tk
from tkinter import messagebox, Menu, Label, filedialog, Checkbutton
from tkinter.ttk import Treeview, Scrollbar, Label, Entry
import os.path
import pyperclip
from Tools.xmlTools import ModifyNode, InitializeConfig, ModifyCode
from Tools.fileTools import GetPossibleVRCPath
from Tools.errorHandler import ErrorLogging
from Tools.webhookTool import CheckForUpdates
from screeninfo import get_monitors
import Globals as gs
from math import isnan
from Tools.Items.Killer import DecodeNote
import datetime


# Create a window
def CreateWindow(i_title, i_width, i_height, i_resizable, i_modal=False):
    try:
        if i_modal==False:
            root = tk.Tk()
        else:
            root = tk.Toplevel()

        root.title(i_title)
        root.geometry(f"{i_width}x{i_height}")
        root.resizable(i_resizable,i_resizable)

        return root
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateWindow: {e}")

# I want the app's windows to be in the middle of the sceen
def CalculatePosition(i_width, i_height):
    try:
        monitor = get_monitors()[0]
        
        # Calculate the center position
        centerX = int(monitor.width / 2 - i_width / 2)
        centerY = int(monitor.height / 2 - i_height / 2)

        return centerX, centerY
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CalculatePosition: {e}")


# region Options Win

# Options window
def CreateOptionsWindow():
    try:
        # Window creation
        optionsRoot = CreateWindow('Options', gs._WIDTH_OPT, gs._HEIGHT_OPT, False, True)
        auxX,auxY = CalculatePosition(gs._WIDTH_OPT, gs._HEIGHT_OPT)
        optionsRoot.geometry(f'{gs._WIDTH_OPT}x{gs._HEIGHT_OPT}+{auxX}+{auxY}')
        # Modal stuff
        optionsRoot.grab_set()
        optionsRoot.transient()
        optionsRoot.wait_visibility()

        frameOptions = tk.Frame(optionsRoot)
        frameOptions.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        # Set weights so they take the window
        optionsRoot.grid_columnconfigure(0, weight=1)
        frameOptions.grid_columnconfigure(0, weight=1)
        frameOptions.grid_columnconfigure(1, weight=1)
        frameOptions.grid_columnconfigure(2, weight=1)
        optionsRoot.grid_rowconfigure(0, weight=1)
        frameOptions.grid_rowconfigure(0, weight=1)
        frameOptions.grid_rowconfigure(1, weight=1)
        frameOptions.grid_rowconfigure(2, weight=1)
        frameOptions.grid_rowconfigure(3, weight=1)
        frameOptions.grid_rowconfigure(4, weight=1)

        ## FIRST ROW
        
        # Label
        labelPath = Label(frameOptions, text="VRC log Path")
        labelPath.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Textbox/Entry Path
        textPath = tk.StringVar()
        textPath.set( gs.configList['vrchat-log-path'] if gs.auxPathFirstBoot is None else gs.auxPathFirstBoot )
        textboxPath = Entry(frameOptions, textvariable=textPath)
        textboxPath.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # File browser
        def BrowseVRCFolder():
            folder_selected = filedialog.askdirectory(parent=optionsRoot,                   # parent prevents it defaulting to root
                                            initialdir=gs.configList['vrchat-log-path'])    
            if folder_selected:
                textPath.set(folder_selected)
        # File browser button
        browseButton = tk.Button(frameOptions, text="Browse", command=BrowseVRCFolder)
        browseButton.grid(row=0, column=2, padx=5, pady=5)


        ## SECOND ROW

        # Label webhook
        labelWH = Label(frameOptions, text="Discord webhook")
        labelWH.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        # Textbox Webhook
        textWebhook = tk.StringVar()
        textWebhook.set( gs.configList['discord-webhook'] if gs.configList['discord-webhook'] is not None else '' )
        textboxWH = Entry(frameOptions, textvariable=textWebhook)
        textboxWH.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')


        # THIRD ROW
        # Label
        labelUpdate = Label(frameOptions, text="When ToNCodes starts:")
        labelUpdate.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        #Checkbox
        cbVar = tk.IntVar()
        cbVar.set(gs.configList['check-updates'])
        cbUpdates = Checkbutton(frameOptions, text="Check for updates ", variable=cbVar)
        cbUpdates.grid(row=2, column=1, padx=5, pady=5, sticky='w')


        # FOURTH ROW

        # Label check delay
        labelFD = Label(frameOptions, text="VRC log frequency (seconds)")
        labelFD.grid(row=3, column=0, padx=5, pady=5, sticky='w')

        # Textbox check delay
        textFileDelay = tk.StringVar()
        textFileDelay.set( gs.configList['file-delay'] if gs.configList['file-delay'] is not None else '' )
        textboxFD = Entry(frameOptions, textvariable=textFileDelay)
        textboxFD.grid(row=3, column=1, padx=5, pady=5, sticky='ew')


        # Save changes
        def SaveOptions():
            # VRC Path
            textPathAux = textPath.get()
            if textPathAux != gs.configList['vrchat-log-path']:
                if textPathAux and not textPathAux.endswith(os.path.sep):
                    textPathAux += os.path.sep
                print(f'Change VRC path to {textPathAux}')
                ModifyNode(gs._FILE_CONFIG, 'vrchat-log-path', textPathAux)

            # Discord Webhook
            textWebhookAux = textWebhook.get()
            if textWebhookAux != gs.configList['discord-webhook']:
                ModifyNode(gs._FILE_CONFIG, 'discord-webhook', textWebhookAux)

            # Check for updates
            cbVarAux = str(cbVar.get())
            if cbVarAux != gs.configList['check-updates']:
                ModifyNode(gs._FILE_CONFIG, 'check-updates', cbVarAux)

            # File delay
            textFileDelayAux = textFileDelay.get()
            if not isnan(float(textFileDelayAux)):                 # Make sure it's a number
                if textFileDelayAux != gs.configList['file-delay']:
                    ModifyNode(gs._FILE_CONFIG, 'file-delay', textFileDelayAux)

            # Reload config variable
            gs.configList = InitializeConfig(gs._FILE_CONFIG)
            optionsRoot.destroy()

        # LAST ROW

        # Save button
        saveButton = tk.Button(frameOptions, text='Save', command=SaveOptions)
        saveButton.grid(row=4, column=2, padx=5, pady=5)

        optionsRoot.wait_window()
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateOptionsWindow: {e}")


# region About win 

def CreateAboutWindow():
    try:
        # Window creation
        aboutRoot = CreateWindow('About...', gs._WIDTH_ABOUT, gs._HEIGHT_ABOUT, False, True)
        auxX,auxY = CalculatePosition(gs._WIDTH_ABOUT, gs._HEIGHT_ABOUT)
        aboutRoot.geometry(f'{gs._WIDTH_ABOUT}x{gs._HEIGHT_ABOUT}+{auxX}+{auxY}')
        # Modal stuff
        aboutRoot.grab_set()
        aboutRoot.transient()
        aboutRoot.wait_visibility()

        frameAbout = tk.Frame(aboutRoot)
        frameAbout.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        # Set weights so they take the window
        aboutRoot.grid_columnconfigure(0, weight=1)
        frameAbout.grid_columnconfigure(0, weight=1)

        # Textr
        bgColor = aboutRoot.cget("bg")  # Get the default background color of the window
        text = tk.Text(aboutRoot, wrap=tk.WORD, bg=bgColor, height=11)
        text.insert(tk.END,     f"ToN Codes: https://github.com/69MichelleDB/ToNCodes\n" +
                                f"Version: {gs._VERSION}\n" + 
                                f"By 69MichelleDB: https://michelledb.com\n\n" +
                                f"Terrors of Nowhere by Beyond: https://www.patreon.com/c/beyondVR\n\n" + 
                                f"Dependencies:\n" + 
                                f"pyperclip: https://github.com/asweigart/pyperclip\n" + 
                                f"screeninfo: https://github.com/rr-/screeninfo\n"+
                                f"cryptography: https://github.com/pyca/cryptography\n" + 
                                f"requests: https://github.com/psf/requests" 
                                )

        text.config(state=tk.DISABLED)  # Make the text uneditable
        text.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateAboutWindow: {e}")


# region Debug Win

# This window will only show up if the debug-window flag is 1
def DebugWindow():
    # Window creation
    debugRoot = CreateWindow('DEBUG', gs._WIDTH_DEBUG, gs._HEIGHT_DEBUG, True, True)
    auxX,auxY = CalculatePosition(gs._WIDTH_DEBUG, gs._HEIGHT_DEBUG)
    debugRoot.geometry(f'{gs._WIDTH_DEBUG}x{gs._HEIGHT_DEBUG}+{auxX}+{auxY}')

    gs.debugRoot = debugRoot

    frameDebug = tk.Frame(debugRoot)
    frameDebug.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

    # Set weights so they take the window
    debugRoot.grid_columnconfigure(0, weight=1)
    frameDebug.grid_columnconfigure(0, weight=1)

    # Textr
    bgColor = debugRoot.cget("bg")  # Get the default background color of the window
    text = tk.Text(debugRoot, wrap=tk.WORD, bg=bgColor, height=15)

    text.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    def DebugWindowRefresh():
        killer = ''
        if gs.roundMap!='' and gs.roundType!='' and gs.roundKiller!='':
            killer = DecodeNote(f"{gs.roundMap}, {gs.roundType}, {gs.roundKiller}, {gs.roundEvent}", True)

        text.config(state=tk.NORMAL)    # Allow edits
        text.delete("1.0", tk.END)
        text.insert(tk.END,     f"Round Event: {gs.roundEvent} \n" +
                                #f"Round joined: {True if gs.roundNotJoined==-1 else False}\n" + 
                                f"Round Map: {gs.roundMap} \n" +
                                f"Round Type: {gs.roundType} \n" +
                                f"Round Killer: {killer} \n" +
                                f"Round Condition: {gs.roundCondition} \n\n" 

                                f"Last update: {datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")}"
                                )
        text.config(state=tk.DISABLED)  # Make the text uneditable
        gs.debugRoot.after(int(gs.configList['file-delay'])*1000, DebugWindowRefresh)
    
    DebugWindowRefresh()


# region Main Win

# H-Menu
def HorizontalMenu(i_root):
    try:
        menubar = Menu(i_root)                  # Create and assign to the window
        i_root.config(menu=menubar)
        
        # File...
        fileMenu = Menu(menubar, tearoff=False) # New Menu
        fileMenu.add_command(label='Options', command=CreateOptionsWindow)
        fileMenu.add_command(label='Check for updates...', command=lambda: CheckForUpdates(True))
        fileMenu.add_separator()
        fileMenu.add_command(
            label='Exit',
            command=i_root.destroy
        )
        menubar.add_cascade(
            label='File',
            menu=fileMenu,
            underline=0
        )

        # About...
        menubar.add_command(label='About',  command=CreateAboutWindow)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in HorizontalMenu: {e}")


# This will allow us to display the XMLs data
def CreateTreeView(i_root, i_CodesData, i_RefreshInterval, i_RefreshCallback):
    try:
        tree = Treeview(i_root, columns=('File', 'Date', 'Code', 'Notes'), show='headings')
        tree.heading('File', text='File')
        tree.heading('Date', text='Date')
        tree.column('Code', width=0, stretch=tk.NO)                 # I'm going to keep Code hidden and add a new colum Notes
        tree.heading('Notes', text='Notes')

        tree.column('File', width=240)
        tree.column('Date', width=140)
        #tree.column('Notes', width=490)
        tree.column('Notes', width=390)
        
        tree.columnconfigure(0, weight=3)
        tree.columnconfigure(1, weight=3)
        tree.columnconfigure(3, weight=1)

        # Scrollbar
        scrollbar = Scrollbar(i_root, orient = 'vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)

        # I need the window to refresh from time to time in case there's new data
        def FillTree():
            gs.newCodeAdded = False
            existingItems = {tree.item(item, 'values') for item in tree.get_children()}     # Get all the items in the tree in a tuple, only the values
            sortedData = sorted(i_CodesData, key=lambda x: x[1], reverse=True)              # Sort by Date
            if len(existingItems) == 0:                                                     # If there's no data in the table, just insert as is
                for fileData in sortedData:
                    noteDecoded = DecodeNote(fileData[3])                                   # Review what the code is to show something user readable
                    row = list(fileData)
                    row[3] = noteDecoded
                    rowTuple = tuple(row)
                    if rowTuple not in existingItems and fileData[2]!='':                   # Only insert new values, avoid blank codes (this is for the future)
                        tree.insert('', tk.END, values=rowTuple)
            else:                                       # If there's data, I need to read from the bottom of sortedData, insert at the top of the tree
                for fileData in reversed(sortedData):
                    noteDecoded = DecodeNote(fileData[3])                                   # Review what the code is to show something user readable
                    row = list(fileData)
                    row[3] = noteDecoded
                    rowTuple = tuple(row)
                    if rowTuple not in existingItems and fileData[2]!='':                   # Only insert new values, avoid blank codes (this is for the future)
                        tree.insert('', 0, values=rowTuple)

        # Event handler for double click, copies the code to the clipboard (I needed xclip on pop!_os for it to work, on windows there's no need in theory)
        def on_row_click(event):
            selectedItems = tree.selection()
            if selectedItems:
                selectedItem = selectedItems[0]
                file, date, code, notes = tree.item(selectedItem, 'values')
                pyperclip.copy(code)
                print("Copied!", f"Code '{date}' copied to clipboard")
                messagebox.showinfo("Copied!", f"Code '{date}' copied to clipboard")
            else:
                print("Warning", "No item selected")
                messagebox.showwarning("Warning", "No item selected")

        # This will handle the data refresh once the mainloop engages
        def refreshTree():
            if not gs.writingFlag:
                nonlocal i_CodesData
                i_CodesData = i_RefreshCallback()
                if gs.newCodeAdded:
                    FillTree()
                i_root.after(i_RefreshInterval, refreshTree)

            if gs.configList['firstBoot']==True:        # Open the config window to get the path if this is the first boot
                gs.configList['firstBoot'] = False
                gs.auxPathFirstBoot = GetPossibleVRCPath()
                CreateOptionsWindow()

        # Event to handle the deletion of a specific code
        def on_row_del(event):
            selectedItems = tree.selection()
            if selectedItems:
                selectedItem = selectedItems[0]
                file, date, code, notes = tree.item(selectedItem, 'values')
                answer = messagebox.askquestion("Confirmation", f"Do you want to delete the code {date}?")          # MsgBox to confirm
                if answer == "yes":
                    ModifyCode(os.path.join(gs._FOLDER_CODES,file.replace('.txt','.xml')),date,'')     # Remove from the XML
                    print(f'Deleting code {date}')
                    messagebox.showinfo("Deleted!", f'Deleting code {date}')
                    tree.delete(selectedItem)                                                                       # Remove from the TreeView
            else:
                print("Warning", "Select a code you want to delete")
                messagebox.showwarning("Warning", "Select a code you want to delete")



        tree.bind('<Double-1>', on_row_click)           # Hook the double click event
        tree.bind('<Delete>', on_row_del)               # Hook for deleting rows
        FillTree()                                      # Fill the tree
        i_root.after(i_RefreshInterval, refreshTree)    # Hook the data refresh event

        # Debug window
        if gs.configList['debug-window'] == '1':
            DebugWindow()

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateTreeView: {e}")