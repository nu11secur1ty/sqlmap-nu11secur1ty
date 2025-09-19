#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generate Metasploit auxiliary modules from Burp requests
             and place them in the MSF modules directory automatically.
"""

import os
import shutil
import getpass

MODULE_TEMPLATE = r"""
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

    print_status("Running safe lab MSF module: {module_name}")
    print_status("RAW_REQUEST set. Use it in your lab responsibly.")
  end
end
"""

def generate_module(module_name, author, description, raw_request, msf_dir):
    # Ensure the module filename ends with .rb
    filename = module_name
    if not filename.lower().endswith(".rb"):
        filename += ".rb"
    output_path = os.path.join(msf_dir, filename)

    # Escape Ruby curly braces for safe formatting
    safe_request = raw_request.replace("{", "{{").replace("}", "}}")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(MODULE_TEMPLATE.format(
                module_name=module_name,
                author=author,
                description=description
            ))
        print(f"[+] Module saved to {output_path}")
    except PermissionError:
        print("[!] Permission denied. Try running with sudo.")
    except Exception as e:
        print(f"[!] Failed to write module: {e}")

if __name__ == "__main__":
    print("=== MSF .rb Module Generator (sqlmap-nu11secur1ty) ===")
    module_name = input("Enter module name (e.g., SQLi-Test): ").strip()
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

    # Detect Metasploit auxiliary/MSF directory automatically if exists
    possible_msf = "/usr/share/metasploit-framework/modules/auxiliary/MSF/"
    if os.path.isdir(possible_msf):
        msf_dir = possible_msf
        print(f"[+] Detected MSF directory: {msf_dir}")
    else:
        msf_dir = input("Enter full path to MSF module directory (auxiliary/MSF/): ").strip()
        if not os.path.isdir(msf_dir):
            print("[!] Directory does not exist. Exiting.")
            exit(1)

    generate_module(module_name, author, description, raw_request, msf_dir)
