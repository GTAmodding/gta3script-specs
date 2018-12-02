require_relative './asciidoctor-python3'

Asciidoctor::Extensions.register do
  preprocessor python3_preprocessor("asciidoctor-grammar-preprocessor.py")
end
