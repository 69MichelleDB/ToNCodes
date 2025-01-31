import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import glob
import os.path

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


# Generic function to get all Node values, given a specific node
def GetNodeValues(i_xmlFile, i_node='.//Date'):
    nodeValues = set()
    if os.path.exists(i_xmlFile):
        tree = ET.parse(i_xmlFile)
        root = tree.getroot()
        
        for fileElement in root.findall(i_node):
            nodeValues.add(fileElement.text)
        
    return list(nodeValues)


# Let's check if the xml file has been initialized
def InitializeConfig(i_configFile):
    result = {}                                             # Dictionary to store all data

    nodes = ReadXmlNodes(i_configFile)                      # retrieve all nodes
    for node in nodes:                                      # iterate each node
        for key, value in node.items(): 
            if key == 'vrchat-log-path':
                if value == 'noinit':                       # if it's not initialized, ask for the path
                    print('Reading config file')
                    print('Please, set the path to the VRChat logs files')
                    print('Win: c:/users/<user>/AppData/LocalLow/VRChat/VRChat/') 
                    print('Ubuntu/Pop!_OS: ~/.steam/debian-installation/steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/: ')
                    print('Arch: ~/.local/share/Steam/steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/: ')
                    print('Flatpak (this one, not sure): ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/')

                    while True:
                        vrchatLogPath = input()               # Wait for user input
                        if vrchatLogPath.strip():             # Check if input is not empty
                            break
                        print("Path cannot be empty. Please enter a valid path.")
                    ModifyNode('config.xml', key, vrchatLogPath)
                    result['firstBoot'] = True
                    result[key] = vrchatLogPath
                else:
                    print('Reading config file')
                    result['firstBoot'] = False
                    result[key] = value
            else:
                result[key] = value                         # Store the rest of the config data

    return result


# This will get all log files in the specified path
def GetAllFiles(i_path):
    logFiles = []
    for file in glob.glob(i_path):
        logFiles.append(file)

    return logFiles


def PopulateCodes(i_logFiles, i_keywordStart, i_keywordEnd, i_endDateIndex, i_codesFolder):
    print('Processing modified files, extracting codes...')
    addedDates = []
    
    for file in i_logFiles:
        currentFilePath = i_codesFolder + '/' + os.path.basename(file).replace('.txt', '.xml')
        auxDates = GetNodeValues(currentFilePath, './/Date')  # Since I'm treating the Date as a PK, we'll use it to discard duplicates
        addedDates = list(set(addedDates + auxDates))

    logEntries = []
    # Read each file in search of all ToN codes
    for file in i_logFiles:
        print(f'[START] Reading file: {os.path.basename(file)}')
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
                fileName = os.path.basename(file)
                if dateTime not in addedDates:              # check the date is not inserted already
                    print(f'Code {dateTime} is new')
                    logEntries.append((fileName, dateTime, logContent))
                else:
                    print(f'Code {dateTime} is not new')
                startCursor = endIndex + len(i_keywordEnd)
            print(f'[END] Reading file: {os.path.basename(file)}')

    print(f'Saving codes to XML...')
    # Extract all data into the XML
    for fileName, dateTime, logContent in logEntries:
        currentLogFile = i_codesFolder + '/' + os.path.basename(fileName).replace('.txt', '.xml')
        if not os.path.exists(currentLogFile):
            root = ET.Element('Root')
            root.text = '\n'                    # Make sure it creates <Root></Root> instead of <Root />
            WriteXml(root, currentLogFile)
        root = ReadXml(currentLogFile)
        tonCode = ET.Element('TON-Code')
        dateElement = ET.SubElement(tonCode, 'File')
        dateElement.text = fileName
        dateElement = ET.SubElement(tonCode, 'Date')
        dateElement.text = dateTime
        codeElement = ET.SubElement(tonCode, 'Code')
        codeElement.text = logContent
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
