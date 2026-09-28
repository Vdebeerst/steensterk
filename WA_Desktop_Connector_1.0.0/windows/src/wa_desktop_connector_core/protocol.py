from dataclasses import dataclass
from urllib.parse import urlparse,parse_qs
from .errors import ConnectorError
@dataclass
class Request: action:str; values:dict[str,str]
def parse(url):
    p=urlparse(url)
    if p.scheme.lower()!="wa":raise ConnectorError("Invalid protocol.")
    vals={k:v[-1] for k,v in parse_qs(p.query).items()}
    return Request((p.netloc or p.path).strip("/").lower(),vals)
