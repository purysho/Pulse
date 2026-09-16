from __future__ import annotations
import json,os,platform,re,subprocess
from pathlib import Path
from .models import ConnectionInfo,ProcessInfo

class ProviderError(RuntimeError): pass

def _run(command:list[str],timeout:float=12.0)->str:
    p=subprocess.run(command,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout,check=False)
    if p.returncode!=0: raise ProviderError(p.stderr.strip() or f"Command failed: {' '.join(command)}")
    return p.stdout

def _json_list(text:str)->list[dict]:
    text=text.strip()
    if not text:return []
    v=json.loads(text)
    if isinstance(v,dict):return [v]
    return [x for x in v if isinstance(x,dict)] if isinstance(v,list) else []

def collect_windows()->list[ProcessInfo]:
    ps=["powershell","-NoProfile","-Command"]
    cim=_json_list(_run(ps+["Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine,WorkingSetSize | ConvertTo-Json -Compress"]))
    try:cpu=_json_list(_run(ps+["Get-Process -ErrorAction SilentlyContinue | Select-Object Id,CPU | ConvertTo-Json -Compress"]))
    except Exception:cpu=[]
    try:rows=_json_list(_run(ps+["Get-NetTCPConnection -ErrorAction SilentlyContinue | Where-Object {$_.State -eq 'Listen' -or $_.State -eq 'Established'} | Select-Object OwningProcess,LocalAddress,LocalPort,RemoteAddress,RemotePort,State | ConvertTo-Json -Compress"]))
    except Exception:rows=[]
    cpu_by={int(r.get('Id',0) or 0):float(r.get('CPU',0) or 0) for r in cpu}; conns={}
    for r in rows:
        pid=int(r.get('OwningProcess',0) or 0); local=f"{r.get('LocalAddress','')}:{r.get('LocalPort','')}"; remote=f"{r.get('RemoteAddress','')}:{r.get('RemotePort','')}"; conns.setdefault(pid,[]).append(ConnectionInfo(pid,local,remote,str(r.get('State',''))))
    out=[]
    for r in cim:
        pid=int(r.get('ProcessId',0) or 0)
        if pid<=0:continue
        out.append(ProcessInfo(pid,int(r.get('ParentProcessId',0) or 0),str(r.get('Name') or 'unknown'),int(r.get('WorkingSetSize',0) or 0),cpu_by.get(pid,0.0),str(r.get('ExecutablePath') or ''),str(r.get('CommandLine') or ''),conns.get(pid,[])))
    return sorted(out,key=lambda p:p.name.lower())

def _linux_connections():
    try:o=_run(["ss","-tunlpH"],6)
    except Exception:return {}
    result={}; rx=re.compile(r"pid=(\d+)")
    for line in o.splitlines():
        parts=line.split()
        if len(parts)<6:continue
        m=rx.search(line)
        if not m:continue
        pid=int(m.group(1)); result.setdefault(pid,[]).append(ConnectionInfo(pid,parts[4],parts[5],parts[1],parts[0].upper()))
    return result

def collect_linux()->list[ProcessInfo]:
    root=Path('/proc'); clk=os.sysconf(os.sysconf_names.get('SC_CLK_TCK','SC_CLK_TCK')); page=os.sysconf('SC_PAGE_SIZE'); conns=_linux_connections(); out=[]
    for item in root.iterdir():
        if not item.name.isdigit():continue
        pid=int(item.name)
        try:
            stat=(item/'stat').read_text(); close=stat.rfind(')'); name=stat[stat.find('(')+1:close]; rest=stat[close+2:].split(); ppid=int(rest[1]); utime=int(rest[11]); stime=int(rest[12]); statm=(item/'statm').read_text().split(); memory=int(statm[1])*page if len(statm)>1 else 0
            try:path=os.readlink(item/'exe')
            except OSError:path=''
            try:command=(item/'cmdline').read_bytes().replace(b'\x00',b' ').decode('utf-8',errors='replace').strip()
            except OSError:command=''
            out.append(ProcessInfo(pid,ppid,name,memory,(utime+stime)/clk,path,command,conns.get(pid,[])))
        except (OSError,ValueError,IndexError):continue
    return sorted(out,key=lambda p:p.name.lower())

def collect_macos()->list[ProcessInfo]:
    o=_run(["ps","-axo","pid=,ppid=,rss=,time=,comm="]); out=[]
    for line in o.splitlines():
        parts=line.strip().split(None,4)
        if len(parts)<5:continue
        try:pid,ppid,rss=int(parts[0]),int(parts[1]),int(parts[2])
        except ValueError:continue
        out.append(ProcessInfo(pid,ppid,Path(parts[4]).name,rss*1024,0.0,parts[4],parts[4],[]))
    return sorted(out,key=lambda p:p.name.lower())

def collect_processes()->list[ProcessInfo]:
    s=platform.system().lower()
    if s=='windows':return collect_windows()
    if s=='linux':return collect_linux()
    if s=='darwin':return collect_macos()
    raise ProviderError(f"Unsupported platform: {platform.system()}")
