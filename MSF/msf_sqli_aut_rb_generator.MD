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


# Setup for example in `msfconsole`
```yaml
reload_all
use auxiliary/MSF/sacco_auto_sqlmap    # or use auxiliary/<path>/<name> depending where you placed it
set SQLMAP_PATH /home/kali/sqlmap-nu11secur1ty/sqlmap.py
set RHOSTS 0.0.0.0 # your RHOSTS
run
```

# Exploit example in my VM Kali Linux
```yaml
msf > use auxiliary/MSF/sacco_auto_sqlmap
msf auxiliary(MSF/sacco_auto_sqlmap) > set SQLMAP_PATH /home/kali/sqlmap-nu11secur1ty/sqlmap.py
SQLMAP_PATH => /home/kali/sqlmap-nu11secur1ty/sqlmap.py
msf auxiliary(MSF/sacco_auto_sqlmap) > set RHOSTS 10.10.0.7
RHOSTS => 10.10.0.7
msf auxiliary(MSF/sacco_auto_sqlmap) > run
```
