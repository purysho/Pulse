from __future__ import annotations
import json,threading,tkinter as tk
from pathlib import Path
from tkinter import filedialog,messagebox,ttk
from .models import ProcessInfo
from .providers import collect_processes

BG="#090d12"; PANEL="#111821"; PANEL2="#17222d"; TEXT="#eef3f7"; MUTED="#8293a4"; ACCENT="#4ed8d2"; BLUE="#5ca8ff"; GOLD="#e8c46c"

def format_bytes(value:int)->str:
    a=float(value)
    for u in ("B","KB","MB","GB","TB"):
        if a<1024 or u=="TB":return f"{a:.0f} {u}" if u in {"B","KB"} else f"{a:.1f} {u}"
        a/=1024
    return f"{a:.1f} TB"

class PulseApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("Pulse — process relationship monitor"); self.geometry("1260x790"); self.minsize(980,640); self.configure(bg=BG); self.processes=[]; self.filtered=[]; self.by_pid={}; self.auto_refresh=tk.BooleanVar(value=True); self.interval=tk.StringVar(value="3"); self.filter_var=tk.StringVar(); self._refresh_after=None; self._style(); self._build(); self.filter_var.trace_add("write",lambda *_:self._apply_filter()); self.after(100,self.refresh); self.protocol("WM_DELETE_WINDOW",self._close)
    def _style(self):
        s=ttk.Style(self); s.theme_use("clam"); s.configure("TFrame",background=BG); s.configure("TLabel",background=BG,foreground=TEXT); s.configure("Muted.TLabel",background=BG,foreground=MUTED); s.configure("Title.TLabel",background=BG,foreground=TEXT,font=("Segoe UI Semibold",22)); s.configure("TButton",background=PANEL2,foreground=TEXT,borderwidth=0,padding=(11,8)); s.configure("Accent.TButton",background=ACCENT,foreground="#051313",padding=(14,9),font=("Segoe UI Semibold",10)); s.configure("Treeview",background=PANEL,fieldbackground=PANEL,foreground=TEXT,rowheight=27,borderwidth=0); s.configure("Treeview.Heading",background=PANEL2,foreground=MUTED,borderwidth=0); s.map("Treeview",background=[("selected","#173945")])
    def _build(self):
        h=ttk.Frame(self); h.pack(fill="x",padx=20,pady=(18,10)); ttk.Label(h,text="Pulse",style="Title.TLabel").pack(side="left"); ttk.Label(h,text="  see what is running — and what it is connected to",style="Muted.TLabel").pack(side="left",pady=(7,0)); ttk.Button(h,text="Export snapshot",command=self._export).pack(side="right"); ttk.Button(h,text="Refresh",style="Accent.TButton",command=self.refresh).pack(side="right",padx=(0,8)); t=ttk.Frame(self); t.pack(fill="x",padx=20,pady=(0,10)); tk.Label(t,text="Filter",bg=BG,fg=MUTED).pack(side="left"); tk.Entry(t,textvariable=self.filter_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=38).pack(side="left",padx=(8,18),ipady=6); tk.Checkbutton(t,text="Auto refresh",variable=self.auto_refresh,bg=BG,fg=TEXT,selectcolor=PANEL2,activebackground=BG,activeforeground=TEXT,command=self._schedule).pack(side="left"); tk.Label(t,text="every",bg=BG,fg=MUTED).pack(side="left",padx=(12,5)); tk.Entry(t,textvariable=self.interval,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=4).pack(side="left",ipady=4); tk.Label(t,text="seconds",bg=BG,fg=MUTED).pack(side="left",padx=(5,0)); self.summary=ttk.Label(t,text="Collecting…",style="Muted.TLabel"); self.summary.pack(side="right")
        p=ttk.Panedwindow(self,orient="horizontal"); p.pack(fill="both",expand=True,padx=18,pady=(0,18)); left=ttk.Frame(p); right=ttk.Frame(p); p.add(left,weight=3); p.add(right,weight=2); self.tree=ttk.Treeview(left,columns=("pid","ppid","memory","cpu","ports"),show="tree headings"); self.tree.heading("#0",text="Process")
        for col,title,width in (("pid","PID",72),("ppid","Parent",72),("memory","Memory",88),("cpu","CPU time",82),("ports","TCP",55)):self.tree.heading(col,text=title); self.tree.column(col,width=width,anchor="e")
        self.tree.column("#0",width=230); self.tree.pack(fill="both",expand=True); self.tree.bind("<<TreeviewSelect>>",lambda _:self._select()); tabs=ttk.Notebook(right); tabs.pack(fill="both",expand=True); details=ttk.Frame(tabs); relations=ttk.Frame(tabs); network=ttk.Frame(tabs); tabs.add(details,text="Details"); tabs.add(relations,text="Relations"); tabs.add(network,text="Network"); self.detail_text=tk.Text(details,bg=PANEL,fg=TEXT,relief="flat",font=("Cascadia Mono",9),padx=12,pady=10,wrap="word"); self.detail_text.pack(fill="both",expand=True); self.canvas=tk.Canvas(relations,bg=PANEL,highlightthickness=0); self.canvas.pack(fill="both",expand=True); self.network_tree=ttk.Treeview(network,columns=("state","local","remote"),show="headings")
        for col,title,width in (("state","State",90),("local","Local",180),("remote","Remote",180)):self.network_tree.heading(col,text=title); self.network_tree.column(col,width=width,anchor="w")
        self.network_tree.pack(fill="both",expand=True)
    def refresh(self):
        if self._refresh_after:self.after_cancel(self._refresh_after); self._refresh_after=None
        self.summary.configure(text="Collecting…",foreground=MUTED); selected=self._selected_pid()
        def work():
            try:data=collect_processes()
            except Exception as e:self.after(0,lambda:self._error(str(e))); return
            self.after(0,lambda:self._set_data(data,selected))
        threading.Thread(target=work,daemon=True).start()
    def _set_data(self,data,selected):
        self.processes=data; self.by_pid={p.pid:p for p in data}; self._apply_filter(selected); tcp=sum(len(p.connections) for p in data); mem=sum(p.memory_bytes for p in data); self.summary.configure(text=f"{len(data)} processes  ·  {tcp} TCP links  ·  {format_bytes(mem)} working set",foreground=ACCENT); self._schedule()
    def _apply_filter(self,selected=None):
        term=self.filter_var.get().strip().lower(); self.filtered=[p for p in self.processes if not term or term in p.name.lower() or term in str(p.pid) or term in p.path.lower() or term in p.command_line.lower()]; self.tree.delete(*self.tree.get_children())
        for p in self.filtered:self.tree.insert("","end",iid=str(p.pid),text=p.name,values=(p.pid,p.ppid or "—",format_bytes(p.memory_bytes),f"{p.cpu_seconds:.1f}s",len(p.connections)))
        if selected and self.tree.exists(str(selected)):self.tree.selection_set(str(selected)); self._select()
    def _selected_pid(self):
        s=self.tree.selection(); return int(s[0]) if s else None
    def _select(self):
        pid=self._selected_pid()
        if pid is None or pid not in self.by_pid:return
        p=self.by_pid[pid]; parent=self.by_pid.get(p.ppid); children=[c for c in self.processes if c.ppid==p.pid]; lines=[p.name,"="*min(70,max(8,len(p.name))),f"PID:        {p.pid}",f"Parent PID: {p.ppid or '—'}"+(f"  ({parent.name})" if parent else ""),f"Memory:     {format_bytes(p.memory_bytes)}",f"CPU time:   {p.cpu_seconds:.2f}s",f"TCP links:  {len(p.connections)}","",f"Path:\n{p.path or 'unavailable'}","",f"Command line:\n{p.command_line or 'unavailable'}"]; self.detail_text.delete("1.0","end"); self.detail_text.insert("1.0","\n".join(lines)); self.network_tree.delete(*self.network_tree.get_children())
        for i,c in enumerate(p.connections):self.network_tree.insert("","end",iid=str(i),values=(c.state,c.local,c.remote))
        self._draw(p,parent,children)
    def _draw(self,p,parent,children):
        c=self.canvas; c.delete("all"); c.update_idletasks(); w=max(c.winfo_width(),420); h=max(c.winfo_height(),360); cx=w/2; cy=h/2
        if parent:self._node(cx,70,parent.name,parent.pid,BLUE,130); c.create_line(cx,105,cx,cy-50,fill="#385363",width=2,arrow="last")
        self._node(cx,cy,p.name,p.pid,ACCENT,160)
        shown=children[:8]
        if not shown:c.create_text(cx,cy+80,text="no visible child processes",fill=MUTED,font=("Segoe UI",9)); return
        gap=min(140,(w-80)/max(1,len(shown))); start=cx-gap*(len(shown)-1)/2; y=h-75
        for i,ch in enumerate(shown):
            x=start+gap*i; c.create_line(cx,cy+42,x,y-36,fill="#385363",width=2,arrow="last"); self._node(x,y,ch.name,ch.pid,GOLD,112)
    def _node(self,x,y,name,pid,color,width):
        c=self.canvas; ht=58; c.create_rectangle(x-width/2,y-ht/2,x+width/2,y+ht/2,fill=PANEL2,outline=color,width=2); c.create_text(x,y-8,text=name[:22],fill=TEXT,font=("Segoe UI Semibold",10)); c.create_text(x,y+12,text=f"PID {pid}",fill=MUTED,font=("Cascadia Mono",8))
    def _schedule(self):
        if self._refresh_after:self.after_cancel(self._refresh_after); self._refresh_after=None
        if self.auto_refresh.get():
            try:s=max(1,float(self.interval.get() or 3))
            except ValueError:s=3
            self._refresh_after=self.after(int(s*1000),self.refresh)
    def _error(self,text):self.summary.configure(text="Collection failed",foreground="#ff7373"); messagebox.showerror("Pulse",text,parent=self); self._schedule()
    def _export(self):
        p=filedialog.asksaveasfilename(parent=self,defaultextension=".json",initialfile="pulse-snapshot.json",filetypes=[("JSON","*.json")])
        if p:Path(p).write_text(json.dumps([x.to_dict() for x in self.processes],indent=2,ensure_ascii=False),encoding="utf-8")
    def _close(self):
        if self._refresh_after:self.after_cancel(self._refresh_after)
        self.destroy()

def main():PulseApp().mainloop()
