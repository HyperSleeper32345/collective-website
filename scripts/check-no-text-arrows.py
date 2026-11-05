# C-SITE-ARROW-1: no arrow character, emoji or variation selector 16 in any served file. Run from the repository root; exits 1 on a hit.
import re,sys,subprocess
files=[f for f in subprocess.run(['git','ls-files','-co','--exclude-standard'],capture_output=True,text=True).stdout.split() if re.search(r'\.(html|js|mjs|css|svg|json|txt|xml)$',f) and not f.startswith(('site-src/','scripts/'))]
pat=re.compile('[←-⇿⬀-⯿➠-➿️⃣⌀-⏿☀-➿\U0001F000-\U0001FAFF]|&(?:nearr|rarr|larr|uarr|darr|harr|swarr|searr|nwarr);|&#(?:x21[9a-f][0-9a-f]|8[56][0-9][0-9]);',re.I)
n=0
for f in files:
    t=open(f,encoding='utf-8',errors='replace').read()
    for m in pat.finditer(t):
        n+=1; print(f, hex(ord(m.group()[0])), repr(t[max(0,m.start()-50):m.end()+20]))
print("hits",n,"files",len(files)); sys.exit(1 if n else 0)
