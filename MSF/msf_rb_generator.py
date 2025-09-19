#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generate Metasploit auxiliary modules from Burp requests
             and execute sqlmap-nu11secur1ty automatically.
"""

import os
import shutil

MODULE_TEMPLATE = r'''
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
    # Correct Ruby block syntax
    File.open(request_file, "w") do |f|
      f.write(raw_request)
    end

    sqlmap_path = File.join(module_dir, "..", "sqlmap.py")

    if File.exist?(sqlmap_path)
      sqlmap_cmd = "python3 \\#{sqlmap_path} -r \\#{request_file} --batch --level=1"
      print_status("Executing: \\#{sqlmap_cmd}")
      system(sqlmap_cmd)
    else
      print_error("sqlmap.py not found in parent directory")
    end
  end
end
'''

def generate_module(output_path, module_name, author, description, raw_request, msf_dir=None):
    # Escape only Python format placeholders
    content = MODULE_TEMPLATE.format(
        module_name=module_name,
        author=author,
        description=description
    )

    # Write .rb module
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Module saved to {output_path}")
    except Exception as e:
        print(f"[!] Failed to write module: {e}")
        return

    # Write exploit.txt
    exploit_txt = os.path.join(os.path.dirname(output_path), "exploit.txt")
    try:
        with open(exploit_txt, "w", encoding="utf-8") as f:
            f.write(raw_request)
        print(f"[+] exploit.txt saved to {exploit_txt}")
    except Exception as e:
        print(f"[!] Failed to save exploit.txt: {e}")

    # Optionally copy to MSF
    if msf_dir and os.path.isdir(msf_dir):
        try:
            shutil.copy(output_path, msf_dir)
            shutil.copy(exploit_txt, msf_dir)
            print(f"[+] Module and exploit.txt copied to {msf_dir}")
        except PermissionError:
            print(f"[!] Permission denied. Use sudo to copy to {msf_dir}")
        except Exception as e:
            print(f"[!] Failed to copy files to MSF directory: {e}")

if __name__ == "__main__":
    print("=== MSF .rb Module Generator (sqlmap-nu11secur1ty) ===")
    output_file = input("Enter output .rb filename (e.g., MyModule.rb): ").strip()
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

    msf_dir = input("Enter full path to MSF module directory (optional, leave empty to skip): ").strip()
    if msf_dir == "":
        msf_dir = None

    generate_module(output_file, module_name, author, description, raw_request, msf_dir)
