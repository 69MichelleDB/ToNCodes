import os

# To avoid uploading my config files we'll have .defaults and just duplicate them if they don't exist
def CreateFromDefault(i_file):
    if not os.path.exists(i_file):                    # If the file doesn't exist, duplicate the template
        print(f'The {os.path.basename(i_file)} file does not exist, creating...')
        defaultConfigFile = os.path.join('Templates/', i_file, '.default')
        if os.path.exists(defaultConfigFile):
            with open(defaultConfigFile, 'r') as src, open(i_file, 'w') as dst:
                dst.write(src.read())
        else:
            raise FileNotFoundError(f"Default template file '{defaultConfigFile}' not found.")

# Pass it a list of files and obtain a dictionary with the file name and the date modified
def GetDateModified(i_files):
    filesDict = {}    
    for file in i_files:
        filesDict[file] = os.path.getmtime(file)

    return filesDict


# Pass it a pair of dictionaries with current an previous dates, return only the ones we need to check
def GetModifiedFiles(i_currentDates, i_previousDates):
    filesToCheck = []    
    for file in i_currentDates:
        if file not in i_previousDates or i_currentDates[file] != i_previousDates[file]:    # if the file is new or if the date has changed
            filesToCheck.append(file)
            print(f'{os.path.basename(file)} was modified({i_currentDates[file]}), adding to list')

    return filesToCheck