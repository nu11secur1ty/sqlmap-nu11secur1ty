# How to use
1. Permissions
```
chmod +x msf_sqli_auto_rb_generator.py
```
2. run it
```
python3 msf_sqli_auto_rb_generator.py
```

3. Provide:

output filename (e.g., sacco_auto_sqlmap.rb)

module name (or leave blank to use filename base)

author and description

default SQLMAP_PATH (path to your sqlmap.py)

paste full Burp request, ending with a single line END

optionally supply an MSF module dir to copy files into (or leave blank to keep files in current directory).

4. After generation you will have:

sacco_auto_sqlmap.rb in current dir (module as you requested)

exploit.txt in current dir (your raw Burp request)

optionally copied to MSF module dir (if you supplied one and had permissions)


# Setup for example
```yaml
reload_all
use auxiliary/MSF/sacco_auto_sqlmap    # or use auxiliary/<path>/<name> depending where you placed it
set RAW_REQUEST `cat /home/kali/.msf_exploits/exploit_YYYYMMDDHHMMSS.txt`   # or set RAW_REQUEST by pasting
set SQLMAP_PATH /home/kali/sqlmap-nu11secur1ty/sqlmap.py
set RHOSTS 192.168.100.46
run
```

In msfconsole:
