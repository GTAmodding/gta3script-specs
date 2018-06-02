**Note:** This is a draft. It may be wrong and subject to change.

## Introduction

This is an attempt to produce a somewhat formal language specification for the GTA3script programming language.

Previous work has been done by [Wesser]. However it's not (nor meant to be) structured formally. That said, this document wouldn't be possible without his huge research effort on describing the language.

GTA3script is a rather simple scripting language built by Rockstar North to design the mission scripts of its Grand Theft Auto games. It's so simple that it has a huge amount of quirks uncommon to other languages. This document will attempt to pull together all those tricks in a coherent way.

## Notation

TODO

## Source Code Representation

The source code is described as an stream of ASCII characters.

TODO is \x00 part of it?

```
ascii_char := '\x00' .. '\x7F' ;
```

TODO atom char

```
atom_char := ascii_char - (whitespace | newline | '"')
```

## Elements

The lexical grammar of the language is context-sensitive. As such, the lexical elements and the syntactic elements will be presented together.

### Whitespaces

The following ASCII characters should be treated as whitespaces:

```
whitespace := ' ' | '\t' | '(' | ')' | ',' | '\r' ;
```

A new line is specified as a LF character or the end of file.

```
newline := `\n` | EOF ;
```

Whitespaces and newlines play a critical role in GTA3script unlike other languages such as C in which spaces are simply ignored.

TODO eol

```
sol := {whitespace}
eol := {whitespace} newline
whitespaces := whitespace {whitespace}
```

### Comments

Comments serve as program documentation. There are two forms:

 + *Line comments* starts with the character sequence `//` and stop at the end of the line.
 + *Multi-line comments* starts with the character sequence `/*` and stop with its matching `*/` character sequence. Those comments can be nested inside each other.

The contents of comments must be interpreted as if it were whitespaces in the source code. Comments cannot start inside [string literals].

### Command

An script is structured as a serie commands describing what the script should do.

The name of a command consists of any character in the ASCII character set except for whitespaces, newline and quotation marks. Command names are always case insensitive and from here on we'll describe them in upper-case.

```
command_name := atom_char { atom_char }
```


A command is a command name followed by zero or more arguments. The end of a command is given by a newline.

```
command := command_name { argument } eol
```

### Arguments

There are several types of arguments. Argument are always delimited by whitespaces.

```
argument := whitespaces ( integer_literal | floating_literal | text_label_literal | label_literal | string_constant | string_literal | filename_literal | variable )
```

#### Integer Literals

An integer literal is a sequence of digits and minus signs.

```
integer_digit := '0'..'9'
integer_literal := { '-' } integer_digit { (integer_digit | '-') }
```

If the literal begins with a minus `-`, the integer number following it should be negated. If the `-` character happens anywhere but in the first character, all characters following and including the minus should be ignored.

To make it clear, the following integer literals are valid and act as if they were the literal on the right.

```
1 => 1
010 => 10
-39 => -39
-432-10 => -432
```

#### Floating-Point Literals

A floating-point literal is a nonempty sequence of digits which must contain at least one occurence of the characters `.`, `f` or `F`. Once the `f` or `F` characters are found, all characters including and following it should be ignored. The same should happen when the character `.` is found a second time. The literal may be preceeded by a minus sign, which should negate the floating-point number.

```
floating_form1 := '.' integer_digit { integer_digit | '.' | 'f' | 'F' }
floating_form2 := integer_digit { integer_digit } ('.' | 'f' | 'F') { integer_digit | '.' | 'f' | 'F' }
floating_literal := { '-' } (floating_form1 | floating_form2)
```

The following are examples of valid and invalid literals:

```
1 => invalid
-1 => invalid
1f => 1.0
1. => 1.0
.1 => 0.1
.1f => 0.1
.11 => 0.11
.1.9 => 0.1
1.1 => 1.1
1.f => 1.0
1.. => 1.0
```

#### Text Literals

There are a few types of text literals. An text literal begins with an alphabetic value and may be followed by any character except whitespaces, newline and quotation marks. A text literal shall not end with a `:` character. Text literals are case insensitive.

A **string constant** is a text literal which expands to an integer value.

