import os

MODULE_TEMPLATE = '''##
# {module_name}.rb
#
# Author: {author}
# Description: {description}
##

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
      sqlmap_cmd = "python3 {{sqlmap_path}} -r {{request_file}} --batch --level=1"
      print_status("Executing: {{sqlmap_cmd}}")
      system(sqlmap_cmd)
    else
      print_error("sqlmap.py not found in parent directory")
    end
  end
end
'''

def generate_module(output_file, module_name, author, description, raw_request):
    # Escape curly braces for Ruby code blocks
    safe_template = MODULE_TEMPLATE.replace("{", "{{").replace("}", "}}")
    # Then restore the Python placeholders
    safe_template = safe_template.replace("{{module_name}}", "{module_name}") \
                                 .replace("{{author}}", "{author}") \
                                 .replace("{{description}}", "{description}")

    content = safe_template.format(
        module_name=module_name,
        author=author,
        description=description
    )

    # Save .rb module
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # Save exploit.txt in same directory
    request_path = os.path.join(os.path.dirname(output_file), "exploit.txt")
    with open(request_path, 'w', encoding='utf-8') as f:
        f.write(raw_request)

    print(f"Module saved to {output_file}")
    print(f"Exploit request saved to {request_path}")

if __name__ == '__main__':
    print("=== MSF sqlmap-nu11secur1ty Module Generator ===")
    output_file = input("Enter output .rb filename (e.g., sqlmap_sqli_test.rb): ")
    module_name = input("Enter module name (e.g., SQLi Test Module): ")
    author = input("Enter author name: ")
    description = input("Enter module description: ")

    print("\nPaste your full Burp request (end with a single line containing only END):")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    raw_request = "\n".join(lines)

    generate_module(output_file, module_name, author, description, raw_request)
