Set WshShell = CreateObject("WScript.Shell")
strPath = WScript.ScriptFullName
strFolder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(strPath)
WshShell.Run "pythonw """ & strFolder & "\main.py""", 0, False
