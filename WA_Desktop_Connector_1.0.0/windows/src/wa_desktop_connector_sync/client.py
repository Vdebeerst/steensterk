import ipaddress,json
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen
from wa_desktop_connector_core.errors import ConnectorError,ConflictError
class Client:
    def __init__(self,server,document_id,token):self.server=server.rstrip("/");self.document_id=str(document_id);self.token=token;self._validate(self.server)
    def _validate(self,url):
        p=urlparse(url);local=False
        try:local=ipaddress.ip_address(p.hostname or "").is_private
        except ValueError:local=(p.hostname or "").lower()=="localhost"
        if p.scheme!="https" and not (p.scheme=="http" and local):raise ConnectorError("HTTPS is required for public servers.")
    def absolute(self,url):return urljoin(self.server+"/",url.lstrip("/"))
    def request(self,url,method="GET",data=None,extra=None,raw=False):
        url=self.absolute(url);self._validate(url);headers={"Authorization":f"Bearer {self.token}","User-Agent":"WA-Desktop-Connector/0.2.4"};headers.update(extra or {})
        try:
            with urlopen(Request(url,method=method,data=data,headers=headers),timeout=90) as r:return r.read() if raw else json.loads(r.read().decode())
        except HTTPError as e:
            body=e.read().decode("utf-8","replace")
            if e.code==409:raise ConflictError(body)
            raise ConnectorError(f"HTTP {e.code}: {body}") from e
        except URLError as e:raise ConnectorError(f"Network error: {e.reason}") from e
    def metadata(self):return self.request(f"/wa_documents_desktop/api/document/{self.document_id}")
    def download(self,url,target):
        tmp=Path(str(target)+".part");tmp.write_bytes(self.request(url,raw=True));tmp.replace(target)
    def upload(self,url,path,etag,lock):
        headers={"Content-Type":"application/octet-stream","X-WA-Filename":Path(path).name,"X-WA-Lock-Token":lock}
        if etag:headers["If-Match"]=etag
        return self.request(url,"PUT",Path(path).read_bytes(),headers)
