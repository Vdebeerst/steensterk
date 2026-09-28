def _show(title,message,flags):
    try:
        import ctypes;ctypes.windll.user32.MessageBoxW(0,message,title,flags)
    except Exception:pass
def info(message):_show("WA Desktop Connector",message,0x40)
def error(message):_show("WA Desktop Connector",message,0x10)
