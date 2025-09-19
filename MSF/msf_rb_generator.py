#!/usr/bin/env python3
"""
MSF .rb Module Generator for sqlmap-nu11secur1ty
Author: nu11secur1ty
Description: Generate Metasploit auxiliary modules from Burp requests
             and execute sqlmap-nu11secur1ty automatically.
"""

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
    File.open(request_file, "w") {{ |f| f.write(raw_request) }}

    sqlmap_path = File.join(module_dir, '..', 'sqlmap.py')

    if File.exist?(sqlmap_path)
      sqlmap_cmd = "python3 \#{{sqlmap_path}} -r \#{{request_file}} --batch --level=1"
      print_status("Executing: \#{{sqlmap_cmd}}")
      system(sqlmap_cmd)
    else
      print_error("sqlmap.py not found in parent directory")
    end
  end
end
'''

def generate_module(output_path, module_name, author, description, raw_request):
    try:
        # Write .rb module
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(MODULE_TEMPLATE.format(
                module_name=module_name,
                author=author,
                description=description
            ))
        print(f"[+] Module saved to {output_path}")

        # Write exploit.txt with raw request
        exploit_txt_path = output_path.replace('.rb', '_exploit.txt')
        with open(exploit_txt_path, 'w', encoding='utf-8') as f:
            f.write(raw_request)
        print(f"[+] Saved Burp request to {exploit_txt_path}")

    except Exception as e:
        print(f"[!] Failed to write files: {e}")

if __name__ == '__main__':
    print("=== MSF .rb Module Generator (sqlmap-nu11secur1ty) ===")
    output_file = input("Enter output .rb filename (e.g., MyModule.rb): ").strip()
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

    generate_module(output_file, module_name, author, description, raw_request)
