import socket
class LockManager:
    def __init__(self,client):self.client=client
    def headers(self,token=None):
        h={"X-WA-Machine":socket.gethostname()}
        if token:h["X-WA-Lock-Token"]=token
        return h
    def acquire(self,machine):
        meta=self.client.metadata();return self.client.request(meta["lock_url"],"POST",b"",self.headers())["lock_token"]
    def heartbeat(self,url,token):return self.client.request(url,"POST",b"",self.headers(token))
    def release(self,url,token):return self.client.request(url,"POST",b"",self.headers(token))
