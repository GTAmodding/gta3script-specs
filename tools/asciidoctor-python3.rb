require 'asciidoctor'
require 'asciidoctor/extensions'
require 'open3'

include Asciidoctor

def python3_preprocessor(name)
  klass = Class.new(Asciidoctor::Extensions::Preprocessor) do
    class << self
      attr_accessor :script
    end
    def process document, reader
      script = self.class.script
      out, err, s = Open3.capture3("python3 #{script}",  :stdin_data => reader.read)
      if not s.success? 
        $stderr.puts(err)
        exit 1
      end
      return Reader.new out.split("\n")
    end
  end
  klass.script = File.join(File.dirname(__FILE__), name)
  return klass
end
