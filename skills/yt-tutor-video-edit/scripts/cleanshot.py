"""CleanShot X .cleanshotvideo <-> Cap-like config (same idea as shotbase.py).
to_cap  <document.json> <out.json>           clips -> timeline.segments, zooms -> timeline.zoomSegments
apply   <document.json> <cap.json> <out.json> cap segments -> clips, zoomSegments -> zooms (timeline seconds)"""
import json,sys,uuid
def load(p): return json.load(open(p))
def to_cap(doc,out):
    d=load(doc)
    segs=[{"recordingSegment":0,"timescale":1.0,"start":c["startTime"],"end":c["startTime"]+c["duration"],"name":None,"_cs":c} for c in d["clips"]]
    zs=[{"start":z["startTimestamp"],"end":z["endTimestamp"],"amount":z["zoomValue"],"mode":"auto","_cs":z} for z in d["zooms"]]
    json.dump({"timeline":{"segments":segs,"zoomSegments":zs,"keyboardSegments":[]},"background":{},"camera":{},"cursor":{},"_source":"cleanshot"},open(out,"w"),indent=2)
def apply(doc,cap,out):
    d,c=load(doc),load(cap)
    d["clips"]=[{"startTime":float(s["start"]),"duration":float(s["end"]-s["start"]),"id":str(uuid.uuid4()).upper()} for s in c["timeline"]["segments"]]
    total=sum(x["duration"] for x in d["clips"]); zs=[]; ids=set()
    for z in c["timeline"].get("zoomSegments") or []:
        m=dict(z.get("_cs") or {"zoomValue":z["amount"],"position":[0.5,0.5],"mode":0})
        m["id"]=m.get("id") if m.get("id") not in ids else None
        m["id"]=m["id"] or str(uuid.uuid4()).upper(); ids.add(m["id"])
        m["startTimestamp"]=float(z["start"]); m["endTimestamp"]=min(float(z["end"]),total); m["zoomValue"]=float(z["amount"])
        if m["endTimestamp"]-m["startTimestamp"]>=0.3: zs.append(m)
    d["zooms"]=sorted(zs,key=lambda m:m["startTimestamp"])
    json.dump(d,open(out,"w"),ensure_ascii=False)
    print(json.dumps({"clips":len(d["clips"]),"duration":f"{int(total//60)}m {round(total%60)}s","zooms":len(zs)}))
{"to_cap":to_cap,"apply":apply}[sys.argv[1]](*sys.argv[2:])
