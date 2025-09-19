#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generate Metasploit auxiliary modules from Burp requests
             with automatic extraction of RHOSTS, TARGETURI, and PORT.
"""

import os
import shutil
from urllib.parse import urlparse

MODULE_TEMPLATE = r"""
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
        OptString.new('RAW_REQUEST', [true, 'Raw HTTP request (from Burp)', '']),
        Opt::RHOSTS.new('RHOSTS', [true, 'Target host', '{rhosts}']),
        OptString.new('TARGETURI', [true, 'Target URI', '{targeturi}']),
        Opt::RPORT.new('RPORT', [true, 'Target port', {rport}])
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
    request_file = File.join(module_dir, "exploit.txt")
    File.open(request_file, "w") {{ |f| f.write(raw_request) }}
    print_status("RAW_REQUEST saved to exploit.txt")

    sqlmap_path = File.join(module_dir, '..', 'sqlmap-nu11secur1ty', 'sqlmap.py')

    if File.exist?(sqlmap_path)
      sqlmap_cmd = "python3 \#{sqlmap_path} -r \#{request_file} --batch --level=1"
      print_status("Executing sqlmap-nu11secur1ty: \#{sqlmap_cmd}")
      system(sqlmap_cmd)
    else
      print_error("sqlmap-nu11secur1ty not found in module directory")
    end
  end
end
"""

def parse_request(raw_request):
    """Extract host, port, and URI from the Burp request."""
    host, port, uri = "127.0.0.1", 80, "/"
    for line in raw_request.splitlines():
        if line.lower().startswith("host:"):
            host_port = line.split(":", 1)[1].strip()
            if ":" in host_port:
                host, port = host_port.split(":")
                port = int(port)
            else:
                host = host_port
                port = 443 if "https" in raw_request.lower() else 80
        elif line.upper().startswith(("GET", "POST", "HEAD", "PUT", "DELETE")):
            parts = line.split()
            if len(parts) >= 2:
                uri = parts[1]
    return host, port, uri

def generate_module(output_path, module_name, author, description, raw_request, msf_dir=None):
    rhost, rport, targeturi = parse_request(raw_request)

    content = MODULE_TEMPLATE.format(
        module_name=module_name,
        description=description,
        author=author,
        rhosts=rhost,
        rport=rport,
        targeturi=targeturi
    )

    try:
        # Save .rb module
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Module saved to {output_path}")

        # Save exploit.txt
        exploit_path = os.path.join(os.path.dirname(output_path), "exploit.txt")
        with open(exploit_path, "w", encoding="utf-8") as f:
            f.write(raw_request)
        print(f"[+] Exploit saved to {exploit_path}")

        # Auto copy to MSF dir if exists
        if msf_dir and os.path.isdir(msf_dir):
            shutil.copy(output_path, msf_dir)
            shutil.copy(exploit_path, msf_dir)
            print(f"[+] Files copied to MSF directory: {msf_dir}")

    except Exception as e:
        print(f"[!] Failed to write files: {e}")

if __name__ == "__main__":
    print("=== MSF .rb Module Generator (sqlmap-nu11secur1ty) ===")
    output_file = input("Enter output .rb filename (e.g., MyModule.rb): ").strip()
    module_name = input("Enter module name (e.g., SQLi-Test): ").strip()
    author = input("Enter author name: ").strip()
    description = input("Enter module description: ").strip()
    msf_dir = input("Enter full path to MSF module directory (or leave blank to skip): ").strip() or None

    print("Paste your Burp request (POST/GET). End with a line containing only END:")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    raw_request = "\n".join(lines)

    generate_module(output_file, module_name, author, description, raw_request, msf_dir)