A **text label literal** is a text literal which expands to an internal game value which is yet unknown during the compilation phrase.

A **label literal** is a reference to a script label.

```
text_literal := ('A'..'Z' | 'a'..'z') { {atom_char} (atom_char - ':') }
string_constant := text_literal
text_label_literal := text_literal
label_literal := text_literal
```

#### String Literal

A string literals holds a sequence of ASCII characters delimited by quotation marks.

```
string_literal := '"' { ascii_char - '"' } '"'
```

#### Filename Literal

A filename literal represents a script filename. It is a sequence of zero or more characters followed by an extension `.sc`.

```
filename_literal := {atom_char} '.' ('s' | 'S') ('c' | 'C')
```

#### Variable Reference

The name of a variable is a sequence of characters similar to the one in `text_literal` except the characters `[` and `]` cannot happen. Variable names are also case insensitive.

```
variable_char := atom_char - ('[' | ']')
variable_name := ('A'..'Z' | 'a'..'z') { {variable_char} (variable_char - ':') }
```

A reference to a variable is a variable name optionally followed by an array subscript. The subscript may either use a variable name or an integer for indexing. Any character following the subscript should be ignored. Do note a subscript cannot happen twice.

```
subscript := '[' (variable_name | integer_literal) ']' 
variable := variable_name { subscript {variable_char} }
```

### Variable Declaration

A variable declaration happens by placing a declaration command followed by the variable names to be declared.

The declaration command names are a pair of the variable scoping rules and the variable static type.

```
command_var_decl_name := 'VAR_INT' | 'LVAR_INT' | 'VAR_FLOAT' | 'LVAR_FLOAT'
command_var_decl_arg := whitespaces variable
command_var_decl := command_var_decl_name command_var_decl_arg {command_var_decl_arg} eol
```

A variable declaration should have at least one variable declared.

A array is declared if a subscript happens on the `variable` argument. The subscript must be use an integer literal, behaviour is otherwise unspecified.

A local variable should only be declared inside a [scope].

### Scopes

There is also a pair of commands named `{` and `}`.

The command `{` creates a lexical scope for local variables. The command `}` leaves the lexical scope.

Lexical scopes cannot be nested.

The scope commands can be described more formally as:

```
scope_block := '{' eol
               command_list
               '}' eol
```

### Expressions

A script is built not only of commands, but of expressions as weel. Those expressions are also mapped to commands in later compilation phrases. Meaning, when we say *command*, we may also be talking about expressions.

An expression may be an assignment to a variable:

```
asop := '=' | '+=' | '-+' | '*=' | '/=' | '+=@' | '-=@' | '=#'
expr_assignment := variable {whitespace} asop {whitespace} argument eol
```

May be an equality test operation:

```
expr_equality := argument {whitespace} '=' {whitespace} argument eol
```

May be an relational operation:

```
relop := '<' | '>' | '>=' | '<='
expr_relational := argument {whitespace} relop {whitespace} argument eol
```

May be an binary operation:

```
binop := '+' | '-' | '*' | '/' | '+@' | '-@'
expr_binary := variable {whitespace} '=' {whitespace} argument {whitespace} binop argument eol
```

Or may be an unary operation:

```
unaryop := '--' | '++'
expr_unary := (unaryop {whitespace} variable eol) 
            | (variable {whitespace} unaryop eol)
```

TODO use limited arguments (no string literal)

### Control-Flow Commands

TODO










TODO exclude string from arguments?
TODO do note arguments are ambigous
TODO alternators
TODO control flow
TODO mission directives
TODO SAN ANDREAS ALLOWS VARIABLES AND STRING CONSTANTS TO BEGIN WITH UNDERSCORES 
TODO commands such as var decl can be implemented at compiler or command def level


### Remarks

 + The lexical grammar is not regular because of the nestable *multi-line comments*.
 + The lexical grammar is not context-free either. Contextual information is needed in order to match each lexical category.







[string literals]:
[scope]:


[Wesser]: https://web.archive.org/web/20170111193059/http://www.gtamodding.com/wiki/GTA3script
[Wesser2]: http://pastebin.com/raw/YfLWLXJw

