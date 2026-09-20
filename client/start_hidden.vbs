' Lance le client en arriere-plan, sans fenetre de console.
' Le mod UE4SS l'appelle automatiquement au demarrage du jeu (client_path.txt) ;
' le client se ferme tout seul quand le jeu se ferme. Pour l'arreter : stop.bat.
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = dir
shell.Run """" & dir & "\.venv\Scripts\pythonw.exe"" """ & dir & "\presence.py""", 0, False
