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
    tree = ttk.Treeview(i_root, columns=('File', 'Date', 'Code'), show='headings')
    tree.heading('File', text='File')
    tree.heading('Date', text='Date')
    tree.heading('Code', text='Code')
    tree.pack(fill=tk.BOTH, expand=True)

    # I need the window to refresh from time to time in case there's new data
    # TODO: Optimize so I don't need to empty the wole tree and refill it, that way we ovoid the flicker
    def FillTree():
        for item in tree.get_children():
            tree.delete(item)
        for fileData in i_CodesData:
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
    i_root.after(i_RefreshInterval, refreshTree)    # Hook the data refresh event