import sys

def command():
    if getattr(sys,"frozen",False):return f'"{sys.executable}" "%1"'
    return f'"{sys.executable}" -m wa_desktop_connector_core.app "%1"'
def install():
    if sys.platform!="win32":raise RuntimeError("Windows only")
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r"Software\Classes\wa") as k:
        winreg.SetValueEx(k,"",0,winreg.REG_SZ,"URL:WA Desktop Connector");winreg.SetValueEx(k,"URL Protocol",0,winreg.REG_SZ,"")
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r"Software\Classes\wa\shell\open\command") as k:winreg.SetValueEx(k,"",0,winreg.REG_SZ,command())
