from dataclasses import asdict,dataclass
import json,re
from pathlib import Path
from wa_desktop_connector_core.config import CACHE
@dataclass
class State:
    server:str;document_id:str;token:str;path:str;etag:str|None;lock_token:str;metadata:dict
class Store:
    def __init__(self,document_id):self.root=CACHE/str(document_id);self.root.mkdir(parents=True,exist_ok=True)
    def target(self,name):
        safe=re.sub(r'[<>:"/\\|?*]+','_',Path(name).name).strip() or f"document-{self.root.name}"
        return self.root/safe
    def save(self,state):
        p=self.root/"state.json";p.write_text(json.dumps(asdict(state),indent=2),encoding="utf-8");return p

def load(path):return State(**json.loads(Path(path).read_text(encoding="utf-8")))
def save(path,state):Path(path).write_text(json.dumps(asdict(state),indent=2),encoding="utf-8")
