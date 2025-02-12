import tkinter as tk
from tkinter import messagebox, Menu, Label, filedialog
from tkinter.ttk import Treeview, Scrollbar, Label, Entry
import os.path
import pyperclip
from Tools.xmlTools import ChangePath, InitializeConfig, ModifyCode
from Tools.fileTools import GetPossibleVRCPath
from screeninfo import get_monitors
import Globals as gs


# Create a window
def CreateWindow(i_title, i_width, i_height, i_resizable, i_modal=False):
    if i_modal==False:
        root = tk.Tk()
    else:
        root = tk.Toplevel()

    root.title(i_title)
    root.geometry(f"{i_width}x{i_height}")
    root.resizable(i_resizable,i_resizable)

    return root

# I want the app's windows to be in the middle of the sceen
def CalculatePosition(i_width, i_height):
    monitor = get_monitors()[0]
    
    # Calculate the center position
    centerX = int(monitor.width / 2 - i_width / 2)
    centerY = int(monitor.height / 2 - i_height / 2)

    return centerX, centerY


# region Options Win

# Options window
def CreateOptionsWindow():
    # Window creation
    optionsRoot = CreateWindow('Options', gs._WIDTH_OPT, gs._HEIGHT_OPT, False, True)
    auxX,auxY = CalculatePosition(gs._WIDTH_OPT, gs._HEIGHT_OPT)
    optionsRoot.geometry(f'{gs._WIDTH_OPT}x{gs._HEIGHT_OPT}+{auxX}+{auxY}')
    # Modal stuff
    optionsRoot.grab_set()
    optionsRoot.transient()
    optionsRoot.wait_visibility()

    framePath = tk.Frame(optionsRoot)
    framePath.pack(fill='x', padx=10, pady=10)

    ## FIRST ROW
    # Label
    labelPath = Label(framePath, text="VRC log Path")
    labelPath.pack(side='left')

    # Textbox/Entry
    textPath = tk.StringVar()
    textPath.set(gs.configList['vrchat-log-path'])
    textboxPath = Entry(framePath, textvariable=textPath)
    textboxPath.pack(side='left', fill='x', padx=5, expand=True)

    # File browser
    def BrowseVRCFolder():
        folder_selected = filedialog.askdirectory(parent=optionsRoot,                   # parent prevents it defaulting to root
                                        initialdir=gs.configList['vrchat-log-path'])    
        if folder_selected:
            textPath.set(folder_selected)
    # File browser button
    browseButton = tk.Button(framePath, text="Browse", command=BrowseVRCFolder)
    browseButton.pack(side='left', padx=5)

    # Save changes
    def SaveOptions():
        # VRC Path
        textPathfix = textPath.get()
        if textPathfix and not textPathfix.endswith(os.path.sep):
            textPathfix += os.path.sep
        print(f'Change VRC path to {textPathfix}')
        ChangePath(gs._CONFIG_FILE, textPathfix)

        # Reload config variable
        gs.configList = InitializeConfig(gs._CONFIG_FILE)
        optionsRoot.destroy()

    saveButton = tk.Button(framePath, text='Save', command=SaveOptions)
    saveButton.pack(side='left', padx=5)

    optionsRoot.wait_window()



# region Main Win

# H-Menu
def HorizontalMenu(i_root):
    menubar = Menu(i_root)                  # Create and assign to the window
    i_root.config(menu=menubar)
    
    # File...
    fileMenu = Menu(menubar, tearoff=False) # New Menu
    fileMenu.add_command(label='Options',  command=CreateOptionsWindow)
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
    aboutMenu = Menu(menubar, tearoff=False)
    aboutMenu.add_command(label='About')
    menubar.add_cascade(
        label='About',
        menu=aboutMenu,
        underline=0
    )


# This will allow us to display the XMLs data
def CreateTreeView(i_root, i_CodesData, i_RefreshInterval, i_RefreshCallback):
    tree = Treeview(i_root, columns=('File', 'Date', 'Code', 'Notes'), show='headings')
    tree.heading('File', text='File')
    tree.heading('Date', text='Date')
    tree.column('Code', width=0, stretch=tk.NO)                 # I'm going to keep Code hidden and add a new colum Notes
    tree.heading('Notes', text='Notes')

    # Scrollbar
    scrollbar = Scrollbar(i_root, orient = 'vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    tree.pack(side='left', fill='both', expand=True)

    # Adjust column widths based on the data
    def AdjustColumnSizes():
        colIndex = {'File': 0, 'Date': 1, 'Notes': 3}
        for col in colIndex:
            maxWidth = max(
                len(str(item[colIndex[col]])) 
                if len(item) > colIndex[col] and item[colIndex[col]] is not None    # This way we cover for empty columns
                else 0 
                for item in i_CodesData
            )
            tree.column(col, width=maxWidth * 4)                                    # It doesn't really fit, so I'll multiply a bit

    # I need the window to refresh from time to time in case there's new data
    def FillTree():
        existingItems = {tree.item(item, 'values') for item in tree.get_children()}     # Get all the items in the tree in a tuple, only the values
        sortedData = sorted(i_CodesData, key=lambda x: x[1], reverse=True)              # Sort by Date
        if len(existingItems) == 0:                 # If there's no data in the table, just insert as is
            for fileData in sortedData:
                if fileData not in existingItems and fileData[2]!='':                   # Only insert new values, avoid blank codes (this is for the future)
                    tree.insert('', tk.END, values=fileData)
        else:                                       # If there's data, I need to read from the bottom of sortedData, insert at the top of the tree
            for fileData in reversed(sortedData):
                if fileData not in existingItems and fileData[2]!='':                   # Only insert new values, avoid blank codes (this is for the future)
                    tree.insert('', 0, values=fileData)

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
        nonlocal i_CodesData
        i_CodesData = i_RefreshCallback()
        FillTree()
        i_root.after(i_RefreshInterval, refreshTree)

        if gs.configList['firstBoot']==True:        # Open the config window to get the path if this is the first boot
            gs.configList['firstBoot'] = False
            gs.configList['vrchat-log-path'] = GetPossibleVRCPath()
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
    if len(tree.get_children()) > 0:
        AdjustColumnSizes()
    i_root.after(i_RefreshInterval, refreshTree)    # Hook the data refresh event