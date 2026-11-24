# usage: add_zooms.py NEW.json zooms.json  (zooms: [[srcStart, srcEnd, anchorX, anchorY, label], ...]) -> manual 1.5x zooms
import json,sys,uuid
p=sys.argv[1]; cfg=json.load(open(p)); segs=cfg["timeline"]["segments"]
def tl(S):
    acc=0
    for s in segs:
        if S<s["start"]: return acc
        if S<=s["end"]: return acc+S-s["start"]
        acc+=s["end"]-s["start"]
    return acc
zs=[]
for a,b,x,y,w in json.load(open(sys.argv[2])):
    s,e=tl(a),tl(b)
    sb={"intensity":0,"isDisabled":False,"positionX":0,"positionY":0,"rotationX":0,"rotationY":0,"rotationZ":0,
        "zoomAnchorX":x,"zoomAnchorY":y,"zoomMode":"manual","zoom":150,"id":str(uuid.uuid4()).upper()}
    zs.append({"start":round(s,3),"end":round(e,3),"amount":1.5,"mode":"manual","_shotbase":sb})
    print(f"{int(s//60):02d}:{s%60:04.1f}-{int(e//60):02d}:{e%60:04.1f} ({e-s:4.1f}s) {w}")
cfg["timeline"]["zoomSegments"]=zs; json.dump(cfg,open(p,"w"),indent=2)
