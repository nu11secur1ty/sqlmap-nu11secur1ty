#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generate Metasploit auxiliary modules from Burp requests
             and move them automatically to MSF folder.
"""

import os
import shutil

MODULE_TEMPLATE = r"""
class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::HttpClient

  def initialize
    super(
      'Name'           => '{module_name}',
      'Description'    => '{description}',
      'Author'         => ['{author}'],
      'License'        => MSF_LICENSE
    )

    register_options(
      [
        OptString.new('RAW_REQUEST', [true, 'Raw HTTP request (from Burp)', ''])
      ]
    )
  end

  def run
    raw_request = datastore['RAW_REQUEST']

    if raw_request.empty?
      print_error("Set RAW_REQUEST first!")
      return
    end

    print_status("Saving RAW_REQUEST to exploit.txt...")

    module_dir = File.expand_path(File.dirname(__FILE__))
    request_file = File.join(module_dir, "exploit.txt")
    File.open(request_file, "w") { |f| f.write(raw_request) }

    sqlmap_path = File.join(module_dir, '..', 'sqlmap.py')

    if File.exist?(sqlmap_path)
      sqlmap_cmd = "python3 #{sqlmap_path} -r #{request_file} --batch --level=1"
      print_status("Executing: #{sqlmap_cmd}")
      system(sqlmap_cmd)
    else
      print_error("sqlmap.py not found in parent directory")
    end
  end
end
"""

def generate_module(module_name, author, description, raw_request, msf_path):
    # Clean up old files in MSF path
    rb_file = os.path.join(msf_path, f"{module_name}.rb")
    txt_file = os.path.join(msf_path, "exploit.txt")
    for f in [rb_file, txt_file]:
        if os.path.exists(f):
            os.remove(f)

    # Write .rb module
    temp_rb = f"{module_name}.rb"
    try:
        with open(temp_rb, 'w', encoding='utf-8') as f:
            f.write(MODULE_TEMPLATE.format(
                module_name=module_name,
                author=author,
                description=description
            ))
        print(f"[+] Module {temp_rb} generated.")
    except Exception as e:
        print(f"[!] Failed to generate module: {e}")
        return

    # Write exploit.txt
    try:
        with open("exploit.txt", 'w', encoding='utf-8') as f:
            f.write(raw_request)
        print("[+] exploit.txt saved.")
    except Exception as e:
        print(f"[!] Failed to save exploit.txt: {e}")
        return

    # Move files to MSF directory
    try:
        shutil.move(temp_rb, rb_file)
        shutil.move("exploit.txt", txt_file)
        print(f"[+] Module and exploit.txt moved to {msf_path}")
        print("[*] Your MSF module is ready: use 'use auxiliary/MSF/{0}' in msfconsole".format(module_name))
    except PermissionError:
        print(f"[!] Permission denied. Try running with sudo to move files to {msf_path}")
    except Exception as e:
        print(f"[!] Failed to move files: {e}")

if __name__ == '__main__':
    print("=== MSF .rb Module Generator (sqlmap-nu11secur1ty) ===")
    module_name = input("Enter module name (e.g., sacco): ").strip()
    author = input("Enter author name: ").strip()
    description = input("Enter module description: ").strip()
    
    print("Paste your Burp request (POST/GET). End with a line containing only END:")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    raw_request = "\n".join(lines)

    msf_path = input("Enter full path to MSF module directory (e.g., /usr/share/metasploit-framework/modules/auxiliary/MSF/): ").strip()

    generate_module(module_name, author, description, raw_request, msf_path)
