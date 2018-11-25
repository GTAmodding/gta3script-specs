Elements
=====================

The lexical grammar of the language is context-sensitive. As such, the lexical elements and the syntactic elements are presented together.

## Source Code

*Source code* is a stream of printable ASCII characters plus the control codes line feed (`\n`), horizontal tab (`\t`) and carriage return (`\r`).

```
ascii_char := ascii_printable | ascii_control ;
ascii_printable := /* printable ASCII characters */ ;
ascii_control := '\n' | '\t' | '\r' ;
```

Carriage returns should appear only before a line feed.

Lowercase letters in the stream shall be interpreted as its uppercase equivalent.

Space, horizontal tab, parentheses and comma are defined as whitespace characters.

```
whitespace := ' ' | '\t' | '(' | ')' | ',' ;
```

A *line* is a sequence of characters delimited by a newline. The start of the stream begins a line. The end of the stream finishes a line.

```
newline := ['\r'] `\n` ;
```

Each line should be interpreted as if there is no whitespaces in either ends of the line.

A *token character* is any character capable of forming a single token.

```
graph_char := ascii_printable - (whitespace | '"') ;
token_char := graph_char - ('+' | '-' | '*' | '/' | '=' | '<' | '>') ;
```

To simplify future definitions, the productions `eol` (end of line) and `sep` (token separator) are defined.

```
sep := whitespace {whitespace} ;
eol := newline | EOF ;
```

## Comments

*Comments* serve as program documentation.

```
comment := line_comment | block_comment ;
line_comment := '//' {ascii_char} eol ;
block_comment := '/*' {block_comment | ascii_char} '*/' ;
```

There are two forms:

 + *Line comments* starts with the character sequence `//` and stop at the end of the line.
 + *Block comments* starts with the character sequence `/*` and stop with its matching `*/`. Block comments can be nested inside each other.

The contents of a comment shall be interpreted as if it is whitespaces in the source code. More specifically: 

 + A line comment should be interpreted as an `eol`.
 + A single, nested, block comment should be interpreted as an `eol` on each line boundary it crosses. On its last line (i.e. the one it does not cross), it should be interpreted as one or more whitespace characters.

Comments cannot start inside string literals.

## Commands

A command describes an operation for a script to perform.

```
command_name := token_char {token_char} ;
command := command_name { sep argument } ;
```

There are several types of arguments.

```
argument := integer
          | floating 
          | identifier
          | string_literal ;
```

### Integer Literals

```
digit := '0'..'9' ;
integer := ['-'] digit {digit} ;
```

A *integer literal* is a sequence of digits optionally preceded by a minus sign.

If the literal begins with a minus, the number following it shall be negated.

### Floating-Point Literals

```
floating_form1 := '.' digit { digit | '.' | 'F' } ;
floating_form2 := digit { digit } ('.' | 'F') { digit | '.' | 'F' } ;
floating := ['-'] (floating_form1 | floating_form2) ;
```

A *floating-point literal* is a nonempty sequence of digits which must contain at least one occurrence of the characters `.` or `F`.

Once the `F` characters is found, all characters including and following it shall be ignored. The same shall happen when the character `.` is found a second time.

The literal can be preceded by a minus sign, which shall negate the floating-point number.

The following are examples of valid and invalid literals:

| Literal | Same As |
| ------  | ------- |
| 1       | invalid |
| -1      | invalid |
| 1f      | 1.0     |
| 1.      | 1.0     |
| .1      | 0.1     |
| .1f     | 0.1     |
| .11     | 0.11    |
| .1.9    | 0.1     |
| 1.1     | 1.1     |
| 1.f     | 1.0     |
| 1..     | 1.0     |

### Identifiers

```
identifier := ('$' | 'A'..'Z') {token_char} ;
```

An *identifier* is a sequence of token characters beggining with a dollar or alphabetic character.

**Constraints**

An identifier shall not end with a `:` character.

### String Literals

A *string literal* holds a string delimited by quotation marks.

```
string_literal := '"' { ascii_char - (newline | '"') } '"' ;
```

### Variable References

A *variable name* is a sequence of token characters, except the characters `[` and `]` cannot happen.

```
variable_char := token_char - ('[' | ']') ;
variable_name := ('$' | 'A'..'Z') {variable_char} ;
```

A *variable reference* is a variable name optionally followed by an array subscript.

```
subscript := '[' (variable_name | integer) ']' ;
variable := variable_name [ subscript ] ;
```

The type of a variable reference is the type of the variable name being referenced.

The subscript uses an integer literal or another variable name of integer type for zero-based indexing.

The program is ill-formed if the array subscript uses a negative or out of bounds value for indexing.

The program is ill-formed if a variable name is followed by a subscript but the variable is not an array.

An array variable name which is not followed by a subscript behaves as if its zero-indexed element is referenced.
