import tkinter as tk
from tkinter import messagebox, Menu, Label, filedialog, Checkbutton, ttk, PhotoImage
from tkinter.ttk import Treeview, Scrollbar, Label, Entry, Combobox
import os.path
import pyperclip
from Tools.xmlTools import ModifyNode, InitializeConfig, ModifyCode, WriteNewCode
from Tools.fileTools import GetPossibleVRCPath, LoadLocale, GetAllThemes
from Tools.errorHandler import ErrorLogging
from Tools.netTools import CheckForUpdates
from screeninfo import get_monitors
import Globals as gs
from math import isnan
from Tools.Items.Killer import DecodeNote
import datetime
from Tools.netTools import SendWSMessage
import json
import re


# This will apply a common theme to every element
def ApplyStyle(i_style):
    path = os.path.join(gs._FOLDER_TOOLS,gs._FOLDER_TOOLS_THEMES,gs.configList['theme'])
    with open(path) as file:
        jsonFile = json.loads(file.read())

    maps = {}
    for widgetStyle in jsonFile:
        if widgetStyle != 'TON':
            maps = jsonFile[widgetStyle].pop('map', None)
            i_style.configure(widgetStyle, **jsonFile[widgetStyle])   # This way we can apply a style to each element, maintain and expand it easily
            if maps is not None:                                      # This is for styles that have states
                for attribute, state_value in maps.items():
                    state, value = state_value
                    i_style.map(widgetStyle, **{attribute: [(state, value)]})
        else: 
            gs.TONStyles = jsonFile[widgetStyle]           # Not everything can be configured with style.configure, they'll need manual fixes


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
        root.minsize(i_width, i_height)

        style = ttk.Style()
        ApplyStyle(style)
        if gs.configList['theme'] != 'Default.json':
            root.configure(**gs.TONStyles['window'])

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


# region Manual Code Win

