Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "cmd /c python OctoCamStreamer.py"
oShell.Run strArgs, 0, false