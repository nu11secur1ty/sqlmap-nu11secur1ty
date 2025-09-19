import os
import zipfile

# --- Config ---
package_name = "MSF_generator_package.zip"
base_dir = "sqlmap-nu11secur1ty_package"
msf_dir = os.path.join(base_dir, "MSF")
sqlmap_file = os.path.join(base_dir, "sqlmap.py")

# Create folder structure
os.makedirs(msf_dir, exist_ok=True)

# --- Create placeholder sqlmap.py ---
sqlmap_content = """# Placeholder for sqlmap-nu11secur1ty
print("sqlmap-nu11secur1ty ready!")
"""
with open(sqlmap_file, "w", encoding="utf-8") as f:
    f.write(sqlmap_content)

# --- Create README_FULL.md ---
readme_content = """# MSF Module Generator (`sqlmap-nu11secur1ty`) — Full Usage Guide

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

[...]

(Paste the full README content here)
"""

with open(os.path.join(msf_dir, "README_FULL.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

# --- Create placeholder generator ---
generator_content = """# msf_rb_generator.py placeholder
print("This is the MSF generator placeholder. Replace with your actual generator code.")
"""
with open(os.path.join(msf_dir, "msf_rb_generator.py"), "w", encoding="utf-8") as f:
    f.write(generator_content)

# --- Create ZIP ---
with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, base_dir)
            zipf.write(filepath, arcname)

print(f"Package created: {package_name}")