# Manual code window
def CreateManualCodeWindow():
    try:
        # Window creation
        mCodeRoot = CreateWindow(gs.localeDict['Manual-Code-Title'], gs._WIDTH_MC, gs._HEIGHT_MC, False, True)
        auxX,auxY = CalculatePosition(gs._WIDTH_MC, gs._HEIGHT_MC)
        mCodeRoot.geometry(f'{gs._WIDTH_MC}x{gs._HEIGHT_MC}+{auxX}+{auxY}')
        # Modal stuff
        mCodeRoot.grab_set()
        mCodeRoot.transient()
        mCodeRoot.wait_visibility()

        frameMCode = tk.Frame(mCodeRoot, **gs.TONStyles['frameOptions'])
        frameMCode.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        # Set weights so they take the window
        mCodeRoot.grid_columnconfigure(0, weight=1)
        frameMCode.grid_columnconfigure(0, weight=1)
        frameMCode.grid_columnconfigure(1, weight=5)
        
        # FIELDS
       
        # Label Code
        labelCode = Label(frameMCode, text=gs.localeDict['Manual-Code-Label'])
        labelCode.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Textbox Code
        textCode = tk.StringVar()
        textboxCode = Entry(frameMCode, textvariable=textCode)
        textboxCode.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        def SaveManualCode():
            code = textboxCode.get()
            WriteNewCode(gs._FOLDER_CODES, f"manual_codes.xml", datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S"), code, "Manual")
            mCodeRoot.destroy()

        # Save button
        saveButton = tk.Button(frameMCode, text=gs.localeDict['Manual-Code-Save-Button'], command=SaveManualCode, **gs.TONStyles['buttons'])
        saveButton.grid(row=1, column=1, padx=5, pady=5, sticky='e')

        mCodeRoot.wait_window()

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateManualCodeWindow: {e}")

# region Options Win

# Options window
def CreateOptionsWindow():
    try:
        # Window creation
        optionsRoot = CreateWindow(gs.localeDict['Options-Title'], gs._WIDTH_OPT, gs._HEIGHT_OPT, False, True)
        auxX,auxY = CalculatePosition(gs._WIDTH_OPT, gs._HEIGHT_OPT)
        optionsRoot.geometry(f'{gs._WIDTH_OPT}x{gs._HEIGHT_OPT}+{auxX}+{auxY}')
        # Modal stuff
        optionsRoot.grab_set()
        optionsRoot.transient()
        optionsRoot.wait_visibility()

        frameOptions = tk.Frame(optionsRoot, **gs.TONStyles['frameOptions'])
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
        frameOptions.grid_rowconfigure(5, weight=1)
        frameOptions.grid_rowconfigure(6, weight=1)
        frameOptions.grid_rowconfigure(7, weight=1)

        restartNeeded = False
        # Some options may need a restart to take effect, this enables a warning
        def NeedRestart(event=None):
            nonlocal restartNeeded
            restartNeeded = True


        ## FIRST ROW
        
        # Label
        labelPath = Label(frameOptions, text=gs.localeDict['Options-VRCPath-Label'])
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
        browseButton = tk.Button(frameOptions, text=gs.localeDict['Options-VRCPath-Browse'], command=BrowseVRCFolder, **gs.TONStyles['buttons'])
        browseButton.grid(row=0, column=2, padx=5, pady=5)


        ## SECOND ROW

        # Label webhook
        labelWH = Label(frameOptions, text=gs.localeDict['Options-Webhook-Label'])
        labelWH.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        # Textbox Webhook
        textWebhook = tk.StringVar()
        textWebhook.set( gs.configList['discord-webhook'] if gs.configList['discord-webhook'] is not None else '' )
        textboxWH = Entry(frameOptions, textvariable=textWebhook)
        textboxWH.grid(row=1, column=1, padx=5, pady=5, sticky='ew')


        # THIRD ROW
        # Label
        labelUpdate = Label(frameOptions, text=gs.localeDict['Options-Update-Label'])
        labelUpdate.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        #Checkbox
        cbVar = tk.IntVar()
        cbVar.set(gs.configList['check-updates'])
        cbUpdates = Checkbutton(frameOptions, text=gs.localeDict['Options-Update-Check'], variable=cbVar, **gs.TONStyles['checkbutton'])
        cbUpdates.grid(row=2, column=1, padx=5, pady=5, sticky='w')


        # FOURTH ROW

        # Label check delay
        labelFD = Label(frameOptions, text=gs.localeDict['Options-Delay-Label'])
        labelFD.grid(row=3, column=0, padx=5, pady=5, sticky='w')

        # Textbox check delay
        textFileDelay = tk.StringVar()
        textFileDelay.set( gs.configList['file-delay'] if gs.configList['file-delay'] is not None else '' )
        textboxFD = Entry(frameOptions, textvariable=textFileDelay)
        textboxFD.grid(row=3, column=1, padx=5, pady=5, sticky='ew')


        # FIFTH ROW
        # Label
        labelWS = Label(frameOptions, text=gs.localeDict['Options-Websocket-Label'])
        labelWS.grid(row=4, column=0, padx=5, pady=5, sticky='w')

        #Checkbox
        cbVarWS = tk.IntVar()
        cbVarWS.set(gs.configList['tontrack-ws'])
        cbWS = Checkbutton(frameOptions, text=gs.localeDict['Options-Websocket-Check'], variable=cbVarWS, command=NeedRestart, **gs.TONStyles['checkbutton'])
        cbWS.grid(row=4, column=1, padx=5, pady=5, sticky='w')


        # SIXTH ROW

        # These are to convert the ID of the language to the name and the other way arround
        def Lang2ID(_lang):
            result = ''
            match _lang:
                case 'en':
                    result = 'English'
                case 'es':
                    result = 'Español'
            return result

        def ID2Lang(_lang):
            result = ''
            match _lang:
                case 'English':
                    result = 'en'
                case 'Español':
                    result = 'es'
            return result

        # Label
        labelcomboLocale = Label(frameOptions, text=gs.localeDict['Options-Locale-Label'])
        labelcomboLocale.grid(row=5, column=0, padx=5, pady=5, sticky='w')

        #Combo box
        comboVarLocale = tk.StringVar()
        comboLocale = Combobox(frameOptions, values=['English','Español'], state='readonly', textvariable=comboVarLocale)
        comboLocale.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        auxLocale = Lang2ID(gs.configList['locale'])
        comboLocale.set(auxLocale)
        comboLocale.bind('<<ComboboxSelected>>', NeedRestart)

    
        # SEVENTH ROW

        # Label
        labelTheme = Label(frameOptions, text=gs.localeDict['Options-Theme-Label'])
        labelTheme.grid(row=6, column=0, padx=5, pady=5, sticky='w')

        #Combo box
        comboVarTheme = tk.StringVar()
        comboTheme = Combobox(frameOptions, values=GetAllThemes(), state='readonly', textvariable=comboVarTheme)
        comboTheme.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        comboTheme.set(gs.configList['theme'])
        comboTheme.bind('<<ComboboxSelected>>', NeedRestart)


        # EIGHTH ROW
        # Label
        labelDebug = Label(frameOptions, text=gs.localeDict['Options-Debug-Label'])
        labelDebug.grid(row=7, column=0, padx=5, pady=5, sticky='w')

        #Checkbox
        cbVarDebug = tk.IntVar()
        cbVarDebug.set(gs.configList['debug-window'])
        cbDebug = Checkbutton(frameOptions, text=gs.localeDict['Options-Debug-Check'], variable=cbVarDebug, **gs.TONStyles['checkbutton'])
        cbDebug.grid(row=7, column=1, padx=5, pady=5, sticky='w')


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

            # Connect to tontrack.me
            cbVarAux2 = str(cbVarWS.get())
            if cbVarAux2 != gs.configList['tontrack-ws']:
                ModifyNode(gs._FILE_CONFIG, 'tontrack-ws', cbVarAux2)

            # Language
            comboVarLocaleAux = ID2Lang(comboVarLocale.get())
            if comboVarLocaleAux != gs.configList['locale']:
                ModifyNode(gs._FILE_CONFIG, 'locale', comboVarLocaleAux)

            # Theme
            comboVarThemeAux = comboVarTheme.get()
            if comboVarThemeAux != gs.configList['theme']:
                ModifyNode(gs._FILE_CONFIG, 'theme', comboVarThemeAux)

            # Debug window
            cbVarAuxDebug = str(cbVarDebug.get())
            if cbVarAuxDebug != gs.configList['debug-window']:
                ModifyNode(gs._FILE_CONFIG, 'debug-window', cbVarAuxDebug)
                if cbVarAuxDebug == '1':
                    DebugBar(gs.root)
                else:
                    gs.root.after_cancel(gs.debugBarAfterID)
                    gs.debugBarFrame.destroy()

            # Reload config variable
            gs.configList = InitializeConfig(gs._FILE_CONFIG)
            optionsRoot.destroy()
            nonlocal restartNeeded
            if restartNeeded:
                messagebox.showinfo(gs.localeDict['Options-Need-Restart-Head'],gs.localeDict['Options-Need-Restart-Body'])

        # LAST ROW

        # Save button
        saveButton = tk.Button(frameOptions, text=gs.localeDict['Options-Save-Button'], command=SaveOptions, **gs.TONStyles['buttons'])
        saveButton.grid(row=7, column=2, padx=5, pady=5)

        optionsRoot.wait_window()
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateOptionsWindow: {e}")


# region About win 

def CreateAboutWindow():
    try:
        # Window creation
        aboutRoot = CreateWindow(gs.localeDict['About-Title'], gs._WIDTH_ABOUT, gs._HEIGHT_ABOUT, False, True)
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
        text = tk.Text(aboutRoot, wrap=tk.WORD, **gs.TONStyles['about'])
        text.insert(tk.END,     f"ToN Codes: https://github.com/69MichelleDB/ToNCodes\n" +
                                f"Version: {gs._VERSION}\n" + 
                                f"By 69MichelleDB: https://michelledb.com\n\n" +
                                f"Terrors of Nowhere by Beyond: https://www.patreon.com/c/beyondVR\n" + 
                                f"tontrack.me by Cinossu: https://tontrack.me/\n\n" + 
                                f"Dependencies:\n" + 
                                f"pyperclip: https://github.com/asweigart/pyperclip\n" + 
                                f"screeninfo: https://github.com/rr-/screeninfo\n"+
                                f"cryptography: https://github.com/pyca/cryptography\n" + 
                                f"requests: https://github.com/psf/requests\n" + 
                                f"websockets: https://github.com/python-websockets/websockets"
                                )

        text.config(state=tk.DISABLED)  # Make the text uneditable
        text.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateAboutWindow: {e}")

# region Main Win

# H-Menu
def HorizontalMenu(i_root):
    try:
        menubar = Menu(i_root, **gs.TONStyles['menu']['baseMenu'])                  # Create and assign to the window
        i_root.config(menu=menubar)
        
        # File...
        fileMenu = Menu(menubar, **gs.TONStyles['menu']['file']) # New Menu
        fileMenu.add_command(label=gs.localeDict['Horizontal-Menu-Manual-Code'], command=CreateManualCodeWindow)
        fileMenu.add_separator()
        fileMenu.add_command(label=gs.localeDict['Horizontal-Menu-Options'], command=CreateOptionsWindow)
        fileMenu.add_command(label=gs.localeDict['Horizontal-Menu-Updates'], command=lambda: CheckForUpdates(True))
        fileMenu.add_separator()
        fileMenu.add_command(
            label=gs.localeDict['Horizontal-Menu-Exit'],
            command=i_root.destroy
        )
        menubar.add_cascade(
            label=gs.localeDict['Horizontal-Menu-File'],
            menu=fileMenu,
            underline=0
        )

        # About...
        menubar.add_command(label=gs.localeDict['Horizontal-Menu-About'],  command=CreateAboutWindow)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in HorizontalMenu: {e}")

# This is the Combobox underneath the Menu with the name of the log to filter
def HorizontalFileBox(i_root):
    try:
        dateBoxFrame = tk.Frame(i_root, **gs.TONStyles['frameHorizontalDate'])        # Gonna put in a frame
        dateBoxFrame.pack(side=tk.TOP, fill=tk.X)

        gs.fileBoxSelected = tk.StringVar()
        combobox = Combobox(dateBoxFrame, values=[], state='readonly', textvariable=gs.fileBoxSelected)
        combobox.pack(pady=5, padx=5, fill=tk.X, expand=True)

        filesOnly = []

        # Feed the Log files names to the combobox
        def RefreshFileBox():
            sortedCodesData = sorted(gs.codesData, key=lambda x: x[1], reverse=True)    # Sort
            for file in sortedCodesData:
                if file[0] not in filesOnly:                                            # I need the unique names without repeating
                    filesOnly.append(file[0])
            if len(filesOnly)!=len(combobox['values']):                                      # If there's new files, update the combobox
                filesOnlySorted = sorted(filesOnly, key=lambda x: x, reverse=True)
                combobox['values'] = filesOnlySorted
                if len(filesOnlySorted)>0:                 # If no value was selected, choose the oldest
                    combobox.set(filesOnlySorted[0])
                    gs.fileBoxChanged = True
            i_root.after(int(gs.configList['ui-delay']), RefreshFileBox)

        RefreshFileBox()

        # If the selected value changes, we inform the tree that it needs a refresh
        def on_value_change(event):
            gs.fileBoxChanged = True

        combobox.bind('<<ComboboxSelected>>', on_value_change)        

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in HorizontalComboBox: {e}")

# This will allow us to display the XMLs data
def CreateTreeView(i_root, i_RefreshInterval, i_RefreshCallback):
    try:
        treeFrame = tk.Frame(i_root, **gs.TONStyles['frameTree'])
        treeFrame.pack(side=tk.TOP, fill="both", expand=True)

        tree = Treeview(treeFrame, columns=('File', 'Date', 'Code', 'Notes'), show='headings')
        tree.column('File', width=0, stretch=tk.NO)                 # File column will now be hidden
        tree.heading('Date', text=gs.localeDict['Tree-Dates'])
        tree.column('Code', width=0, stretch=tk.NO)                 # I'm going to keep Code hidden and add a new colum Notes
        tree.heading('Notes', text=gs.localeDict['Tree-Notes'])

        #tree.column('File', width=240)
        tree.column('Date', width=150)
        tree.column('Notes', width=500)
        
        #tree.columnconfigure(0, weight=3)
        tree.columnconfigure(1, weight=3)
        tree.columnconfigure(3, weight=1)

        # Scrollbar
        scrollbar = Scrollbar(treeFrame, orient = 'vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        tree.pack(side='left', fill='both', expand=True)

        # I need the window to refresh from time to time in case there's new data
        def FillTree():
            gs.newCodeAdded = False
            gs.fileBoxChanged = False
            # existingItems = {tree.item(item, 'values') for item in tree.get_children()}     # Get all the items in the tree in a tuple, only the values
            sortedData = sorted(gs.codesData, key=lambda x: x[1], reverse=True)             # Sort by Date
            if gs.fileBoxSelected.get() != '':                                              # Only from the selected file
                
                newDataList = []                                                            # Get selected data only
                for data in sortedData:
                    if data[0] == gs.fileBoxSelected.get():
                        newDataList.append(data)
                
                for item in tree.get_children():                # Empty the tree
                    tree.delete(item)
                for fileData in newDataList:
                    noteDecoded = DecodeNote(fileData[3])       # Review what the code is to show something user readable
                    row = list(fileData)
                    row[3] = noteDecoded
                    rowTuple = tuple(row)
                    if fileData[2]!='':                         # Avoid blank codes (this is for deleted codes)
                        tree.insert('', tk.END, values=rowTuple)

        # Event handler for double click, copies the code to the clipboard (I needed xclip on pop!_os for it to work, on windows there's no need in theory)
        def on_row_click(event):
            selectedItems = tree.selection()
            if selectedItems:
                selectedItem = selectedItems[0]
                file, date, code, notes = tree.item(selectedItem, 'values')
                pyperclip.copy(code)
                print("Copied!", f"Code '{date}' copied to clipboard")
                messagebox.showinfo(gs.localeDict['Message-Code-Copied-Head'], gs.localeDict['Message-Code-Copied-Body'].format(date=date))
            else:
                print("Warning", "No item selected")
                messagebox.showwarning(gs.localeDict['Message-Code-Copied-NoItem-Head'], gs.localeDict['Message-Code-Copied-NoItem-Body'])

        # This will handle the data refresh once the mainloop engages
        def refreshTree():
            if not gs.writingFlag:
                gs.codesData = i_RefreshCallback()
                if gs.newCodeAdded or gs.fileBoxChanged:
                    FillTree()

            if gs.configList['firstBoot']==True:        # Open the config window to get the path if this is the first boot
                gs.configList['firstBoot'] = False
                gs.auxPathFirstBoot = GetPossibleVRCPath()
                CreateOptionsWindow()

            i_root.after(i_RefreshInterval, refreshTree)

        # Event to handle the deletion of a specific code
        def on_row_del(event):
            selectedItems = tree.selection()
            if selectedItems:
                selectedItem = selectedItems[0]
                file, date, code, notes = tree.item(selectedItem, 'values')
                answer = messagebox.askquestion(gs.localeDict['Message-Code-Delete-Head'], gs.localeDict['Message-Code-Delete-Body'].format(date=date)) # MsgBox to confirm
                if answer == "yes":
                    ModifyCode(os.path.join(gs._FOLDER_CODES,file.replace('.txt','.xml')),date,'')     # Remove from the XML
                    print(f'Deleting code {date}')
                    tree.delete(selectedItem)                                                          # Remove from the TreeView
                    messagebox.showinfo(gs.localeDict['Message-Code-Deleted-Head'], gs.localeDict['Message-Code-Deleted-Body'].format(date=date))
            else:
                print("Warning", "Select a code you want to delete")
                messagebox.showwarning(gs.localeDict['Message-Code-Delete-NoSelection-Head'], gs.localeDict['Message-Code-Delete-NoSelection-Body'])

        tree.bind('<Double-1>', on_row_click)           # Hook the double click event
        tree.bind('<Delete>', on_row_del)               # Hook for deleting rows
        FillTree()                                      # Fill the tree
        i_root.after(i_RefreshInterval, refreshTree)    # Hook the data refresh event

        # Handler for when the main window closes
        def on_closing():
            print('Closing...')
            SendWSMessage("ws_disconnect", [])
            gs.root.destroy()

        gs.root.protocol("WM_DELETE_WINDOW", on_closing)   # Handle what to do during a delete window event for the debug window

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CreateTreeView: {e}")


# This bar at the bottom of the window will display debug info of the round
def DebugBar(i_root):
    try:
        gs.debugBarFrame = tk.Frame(i_root, **gs.TONStyles['frameDebug'])
        gs.debugBarFrame.pack(side=tk.BOTTOM, fill=tk.X)

        heightT = 1
        if 'debug-ws' in gs.configList:
            if gs.configList['debug-ws']=='1':
                heightT = 2
        text = tk.Text(gs.debugBarFrame, wrap=tk.WORD, height=heightT, **gs.TONStyles['debugText'])
        text.pack(fill=tk.X, expand=True)
        
        # Function to refresh the content of the debug bar
        def DebugBarRefresh():
            killer = ''
            mapRegex = re.compile(r"(^.+?) \((\d+)\)$")
            if gs.roundMap!='' and gs.roundType!='' and gs.roundKiller!='':
                killer = DecodeNote(f"{gs.roundMap}, {gs.roundType}, {gs.roundKiller}, {gs.roundEvent}", True)

            text.config(state=tk.NORMAL)    # Enable edits in the text box
            text.delete("1.0", tk.END)
            currentMap = mapRegex.search(gs.roundMap)
            if currentMap:
                currentMap = currentMap.groups()[0]
            else:
                currentMap = ''

            auxWS = ''
            if 'debug-ws' in gs.configList:
                if gs.configList['debug-ws']=='1':
                    auxWS = gs.lastWSMessage
            text.insert(tk.END, f"{datetime.datetime.now().strftime("%H:%M:%S")} {gs.roundEvent} {currentMap} {gs.roundType} {killer} {gs.roundCondition}\n" \
                                f"{auxWS}")
            text.config(state=tk.DISABLED)  # Disable edits in the text box
            gs.debugBarAfterID = gs.root.after(gs._DEBUG_REFRESH, DebugBarRefresh)

        DebugBarRefresh()
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in DebugBar: {e}")
