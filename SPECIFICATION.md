**Note:** This is a draft. It may be wrong, incomplete and subject to change.

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
integer_literal := ['-'] integer_digit { (integer_digit | '-') }
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
floating_literal := ['-'] (floating_form1 | floating_form2)
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
text_literal := ('A'..'Z' | 'a'..'z') [ {atom_char} (atom_char - ':') ]
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
variable_name := ('A'..'Z' | 'a'..'z') [ {variable_char} (variable_char - ':') ]
```

A reference to a variable is a variable name optionally followed by an array subscript. The subscript may either use a variable name or an integer for indexing. Any character following the subscript should be ignored. Do note a subscript cannot happen twice.

```
subscript := '[' (variable_name | integer_literal) ']' 
variable := variable_name [ subscript {variable_char} ]
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

### Expressions

A script is built not only of commands, but of expressions as weel. Those expressions are also mapped to commands in later compilation phrases. Meaning, when we say *command*, we may also be talking about expressions.

An expression may be an assignment to a variable, an equality test, a relational operation, a binary operation or an unary operation.

```
expr := expr_assignment | expr_equality | expr_relational | expr_binary | expr_unary
```

#### Assignment Expression

```
asop := '=' | '+=' | '-+' | '*=' | '/=' | '+=@' | '-=@' | '=#'
expr_assignment := variable {whitespace} asop {whitespace} argument eol
```

#### Equality Expression

```
expr_equality := argument {whitespace} '=' {whitespace} argument eol
```

#### Relational Operation

```
relop := '<' | '>' | '>=' | '<='
expr_relational := argument {whitespace} relop {whitespace} argument eol
```

#### Binary Operation

```
binop := '+' | '-' | '*' | '/' | '+@' | '-@'
expr_binary := variable {whitespace} '=' {whitespace} argument {whitespace} binop argument eol
```

#### Unary Operation

```
unaryop := '--' | '++'
expr_unary := (unaryop {whitespace} variable eol) 
            | (variable {whitespace} unaryop eol)
```

TODO use limited arguments (no string literal)

### Statements

```
statement := label_statement | unlabeled_statement

label_name := {atom_char}
label_statement := label_name ':' [whitespace unlabeled_statement] eol

unlabeled_statement := primary_statement
                     | scope_statement
                     | if_statement
                     | ifnot_statement
                     | while_statement
                     | whilenot_statement
                     | repeat_statement
```

TODO label name can be empty yes
TODO label name may not match label literal

#### Primary Statement

```
primary_statement := {whitespace} (command | expr)
```

#### Labeled Statements


#### Scope Statement

There is also a pair of commands named `{` and `}`.

The command `{` creates a lexical scope for local variables. The command `}` leaves the lexical scope.

Lexical scopes cannot be nested.

```
command_scope_begin = '{' eol
command_scope_end = '}' eol

scope_statement := command_scope_begin
                   statement_list
                   command_scope_end
```


#### Conditional Statements

A conditional statement is a primary statement which produces a boolean result. The boolean result can be negated by prepending the primary statement with a `NOT` token.

```
conditional_statement := {whitespace} ['NOT' whitespaces] primary_statement
```

A conditional list is either a single conditional statement or multiple conditional statements concatenated by `AND` or `OR` tokens. Those tokens cannot be combined.

```
and_conditional_stmt := 'AND' whitespaces conditional_statement
or_conditional_stmt := 'OR' whitespaces conditional_statement

conditional_list := conditional_statement
                    ({and_conditional_stmt} | {or_conditional_stmt})
```

In case of a single conditional, the list boolean result is the same as its conditional statement.

In case of multiple conditionals, all statements are executed and the boolean result of the list is:

 + If `AND` was used and all conditional statements give a true boolean result, the list boolean result is true.
 + If `OR` was used and at least one conditional statement gives a true boolean result, the list boolean result is true.
 + In any other case, the boolean result is false.

#### IF Statement

An IF statement is an `IF` command followed by a list of statements to be executed in case its boolean result is true. The statements are executed until a matching `ELSE` or `ENDIF` command are found.

If a matching `ELSE` exists and the `IF` boolean result is false, all statements from the `ELSE` until the matching `ENDIF` are executed.

The boolean result of an `IF` command is the same as the conditional list it holds.

```
command_if := 'IF' whitespaces conditional_list
command_else := 'ELSE' eol
command_endif := 'ENDIF' eol

if_statement := command_if
                statement_list
                [command_else
                statement_list]
                command_endif
```

#### IFNOT Statement

The `IFNOT` statement is specified the same way as the `IF` statement, except the `IFNOT` command boolean result is the complement of `IF` boolean result.

```
command_ifnot := 'IFNOT' whitespaces conditional_list

ifnot_statement := command_ifnot
                   statement_list
                   [command_else
                   statement_list]
                   command_endif
```

#### WHILE Statement

A `WHILE` statement is a `WHILE` command followed by a list of statements to be executed. The list of such commands ends when an matching `ENDWHILE` is found.

This statement executes by executing its conditional list, checking its boolean result and making a choice:
 
  + In case it is true, execute the list of statements given, then re-execute the conditional list and make a choice again.
  + In case it is false, skip to its matching `ENDWHILE`.

The boolean result of the `WHILE` command is the same as the conditional list it holds.

```
command_while := 'WHILE' whitespaces conditional_list
command_endwhile := 'ENDWHILE' eol

while_statement := command_while
                   statement_list
                   command_endwhile
```

#### WHILENOT Statement

The `WHILENOT` statement is specified the same way as the `WHILE` statement, except the `WHILENOT` command boolean result is the complement of the boolean result of the `WHILE` command.

```
command_whilenot := 'WHILENOT' whitespaces conditional_list

whilenot_statement := command_whilenot
                      statement_list
                      command_endwhile
```

#### REPEAT Statement

TODO describe repeat

TODO describe args, note that variable must be global variable, and string constants only the global ones (right?), and argument is not all arg kinds

```
command_repeat := 'REPEAT' whitespaces argument whitespaces variable eol
command_endrepeat = 'ENDREPEAT'

repeat_statement := command_repeat
                    statement_list
                    command_endrepeat
```


### Remarks

 + The lexical grammar is not regular because of the nestable *multi-line comments*.
 + The lexical grammar is not context-free either. Contextual information is needed in order to match each lexical category.
 + NO SHORTCIRCUIT IN CONDITIONAL LIST




TODO exclude string from arguments?
TODO do note arguments are ambigous
TODO alternators
TODO mission directives
TODO SAN ANDREAS ALLOWS VARIABLES AND STRING CONSTANTS TO BEGIN WITH UNDERSCORES 
TODO commands such as var decl can be implemented at compiler or command def level



[string literals]:
[scope]:


[Wesser]: https://web.archive.org/web/20170111193059/http://www.gtamodding.com/wiki/GTA3script
[Wesser2]: http://pastebin.com/raw/YfLWLXJw

