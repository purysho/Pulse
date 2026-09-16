from __future__ import annotations
from dataclasses import asdict,dataclass,field
from typing import Any

@dataclass
class ConnectionInfo:
    pid:int
    local:str
    remote:str
    state:str
    protocol:str="TCP"
    def to_dict(self)->dict[str,Any]: return asdict(self)

@dataclass
class ProcessInfo:
    pid:int
    ppid:int
    name:str
    memory_bytes:int=0
    cpu_seconds:float=0.0
    path:str=""
    command_line:str=""
    connections:list[ConnectionInfo]=field(default_factory=list)
    def to_dict(self)->dict[str,Any]: return asdict(self)
