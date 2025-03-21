import os.path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import glob
import os.path
import Globals as gs
from Tools.webhookTool import SendWebhook
from Tools.errorHandler import ErrorLogging
from Tools.notesTools import ParseContent


#region Common XML

# Function to read XML file
def ReadXml(i_filePath):
    try: 
        tree = ET.parse(i_filePath)
        root = tree.getroot()
        return root
    # In case of XML corruption...
    except ET.ParseError as e:
        if i_filePath == gs._FILE_CONFIG:               # CONFIG FILE corruption
            error = f'Your {gs._FILE_CONFIG} is corrupted, we are going to attempt to regenerate it'
            fileOg = gs._FILE_CONFIG
            if os.path.exists(fileOg):                  # Delete the corrupted config file and create a new one
                os.remove(fileOg)
            defaultConfigFile = os.path.join(gs._FOLDER_TEMPLATES, gs._FILE_CONFIG+'.default')
            with open(defaultConfigFile, 'r') as src, open(gs._FILE_CONFIG, 'w') as dst:
                dst.write(src.read())
        elif i_filePath == os.path.join(gs.configList['codes-folder'], gs._FILE_CONTROL):            # CONTROL FILE corruption
            error = f'Your {gs._FILE_CONTROL} is corrupted, we are going to attempt to regenerate it'
            fileControl = os.path.join(gs.configList['codes-folder'], gs._FILE_CONTROL)
            if os.path.exists(fileControl):                  # Delete the corrupted control file and create a new one
                os.remove(fileControl)
            with open(fileControl, 'w') as file:
                file.write('<?xml version="1.0" ?><Root></Root>')
        elif i_filePath[len(gs.configList['codes-folder'])+1:len(gs.configList['codes-folder'])+11] == 'output_log':    # CODE FILE corruption
            fileCode = i_filePath
            error = f'{fileCode} is corrupted, we are going to attempt to regenerate it'
            if os.path.exists(fileCode):                    # Delete the corrupted code file
                os.remove(fileCode)
            allLogs = GetAllFiles(gs.configList['vrchat-log-path']+'output_log_*.txt')                  # I want control to forget the corrupted file
            fileCodeXML = os.path.join(gs.configList['vrchat-log-path'] ,fileCode.replace('Codes/','').replace('.xml','.txt'))
            allLogs.remove(fileCodeXML)
            CleanControlEntries(os.path.join(gs.configList['codes-folder'], gs._FILE_CONTROL), allLogs) # And we do that here
            with open(fileCode, 'w') as file:
                file.write('<?xml version="1.0" ?><Root></Root>')
            gs.forceRefreshCodes = True                     # We need to tell CodesHunter to refresh and read the Codes again
        else:
            raise Exception
        print(error)
        ErrorLogging(error, True)
        tree = ET.parse(i_filePath)                   # Recover and continue the process as normal
        root = tree.getroot()
        return root
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ReadXml: {e}")


# Function to read the contents of the nodes inside the root
def ReadXmlNodes(i_filePath):
    try:
        root = ReadXml(i_filePath)
        nodesContent = []
        for child in root:
            nodeData = {child.tag: child.text}
            nodesContent.append(nodeData)
        return nodesContent
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ReadXmlNodes: {e}")


# Function to modify a node in the XML file
def ModifyNode(i_filePath, i_nodeTag, i_newText):
    try:
        root = ReadXml(i_filePath)
        for node in root.iter(i_nodeTag):
            node.text = i_newText
        WriteXml(root, i_filePath)
        
        # Let's clean the mess and leave it pretty
        PrettifyXML(root, i_filePath)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ModifyNode: {e}")


# Function to write XML file
def WriteXml(i_root, i_filePath):
    try:
        tree = ET.ElementTree(i_root)
        tree.write(i_filePath)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in WriteXml: {e}")


# Function to find specific Date and modify its sibling Code node
def ModifyCode(i_filePath, i_date, i_code):
    try:
        root = ReadXml(i_filePath)
        for tonCode in root.findall('.//TON-Code'):
            dateNode = tonCode.find('Date')
            if dateNode is not None and dateNode.text == i_date:
                codeNode = tonCode.find('Code')
                if codeNode is not None:
                    codeNode.text = i_code
        WriteXml(root, i_filePath)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ModifyCode: {e}")


