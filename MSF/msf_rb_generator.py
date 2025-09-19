#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generates Metasploit auxiliary modules from Burp requests
             and creates exploit.txt automatically.
             Detects MSF auxiliary path and moves files using sudo if needed.
"""

import os
import shutil
import subprocess
import getpass

MODULE_TEMPLATE = r'''##
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

    print_status("Saving RAW_REQUEST to exploit.txt...")
    module_dir = File.expand_path(File.dirname(__FILE__))
    request_file = File.join(module_dir, "exploit.txt")
    File.open(request_file, "w") { |f| f.write(raw_request) }

    print_good("Saved exploit.txt in module directory")
  end
end
'''

def generate_module(module_name, author, description, raw_request, msf_path=None):
    module_name = module_name.rstrip(".rb")
    rb_filename = f"{module_name}.rb"
    txt_filename = "exploit.txt"

    # Write the Ruby module
    try:
        with open(rb_filename, "w", encoding="utf-8") as f:
            f.write(MODULE_TEMPLATE.format(
                module_name=module_name,
                author=author,
                description=description
            ))
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(raw_request)
    except Exception as e:
        print(f"[!] Failed to write files: {e}")
        return

    print(f"[+] Created {rb_filename} and {txt_filename} in current directory")

    # Detect MSF path if not provided
    if not msf_path:
        default_paths = [
            "/usr/share/metasploit-framework/modules/auxiliary/MSF",
            "/opt/metasploit-framework/embedded/framework/modules/auxiliary/MSF"
        ]
        for path in default_paths:
            if os.path.isdir(path):
                msf_path = path
                break

    if not msf_path or not os.path.isdir(msf_path):
        print("[!] MSF path not found. Files remain in current directory.")
        return

    # Move files using sudo if needed
    try:
        user = getpass.getuser()
        if os.access(msf_path, os.W_OK):
            # Direct move
            shutil.move(rb_filename, os.path.join(msf_path, rb_filename))
            shutil.move(txt_filename, os.path.join(msf_path, txt_filename))
        else:
            # Requires sudo
            print("[*] Moving files with sudo...")
            subprocess.run(["sudo", "mv", rb_filename, msf_path], check=True)
            subprocess.run(["sudo", "mv", txt_filename, msf_path], check=True)
        print(f"[+] Moved {rb_filename} and {txt_filename} to {msf_path}")
    except Exception as e:
        print(f"[!] Failed to move files: {e}")

if __name__ == "__main__":
    print("=== MSF .rb Module Generator (sqlmap-nu11secur1ty) ===")
    module_name = input("Enter module name (without .rb): ").strip()
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

    generate_module(module_name, author, description, raw_request)
