# usage: loudmic.py <project.shotbase> <workdir>  -> <workdir>/microphone.loud.m4a, prints checks
import json,sys,subprocess,re,numpy as np
P,W=sys.argv[1],sys.argv[2]; src=f"{P}/microphone.m4a"; out=f"{W}/microphone.loud.m4a"
r=subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",src,"-af","loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json","-f","null","-"],capture_output=True,text=True)
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
af=(f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample=48000")
subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-af",af,"-c:a","aac","-b:a","192k",out],check=True)
r=subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",out,"-af","loudnorm=print_format=summary","-f","null","-"],capture_output=True,text=True)
print("input", m["input_i"], "LUFS ->", " | ".join(l.strip() for l in r.stderr.splitlines() if re.match(r"Input (Integrated|True)",l.strip())))
def env(p):
    x=np.abs(np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","8000","-f","f32le","-"],capture_output=True).stdout,np.float32)); n=len(x)//8; return x[:n*8].reshape(n,8).mean(1)
a,b=env(src),env(out); print("decoded length ms", len(a), len(b))
n=min(len(a),len(b)); a,b=a[:n]-a[:n].mean(),b[:n]-b[:n].mean()
for s in (0,n//2,n-60000):
    A,B=a[s:s+60000],b[s:s+60000]; k_=len(A)
    print(" window", s//1000, "s offset", max(range(-100,101),key=lambda k: float(np.dot(A[max(0,k):k_+min(0,k)],B[max(0,-k):k_-max(0,k)]))), "ms")
