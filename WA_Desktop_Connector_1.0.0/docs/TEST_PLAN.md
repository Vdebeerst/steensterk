# Staging test plan

1. Install the five add-ons on Odoo.sh staging.
2. Install the unsigned test Setup EXE on one Windows test machine.
3. Open a disposable DOCX from Documents.
4. Verify the local copy opens in Word.
5. Save once and verify a successful upload appears in the synchronization log.
6. Modify the Odoo attachment while the local copy is open, then save locally and verify a conflict is reported rather than overwritten.
7. Verify another user receives HTTP 423 while the active lock is valid.
8. Close the editor and confirm the lock is released after the configured idle window.
9. Test expired-token and temporary-network-failure behavior.
10. Only after all checks pass, repeat on production with a non-critical file.
