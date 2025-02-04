import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

# Create the window
def CreateWindow(i_title, i_width, i_height):
    root = tk.Tk()
    root.title(i_title)
    root.geometry(f"{i_width}x{i_height}")
    return root

# This will allow us to display the XMLs data
def CreateTreeView(i_root, i_CodesData, i_RefreshInterval, i_RefreshCallback):
    tree = ttk.Treeview(i_root, columns=('File', 'Date', 'Code', 'Notes'), show='headings')
    tree.heading('File', text='File')
    tree.heading('Date', text='Date')
    tree.column('Code', width=0, stretch=tk.NO)                 # I'm going to keep Code hidden and add a new colum Notes
    tree.heading('Notes', text='Notes')
    tree.pack(fill=tk.BOTH, expand=True)

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
            tree.column(col, width=maxWidth * 3)                                    # It doesn't really fit, so I'll multiply a bit

    # I need the window to refresh from time to time in case there's new data
    def FillTree():
        existingItems = {tree.item(item, 'values') for item in tree.get_children()}    # Get all the items in the tree in a tuple, only the values
        sortedData = sorted(i_CodesData, key=lambda x: x[1], reverse=True)  # Sort by Date
        for fileData in sortedData:
            if fileData not in existingItems and fileData[2]!='':           # Only insert new values, avoid blank codes (this is for the future)
                tree.insert('', tk.END, values=fileData)

    # Event handler for double click, copies the code to the clipboard (I needed xclip on pop!_os for it to work, on windows there's no need in theory)
    def on_row_click(event):
        selectedItems = tree.selection()
        if selectedItems:
            selectedItem = selectedItems[0]
            file, Date, code = tree.item(selectedItem, 'values')
            pyperclip.copy(code)
            messagebox.showinfo("Copied!", f"Code '{Date}' copied to clipboard")
        else:
            messagebox.showwarning("Warning", "No item selected")

    # This will handle the data refresh once the mainloop engages
    def refreshTree():
        nonlocal i_CodesData
        i_CodesData = i_RefreshCallback()
        FillTree()
        i_root.after(i_RefreshInterval, refreshTree)

    tree.bind('<Double-1>', on_row_click)           # Hook the double click event
    FillTree()                                      # Fill the tree
    if len(tree.get_children()) > 0:
        AdjustColumnSizes()
    i_root.after(i_RefreshInterval, refreshTree)    # Hook the data refresh event