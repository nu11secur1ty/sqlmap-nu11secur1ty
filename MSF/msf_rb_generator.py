#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generate Metasploit auxiliary modules from Burp requests,
             save exploit.txt, and auto-copy both to MSF modules folder.
"""

import os
import shutil
import getpass

MODULE_TEMPLATE = r'''
##
# {module_name}.rb
#
# Author: {author}
# Description: {description}
##

class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::HttpClient

  def initialize
    super(
      'Name'           => '{module_name}',
      'Description'    => '{description}',
      'Author'         => '{author}',
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

    print_status("RAW_REQUEST loaded, ready for lab testing...")
  end
end
'''

def generate_module(module_name, author, description, raw_request, msf_path):
    try:
        # Ensure MSF path exists
        if not os.path.isdir(msf_path):
            print(f"[!] MSF path does not exist: {msf_path}")
            return

        # Clean old files in MSF folder
        rb_file_path = os.path.join(msf_path, f"{module_name}.rb")
        txt_file_path = os.path.join(msf_path, "exploit.txt")
        for f in [rb_file_path, txt_file_path]:
            if os.path.exists(f):
                os.remove(f)

        # Save exploit.txt in MSF folder
        with open(txt_file_path, 'w', encoding='utf-8') as f:
            f.write(raw_request)

        # Save .rb module in MSF folder
        with open(rb_file_path, 'w', encoding='utf-8') as f:
            f.write(MODULE_TEMPLATE.format(
                module_name=module_name,
                author=author,
                description=description
            ))

        print(f"[+] Module and exploit.txt copied to {msf_path}")
        print("[!] Your module is ready! Load it in msfconsole with:")
        print(f"msfconsole -q -x 'use auxiliary/MSF/{module_name}; run;'")

    except PermissionError:
        print("[!] Permission denied. Try running the generator with sudo.")
    except Exception as e:
        print(f"[!] Failed to write files: {e}")

if __name__ == '__main__':
    print("=== MSF .rb Module Generator (sqlmap-nu11secur1ty) ===")
    module_name = input("Enter module name (e.g., SQLi-Test): ").strip()
    author = input("Enter author name: ").strip()
    description = input("Enter module description: ").strip()
    
    print("Paste your Burp request (POST/GET). End with a line containing only END:")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    raw_request = '\n'.join(lines)

    # Auto-detect MSF auxiliary/MSF folder
    default_msf_path = "/usr/share/metasploit-framework/modules/auxiliary/MSF/"
    msf_path_input = input(f"Enter full path to MSF module directory [{default_msf_path}]: ").strip()
    msf_path = msf_path_input if msf_path_input else default_msf_path

    generate_module(module_name, author, description, raw_request, msf_path)
