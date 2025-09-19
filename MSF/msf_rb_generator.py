#!/usr/bin/env python3
import os
import shutil

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

    print_status("Target: #{target_host}:#{target_port}")
    print_status("Saving RAW_REQUEST to exploit.txt...")

    module_dir = File.expand_path(File.dirname(__FILE__))
    request_file = File.join(module_dir, "exploit.txt")

    begin
      File.open(request_file, "w") {{ |f| f.write(raw_request) }}
    rescue => e
      print_error("Failed to write exploit.txt: #{e}")
      return
    end

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
'''

def generate_module(module_name, author, description, raw_request, msf_path=None):
    # Detect MSF module path or ask user
    if not msf_path:
        msf_path = input("Enter full path to MSF module directory (e.g., /home/kali/.../auxly/MSF/): ").strip()
    os.makedirs(msf_path, exist_ok=True)

    output_rb = os.path.join(msf_path, f"{module_name}.rb")
    exploit_txt = os.path.join(msf_path, "exploit.txt")

    # Generate module content
    content = MODULE_TEMPLATE.format(
        module_name=module_name,
        author=author,
        description=description
    )

    # Write .rb module
    with open(output_rb, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[+] Module saved to {output_rb}")

    # Write exploit.txt
    with open(exploit_txt, 'w', encoding='utf-8') as f:
        f.write(raw_request)
    print(f"[+] Burp request saved to {exploit_txt}")

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

    generate_module(module_name, author, description, raw_request)
