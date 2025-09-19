#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generate Metasploit auxiliary modules from Burp requests
             and run sqlmap-nu11secur1ty directly from RAW_REQUEST.
"""

import os
import shutil
import getpass

MODULE_TEMPLATE = r'''
class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::HttpClient

  def initialize
    super(
      'Name'        => '{module_name}',
      'Description' => '{description}',
      'Author'      => '{author}',
      'License'     => MSF_LICENSE
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

    module_dir = File.expand_path(File.dirname(__FILE__))
    sqlmap_path = File.join(module_dir, '..', 'sqlmap.py')

    if File.exist?(sqlmap_path)
      # Save RAW_REQUEST temporarily
      tmp_file = File.join(module_dir, "tmp_request.txt")
      File.open(tmp_file, "w") { |f| f.write(raw_request) }

      sqlmap_cmd = "python3 {sqlmap_path} -r #{tmp_file} --batch --level=1"
      print_status("Executing: #{sqlmap_cmd}")
      system(sqlmap_cmd)

      File.delete(tmp_file) if File.exist?(tmp_file)
    else
      print_error("sqlmap-nu11secur1ty not found in parent directory")
    end
  end
end
'''

def generate_module(module_name, author, description, raw_request):
    # Determine MSF auxiliary/MSF directory
    home_msf = os.path.expanduser("~/.msf4/modules/auxiliary/MSF")
    system_msf = "/usr/share/metasploit-framework/modules/auxiliary/MSF"

    if os.path.isdir(home_msf):
        msf_dir = home_msf
    elif os.path.isdir(system_msf):
        msf_dir = system_msf
    else:
        print("[!] MSF directory not found!")
        return

    # Output filename
    output_file = f"{module_name}.rb"
    output_path = os.path.join(msf_dir, output_file)

    # Escape braces in Ruby code
    safe_template = MODULE_TEMPLATE.replace("{", "{{").replace("}", "}}")
    safe_template = safe_template.replace("{{module_name}}", module_name)\
                                 .replace("{{author}}", author)\
                                 .replace("{{description}}", description)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(safe_template)
        print(f"[+] Module saved to {output_path}")
        print("[+] You can now load it in Metasploit:")
        print(f"    msfconsole\n    use auxiliary/MSF/{output_file}")
    except PermissionError:
        print(f"[!] Permission denied. Try with sudo:\n    sudo python3 {__file__}")
    except Exception as e:
        print(f"[!] Failed to write files: {e}")

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

    generate_module(module_name, author, description, raw_request)
