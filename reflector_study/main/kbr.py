import win32com.client as client
wsh = client.Dispatch('WScript.Shell')
wsh.AppActivate("SAP2000")
wsh.SendKeys("{RIGHT}{ENTER}")
