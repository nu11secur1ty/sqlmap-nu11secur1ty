#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Generates a .rb module and saves exploit.txt automatically
Author: nu11secur1ty
"""

import os
from string import Template
import shutil

# Ruby template with $ placeholders instead of {}
MODULE_TEMPLATE = Template(r'''
class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::HttpClient

  def initialize
    super(
      'Name'           => '$module_name',
      'Description'    => '$description',
      'Author'         => '$author',
      'License'        => MSF_LICENSE
    )

    register_options(
      [
        OptString.new('RAW_REQUEST', [true, 'Raw HTTP request (from Burp)', '']),
        OptString.new('TARGETURI', [true, 'Target URI extracted from request', '$targeturi']),
        OptString.new('RHOSTS', [true, 'Target host extracted from request', '$rhost'])
      ]
    )
  end

  def run
    print_status("Running module $module_name")
    raw_request = datastore['RAW_REQUEST']

    if raw_request.empty?
      print_error("Set RAW_REQUEST first!")
      return
    end

    # Save the request to exploit.txt
    module_dir = File.expand_path(File.dirname(__FILE__))
    request_file = File.join(module_dir, "exploit.txt")
    File.open(request_file, "w") { |f| f.write(raw_request) }

    print_status("exploit.txt saved in module directory")
  end
end
''')

def generate_module(output_path, module_name, author, description, raw_request, msf_dir):
    # Extract RHOST and TARGETURI from request
    rhost = ""
    targeturi = ""
    for line in raw_request.splitlines():
        if line.startswith("Host:"):
            rhost = line.split(":",1)[1].strip()
        elif line.startswith("POST") or line.startswith("GET"):
            targeturi = line.split(" ",2)[1].strip()

    # Ensure MSF directory exists
    if not os.path.isdir(msf_dir):
        print(f"[!] MSF directory {msf_dir} does not exist")
        return

    # Write exploit.txt
    exploit_path = os.path.join(msf_dir, "exploit.txt")
    try:
        with open(exploit_path, 'w', encoding='utf-8') as f:
            f.write(raw_request)
        print(f"[+] exploit.txt saved to {exploit_path}")
    except Exception as e:
        print(f"[!] Failed to write exploit.txt: {e}")
        return

    # Fill template
    content = MODULE_TEMPLATE.substitute(
        module_name=module_name,
        author=author,
        description=description,
        rhost=rhost,
        targeturi=targeturi
    )

    # Write .rb module
    rb_path = os.path.join(msf_dir, output_path)
    try:
        with open(rb_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[+] Module saved to {rb_path}")
    except Exception as e:
        print(f"[!] Failed to write module: {e}")

if __name__ == "__main__":
    print("=== MSF .rb Module Generator (sqlmap-nu11secur1ty) ===")
    output_file = input("Enter output .rb filename (e.g., sacco.rb): ").strip()
    module_name = input("Enter module name: ").strip()
    author = input("Enter author name: ").strip()
    description = input("Enter module description: ").strip()
    msf_dir = input("Enter full path to MSF module directory (e.g., /usr/share/metasploit-framework/modules/auxiliary/MSF/): ").strip()

    print("Paste your Burp request (POST/GET). End with a line containing only END:")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    raw_request = "\n".join(lines)

    generate_module(output_file, module_name, author, description, raw_request, msf_dir)
