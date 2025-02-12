import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import glob
import os.path
import Globals as gs
from Tools.webhookTool import SendWebhook


# Function to read XML file
def ReadXml(i_filePath):
    tree = ET.parse(i_filePath)
    root = tree.getroot()
    return root


# Function to read the contents of the nodes inside the root
def ReadXmlNodes(i_filePath):
    root = ReadXml(i_filePath)
    nodesContent = []
    for child in root:
        nodeData = {child.tag: child.text}
        nodesContent.append(nodeData)
    return nodesContent


# Function to modify a node in the XML file
def ModifyNode(i_filePath, i_nodeTag, i_newText):
    root = ReadXml(i_filePath)
    for node in root.iter(i_nodeTag):
        node.text = i_newText
    WriteXml(root, i_filePath)


# Function to write XML file
def WriteXml(i_root, i_filePath):
    tree = ET.ElementTree(i_root)
    tree.write(i_filePath)


# Function to find specific Date and modify its sibling Code node
def ModifyCode(i_filePath, i_date, i_code):
    root = ReadXml(i_filePath)
    for tonCode in root.findall('.//TON-Code'):
        dateNode = tonCode.find('Date')
        if dateNode is not None and dateNode.text == i_date:
            codeNode = tonCode.find('Code')
            if codeNode is not None:
                codeNode.text = i_code
    WriteXml(root, i_filePath)


# Generic function to get all Node values, given a specific node
def GetNodeValues(i_xmlFile, i_node='.//Date'):
    nodeValues = set()
    if os.path.exists(i_xmlFile):
        root = ReadXml(i_xmlFile)
        
        for fileElement in root.findall(i_node):
            nodeValues.add(fileElement.text)
        
    return list(nodeValues)


# Retrieves everything from every XML file in the given folder
def ReadCodeFiles(folder):
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


# Let's check if the xml file has been initialized
def InitializeConfig(i_configFile):
    result = {}                                             # Dictionary to store all data

    nodes = ReadXmlNodes(i_configFile)                      # retrieve all nodes
    for node in nodes:                                      # iterate each node
        for key, value in node.items(): 
            if key == 'vrchat-log-path':
                result['firstBoot'] = True if value == 'noinit' else False

            result[key] = value                             # Store the rest of the config data

    return result


# This will get all log files in the specified path
def GetAllFiles(i_path):
    logFiles = []
    for file in glob.glob(i_path):
        logFiles.append(file)

    return logFiles


# Changes the Path in the XML for the change path gui setting
def ChangeConfigFileValue(i_configFile, i_config, i_path):
    ModifyNode(i_configFile, i_config, i_path)

# TODO: #8 Optimize log reading, @69MichelleDB
# I'm considering redoing the way I handle the log reading to avoid reading the whole file
# whenever there's a modification by storing the last cursor position, that way we should be able to also handle things related to the Note's field.
def PopulateCodes(i_logFiles, i_keywordStart, i_keywordEnd, i_endDateIndex, i_codesFolder):
    print('Processing modified files, extracting codes...')
    addedDates = []
    
    for file in i_logFiles:
        currentFilePath = os.path.join(i_codesFolder,os.path.basename(file).replace('.txt', '.xml'))
        auxDates = GetNodeValues(currentFilePath, './/Date')  # Since I'm treating the Date as a PK, we'll use it to discard duplicates
        addedDates = list(set(addedDates).union(auxDates))

    logEntries = []
    # Read each file in search of all ToN codes
    for file in i_logFiles:
        fileNameAux = os.path.basename(file)
        print(f'[START] Reading file: {fileNameAux}')
        with open(file, 'r') as f:
            content = f.read()
            startCursor = 0
            while True:                                     # There might be multiple codes in the same file, iterate until done
                startCursor = content.find(i_keywordStart, startCursor)
                if startCursor == -1:                       # If there's no codes, get out
                    break
                # If we find codes, otherwise start parsing the data to split code and datetime
                print('Code found...')
                endIndex = content.find(i_keywordEnd, startCursor)
                logContent = content[startCursor + len(i_keywordStart):endIndex]
                logLineStart = content.rfind('\n', 0, startCursor) + 1
                dateTime = content[logLineStart:startCursor].strip().split(i_endDateIndex)[0]
                note = 'No notes'                                   # TODO: Add logic to process what note goes here
                if dateTime not in addedDates:                      # check the date is not inserted already
                    print(f'Code {dateTime} is new')
                    logEntries.append((fileNameAux, dateTime, logContent, note))
                else:
                    print(f'Code {dateTime} is not new')
                startCursor = endIndex + len(i_keywordEnd)

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