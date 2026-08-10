from PyInstaller.utils.hooks import collect_submodules

hidden = []
for package in [
    "wa_desktop_connector_core",
    "wa_desktop_connector_cache",
    "wa_desktop_connector_sync",
    "wa_desktop_connector_monitor",
    "wa_desktop_connector_locking",
    "wa_desktop_connector_ui",
    "wa_desktop_connector_installer",
]:
    hidden += collect_submodules(package)

a = Analysis(
    ["launcher.py"],
    pathex=["src"],
    hiddenimports=hidden,
    datas=[],
    binaries=[],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="WA Desktop Connector",
    console=False,
    icon="assets/wa_desktop_connector.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="WA Desktop Connector",
)
