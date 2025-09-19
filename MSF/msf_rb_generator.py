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

    # Save exploit.txt in a safe writable location
    exploit_dir = File.join(Dir.home, ".msf_exploits")
    Dir.mkdir(exploit_dir) unless Dir.exist?(exploit_dir)
    request_file = File.join(exploit_dir, "exploit.txt")

    File.open(request_file, "w") { |f| f.write(raw_request) }
    print_status("exploit.txt saved to #{request_file}")

    # Path to sqlmap
    sqlmap_path = File.join(File.expand_path("..", File.dirname(__FILE__)), "sqlmap.py")

    if File.exist?(sqlmap_path)
      sqlmap_cmd = "python3 #{sqlmap_path} -r #{request_file} --batch --level=1"
      print_status("Executing: #{sqlmap_cmd}")
      system(sqlmap_cmd)
    else
      print_error("sqlmap.py not found in parent directory")
    end
  end
end
'''

def generate_module(output_file, module_name, author, description, raw_request):
    # Fix filename duplicates
    if not output_file.endswith(".rb"):
        output_file += ".rb"

    content = MODULE_TEMPLATE.format(
        module_name=module_name,
        author=author,
        description=description
    )

    # Write .rb in local folder first
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[+] Module saved locally as {output_file}")

    # Save exploit.txt in user's home folder
    exploit_dir = os.path.join(os.path.expanduser("~"), ".msf_exploits")
    os.makedirs(exploit_dir, exist_ok=True)
    exploit_path = os.path.join(exploit_dir, "exploit.txt")
    with open(exploit_path, 'w', encoding='utf-8') as f:
        f.write(raw_request)

    print(f"[+] exploit.txt saved to {exploit_path}")

    # Detect MSF auxiliary module path
    msf_path_default = "/usr/share/metasploit-framework/modules/auxiliary/MSF/"
    if os.path.exists(msf_path_default):
        msf_file_path = os.path.join(msf_path_default, os.path.basename(output_file))
        try:
            shutil.copy2(output_file, msf_file_path)
            print(f"[+] Module copied to MSF directory: {msf_file_path}")
        except PermissionError:
            print(f"[!] Cannot copy to MSF directory, sudo may be required: {msf_file_path}")
    else:
        print("[!] MSF directory not found, .rb module only saved locally.")

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

    generate_module(output_file, module_name, author, description, raw_request)
