#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generate Metasploit auxiliary modules from Burp requests
             and execute sqlmap-nu11secur1ty automatically.
"""

import os
import shutil

# List of common Metasploit auxiliary folders
MSF_PATHS = [
    "/usr/share/metasploit-framework/modules/auxiliary/MSF/",
    "/usr/share/metasploit-framework/modules/auxiliary/scanner/",
    "/opt/metasploit-framework/embedded/framework/modules/auxiliary/MSF/"
]

MODULE_TEMPLATE = r'''
class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::HttpClient

  def initialize(info = {})
    super(
      update_info(
        info,
        'Name'           => '{module_name}',
        'Description'    => '{description}',
        'Author'         => ['{author}'],
        'License'        => MSF_LICENSE
      )
    )

    register_options(
      [
        Opt::RHOSTS(),
        Opt::RPORT(80),
        OptString.new('RAW_REQUEST', [true, 'Raw HTTP request (from Burp)', ''])
      ]
    )
  end

  def run
    target_host = datastore['RHOSTS']
    target_port = datastore['RPORT']
    raw_request = datastore['RAW_REQUEST']

    if raw_request.nil? || raw_request.empty?
      print_error("Set RAW_REQUEST first!")
      return
    end

    print_status("Target: \#{target_host}:\#{target_port}")
    print_status("Saving RAW_REQUEST to exploit.txt...")

    module_dir = File.expand_path(File.dirname(__FILE__))
    request_file = File.join(module_dir, "exploit.txt")

    begin
      File.open(request_file, "w") {{ |f| f.write(raw_request) }}
    rescue => e
      print_error("Failed to write exploit.txt: \#{e}")
      return
    end

    sqlmap_path = File.join(module_dir, '..', 'sqlmap.py')

    if File.exist?(sqlmap_path)
      sqlmap_cmd = "python3 \#{sqlmap_path} -r \#{request_file} --batch --level=1"
      print_status("Executing: \#{sqlmap_cmd}")
      system(sqlmap_cmd)
    else
      print_error("sqlmap.py not found in parent directory")
    end
  end
end
'''

def detect_msf_folder():
    for path in MSF_PATHS:
        if os.path.isdir(path):
            return path
    return None

def clean_msf_folder(msf_path):
    # Remove existing .rb and .txt files in the target folder
    for filename in os.listdir(msf_path):
        if filename.endswith(".rb") or filename.endswith(".txt"):
            file_path = os.path.join(msf_path, filename)
            try:
                os.remove(file_path)
                print(f"[+] Removed old file: {filename}")
            except Exception as e:
                print(f"[!] Failed to remove {filename}: {e}")

def generate_module(module_name, author, description, raw_request, msf_path):
    os.makedirs(msf_path, exist_ok=True)

    # Clean the directory first
    clean_msf_folder(msf_path)

    rb_file = f"{module_name}.rb"
    txt_file = "exploit.txt"

    # Write temporary files first
    with open(rb_file, 'w', encoding='utf-8') as f:
        f.write(MODULE_TEMPLATE.format(
            module_name=module_name,
            author=author,
            description=description
        ))

    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(raw_request)

    # Move files to MSF folder
    shutil.move(rb_file, os.path.join(msf_path, rb_file))
    shutil.move(txt_file, os.path.join(msf_path, txt_file))

    print(f"[+] Your exploit '{module_name}' has been created and moved to MSF folder: {msf_path}")
    print(f"[+] Module: {rb_file}")
    print(f"[+] Burp request saved as: {txt_file}")
    print("[!] Ready to use in msfconsole!")

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

    msf_path = detect_msf_folder()
    if msf_path:
        print(f"[+] Detected MSF folder: {msf_path}")
        generate_module(module_name, author, description, raw_request, msf_path)
    else:
        print("[!] Could not detect MSF folder automatically.")
        msf_path = input("Enter full path to MSF module directory manually: ").strip()
        generate_module(module_name, author, description, raw_request, msf_path)