# Generic function to get all Node values, given a specific node
def GetNodeValues(i_xmlFile, i_node='.//Date'):
    try:
        nodeValues = set()
        if os.path.exists(i_xmlFile):
            root = ReadXml(i_xmlFile)
            
            for fileElement in root.findall(i_node):
                nodeValues.add(fileElement.text)
            
        return list(nodeValues)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in GetNodeValues: {e}")


# Retrieves everything from every XML file in the given folder
def ReadCodeFiles(folder):
    try:
        files_data = []
        if not gs.writingFlag:
            for file_name in os.listdir(folder):
                if file_name.endswith('.xml'):
                    xmlFile = os.path.join(folder, file_name)
                    root = ReadXml(xmlFile)
                    for ton_code in root.findall('.//TON-Code'):
                        file = ton_code.find('.//File').text if ton_code.find('.//File') is not None else None
                        data = ton_code.find('.//Date').text if ton_code.find('.//Date') is not None else None
                        code = ton_code.find('.//Code').text if ton_code.find('.//Code') is not None else None
                        note = ton_code.find('.//Note').text if ton_code.find('.//Note') is not None else None
                        if code != None:                  # I plan to allow deleting codes, this will help
                            files_data.append((file, data, code, note))
        return files_data
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ReadCodeFiles: {e}")


# Let's check if the xml file has been initialized
def InitializeConfig(i_configFile):
    try:
        result = {}                                             # Dictionary to store all data

        nodes = ReadXmlNodes(i_configFile)                      # retrieve all nodes
        for node in nodes:                                      # iterate each node
            for key, value in node.items(): 
                if key == 'vrchat-log-path':
                    result['firstBoot'] = True if value == 'noinit' else False

                result[key] = value                             # Store the rest of the config data

        return result
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in InitializeConfig: {e}")


# This will get all log files in the specified path
def GetAllFiles(i_path):
    try:
        logFiles = []
        for file in glob.glob(i_path):
            logFiles.append(file)

        return logFiles
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in GetAllFiles: {e}")


def PrettifyXML(i_root, i_file):
    try:
    # Let's clean the mess and leave it pretty
        tree = ET.ElementTree(i_root)
        tree.write(i_file, encoding='utf-8', xml_declaration=True)

        # Add indentations and save it...
        with open(i_file, 'r+') as file:
            xmlContent = file.read()
            xmlDom = minidom.parseString(xmlContent)
            prettyXmlString = xmlDom.toprettyxml(indent="  ")  # Add indentations
            prettyXmlString = "\n".join([line for line in prettyXmlString.split('\n') if line.strip()])   # Remove empty lines
            file.seek(0)
            file.write(prettyXmlString)
            file.truncate()
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in PrettifyXML: {e}")


# This is in case the user updated and their config file is old and missing new fields, it'll add them
def VerifyConfigFields(i_file):
    try:
        defaultConfigFile = os.path.join(gs._FOLDER_TEMPLATES, i_file+'.default')
        
        rootDefault = ReadXml(defaultConfigFile)
        rootConfig = ReadXml(i_file)
        
        for nodeD in rootDefault:
            found = False
            for nodeC in rootConfig:
                if nodeD.tag == nodeC.tag:
                    found = True
                    break
            # If the loop ends and doesn't find a match, insert it 
            if not found:
                print(f"Node {nodeD.tag} not found in {i_file}, adding...")
                newNode = ET.Element(nodeD.tag)
                newNode.text = nodeD.text
                rootConfig.append(newNode)

        WriteXml(rootConfig, i_file)
        PrettifyXML(rootConfig, i_file)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in VerifyConfigFields: {e}")


# region Control File

# Read all data in contro.xml
def ReadControlFile(i_controlFile):
    try:
        controlCursors = []

        xmlFile = i_controlFile
        root = ReadXml(xmlFile)
        for ton_code in root.findall('.//TON-File'):
            file = ton_code.find('.//File').text if ton_code.find('.//File') is not None else None
            date = ton_code.find('.//Date').text if ton_code.find('.//Date') is not None else None
            cursor = ton_code.find('.//Cursor').text if ton_code.find('.//Cursor') is not None else None
            controlCursors.append((file, date, cursor))
        return controlCursors
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ControlFileDates: {e}")


