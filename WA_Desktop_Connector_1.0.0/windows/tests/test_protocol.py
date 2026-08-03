from wa_desktop_connector_core.protocol import parse
def test_protocol():
    r=parse("wa://open?server=https%3A%2F%2Fexample.com&document_id=1&access_token=x")
    assert r.action=="open" and r.values["document_id"]=="1"
