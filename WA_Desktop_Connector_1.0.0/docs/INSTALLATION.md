# Installation

## Odoo 19

Copy all folders from `odoo_addons` into the custom-addons repository. Update the Apps list and install **WA Documents Desktop Admin**. Dependencies install the other four add-ons automatically.

Configure the public base URL in Settings. Public servers must use HTTPS. Local/private development addresses may use HTTP.

## Windows developer build

Requirements:

- Windows 10 or 11, 64-bit
- Python 3.12 or 3.13
- Inno Setup 6 for the Setup EXE

Run PowerShell:

```powershell
cd windows
.\build_installer.ps1
```

Output:

```text
dist\WA_Desktop_Connector_Setup_0.2.4.exe
```

## Client installation

Run the Setup EXE. It installs the application, registers `wa://`, adds startup integration, and registers an uninstaller. No separate Python installation is needed.
