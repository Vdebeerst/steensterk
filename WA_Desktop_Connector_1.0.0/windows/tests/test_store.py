from wa_desktop_connector_cache.store import Store
def test_safe_name(tmp_path,monkeypatch):
    assert Store("1").target('bad:name.docx').name=='bad_name.docx'
