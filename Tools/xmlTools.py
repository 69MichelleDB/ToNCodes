import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import glob
import os.path
import Globals as gs
from Tools.webhookTool import SendWebhook
from Tools.errorHandler import ErrorLogging


# Function to read XML file
def ReadXml(i_filePath):
    try: 
        tree = ET.parse(i_filePath)
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
        if not os.path.exists(i_controlFile):
            root = ET.Element('Root')
            root.text = '\n'                    # Make sure it creates <Root></Root> instead of <Root />
            WriteXml(root, i_controlFile)

        root = ReadXml(i_controlFile)
        tonCode = ET.Element('TON-File')
        ET.SubElement(tonCode, 'File').text = str(i_file)
        ET.SubElement(tonCode, 'Date').text = str(i_date)
        ET.SubElement(tonCode, 'Cursor').text = str(i_cursor)
        root.append(tonCode)
    
        # Let's clean the mess and leave it pretty
        tree = ET.ElementTree(root)
        tree.write(i_controlFile, encoding='utf-8', xml_declaration=True)

        # Add indentations and save it...
        with open(i_controlFile, 'r+') as file:
            xmlContent = file.read()
            xmlDom = minidom.parseString(xmlContent)
            prettyXmlString = xmlDom.toprettyxml(indent="  ")  # Add indentations
            prettyXmlString = "\n".join([line for line in prettyXmlString.split('\n') if line.strip()])   # Remove empty lines
            file.seek(0)
            file.write(prettyXmlString)
            file.truncate()

    except Exception as e:
        print(e)
        ErrorLogging(f"Error in ControlFileUpdate: {e}")

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
        print(f'[START] Reading file: {fileNameAux}')
        with open(i_logFile, 'r') as f:
            content = f.read()
            while True:                                     # There might be multiple codes in the same file, iterate until done
                cursorLastPos = cursor
                cursor = content.find("Log        -  [START]", cursorLastPos)
                if cursor == -1:                       # If there's no codes, get out
                    cursor = cursorLastPos
                    break
                # If we find codes, otherwise start parsing the data to split code and datetime
                print('Code found...')
                endIndex = content.find("[END]", cursor)
                logContent = content[cursor + len("Log        -  [START]"):endIndex]
                logLineStart = content.rfind('\n', 0, cursor) + 1
                dateTime = content[logLineStart:cursor].strip().split(" Log")[0]
                note = 'No notes'                                   # TODO: Add logic to process what note goes here
                if dateTime not in addedDates:                      # check the date is not inserted already
                    print(f'Code {dateTime} is new')
                    logEntries.append((fileNameAux, dateTime, logContent, note))
                else:
                    print(f'Code {dateTime} is not new')
                cursor = endIndex + len("[END]")

            print(f'[END] Reading file: {fileNameAux}')

        print(f'Saving codes to XML...')
        # Extract all data into the XML
        for fileName, dateTime, logContent, note in logEntries:
            currentLogFile = i_codesFolder + os.path.sep + os.path.basename(fileName).replace('.txt', '.xml')
            if not os.path.exists(currentLogFile):
                root = ET.Element('Root')
                root.text = '\n'                    # Make sure it creates <Root></Root> instead of <Root />
                WriteXml(root, currentLogFile)

            root = ReadXml(currentLogFile)
            tonCode = ET.Element('TON-Code')
            ET.SubElement(tonCode, 'File').text = fileName
            ET.SubElement(tonCode, 'Date').text = dateTime
            ET.SubElement(tonCode, 'Code').text = logContent
            ET.SubElement(tonCode, 'Note').text = note
            root.append(tonCode)
        
            # Let's clean the mess and leave it pretty
            tree = ET.ElementTree(root)
            tree.write(currentLogFile, encoding='utf-8', xml_declaration=True)

            # Add indentations and save it...
            with open(currentLogFile, 'r+') as file:
                xmlContent = file.read()
                xmlDom = minidom.parseString(xmlContent)
                prettyXmlString = xmlDom.toprettyxml(indent="  ")  # Add indentations
                prettyXmlString = "\n".join([line for line in prettyXmlString.split('\n') if line.strip()])   # Remove empty lines
                file.seek(0)
                file.write(prettyXmlString)
                file.truncate()

            # Send the webhook
            if gs.configList['discord-webhook'] is not None:
                SendWebhook(dateTime, logContent)

        return cursor
    except Exception as e:
        print(e)
        ErrorLogging(f"Error in PopulateCodes2: {e}")
