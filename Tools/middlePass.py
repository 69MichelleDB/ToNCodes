import Tools.xmlTools as xml

# This one will be for those the need to import eachother

def ModifyNode_Call(i_filePath, i_nodeTag, i_newText):
    xml.ModifyNode(i_filePath, i_nodeTag, i_newText)