# Insert a new entry to the Control file
def ControlFileInsert(i_controlFile, i_file, i_date, i_cursor):
    try:
        root = ReadXml(i_controlFile)
        tonCode = ET.Element('TON-File')
        ET.SubElement(tonCode, 'File').text = str(i_file)
        ET.SubElement(tonCode, 'Date').text = str(i_date)
        ET.SubElement(tonCode, 'Cursor').text = str(i_cursor)
        root.append(tonCode)
    
        # Let's clean the mess and leave it pretty
        PrettifyXML(root, i_controlFile)

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ControlFileUpdate: {e}")

# Try to update an entry in the control file, if there's no entry, insert a new entry
def ControlFileUpdate(i_controlFile, i_file, i_date, i_cursor):
    try:
        found = False
        root = ReadXml(i_controlFile)
        for tonCode in root.findall('.//TON-File'):
            fileNode = tonCode.find('File')
            if fileNode.text == i_file:
                found = True
                dateNode = tonCode.find('Date')
                dateNode.text = i_date
                cursorNode = tonCode.find('Cursor')
                cursorNode.text = str(i_cursor)
                break
        if found:
            WriteXml(root, i_controlFile)
        else:
           ControlFileInsert(i_controlFile, i_file, i_date, i_cursor)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ModifyCode: {e}")

# Loop the xml file and if there's a file that doesn't exist anymore, delete it from control
def CleanControlEntries(i_controlFile, i_logFiles):
    try: 
        print('Checking for old entries in Control file...')
        root = ReadXml(i_controlFile)
        for tonCode in root.findall('.//TON-File'):
            fileNode = tonCode.find('File')
            if fileNode.text not in i_logFiles:
                print(f"{fileNode.text} doesn't exist anymore, deleting entry from control file.")
                root.remove(tonCode)
        WriteXml(root, i_controlFile)
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in CleanControlEntries: {e}")


# region Populate codes

# Write code in file
def WriteNewCode(i_codesFolder, i_fileName, i_dateTime, i_logContent, i_note):
    gs.writingFlag = True                   # Prevents the gui from accessing while the file is open
    gs.newCodeAdded = True                  # Alerts the gui that there's a new Code
    
    currentLogFile = i_codesFolder + os.path.sep + os.path.basename(i_fileName).replace('.txt', '.xml')
    if not os.path.exists(currentLogFile):
        root = ET.Element('Root')
        root.text = '\n'                    # Make sure it creates <Root></Root> instead of <Root />
        WriteXml(root, currentLogFile)

    root = ReadXml(currentLogFile)
    tonCode = ET.Element('TON-Code')
    ET.SubElement(tonCode, 'File').text = i_fileName
    ET.SubElement(tonCode, 'Date').text = i_dateTime
    ET.SubElement(tonCode, 'Code').text = i_logContent
    ET.SubElement(tonCode, 'Note').text = i_note
    root.append(tonCode)

    # Let's clean the mess and leave it pretty
    PrettifyXML(root, currentLogFile)

    gs.writingFlag = False

# Processes log file in search of data
def PopulateCodes2(i_logFile, i_codesFolder, i_cursor):
    try:
        cursor = int(i_cursor)

        print('Processing modified files, extracting codes...')
        addedDates = []
        
        currentFilePath = os.path.join(i_codesFolder,os.path.basename(i_logFile).replace('.txt', '.xml'))
        auxDates = GetNodeValues(currentFilePath, './/Date')  # Since I'm treating the Date as a PK, we'll use it to discard duplicates
        addedDates = list(set(addedDates).union(auxDates))

        logEntries = []
        # Read each file in search of all ToN codes
        fileNameAux = os.path.basename(i_logFile)
        with open(i_logFile, 'r') as f:
            print(f'[START] Reading file: {fileNameAux}')
            cursor, logEntriesAux = ParseContent(f.read(), fileNameAux, cursor)
            if len(logEntriesAux)>0:
                if logEntriesAux[0][1] not in addedDates:
                    logEntries += logEntriesAux
            print(f'[END] Reading file: {fileNameAux}')

        print(f'Saving codes to XML...')
        # Extract all data into the XML
        for fileName, dateTime, logContent, note in logEntries:
            WriteNewCode(i_codesFolder, fileName, dateTime, logContent, note)

            # Send the webhook
            if gs.configList['discord-webhook'] is not None:
                SendWebhook(dateTime, note, logContent)

        return cursor
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in PopulateCodes2: {e}")
