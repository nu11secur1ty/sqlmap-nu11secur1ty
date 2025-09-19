"""
Python generator for Metasploit auxiliary modules using sqlmap-nu11secur1ty.
Generates a .rb module and saves the Burp request to exploit.txt.
"""

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

    print_status("Saving RAW_REQUEST to exploit.txt...")

    module_dir = File.expand_path(File.dirname(__FILE__))
    request_file = File.join(module_dir, "exploit.txt")

    File.open(request_file, "w") {{ |f| f.write(raw_request) }}  # This line fixed below

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

def generate_module(output_path, module_name, author, description, raw_request):
    # Escape any Ruby-specific characters
    escaped_request = raw_request.replace('\\', '\\\\').replace('"', '\\"')

    # Fix the File.open line
    content = MODULE_TEMPLATE.format(
        module_name=module_name,
        author=author,
        description=description,
        raw_request=escaped_request
    )

    # Replace the double braces with correct Ruby block syntax
    content = content.replace('{{ |f| f.write(raw_request) }}', '{ |f| f.write(raw_request) }')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Module saved to {output_path}')
    print('exploit.txt will be saved when you run this module in MSF.')

if __name__ == '__main__':
    output_file = input('Enter output .rb filename (e.g., MyModule.rb): ')
    module_name = input('Enter module name (e.g., SQLi-Test): ')
    author = input('Enter author name: ')
    description = input('Enter module description: ')
    print('Paste your Burp request (end with a single line containing only END):')

    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    raw_request = '\n'.join(lines)

    generate_module(output_file, module_name, author, description, raw_request)
