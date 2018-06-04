**Note:** This is a draft. It may be wrong, incomplete and subject to change.

Introduction
---------------------

This is an attempt to produce a somewhat formal language specification for the GTA3script language.

GTA3script is a rather simple scripting language built by DMA Design (now Rockstar North) to design the mission scripts of its Grand Theft Auto series. It's so simple that it has a huge amount of quirks uncommon to other languages. This document attempts to pull together all those tricks in a coherent way.

Previous work has been done by [Wesser]. However it's not (nor meant to be) structured formally. That said, this document wouldn't be possible without his huge research effort on describing the language.

Scope
---------------------

This document is targeted at compiler writers and perhaps curious community members.

This document specifies the syntax, constraints and semantic rules of the GTA3script language.

This document does not specify a runtime system nor does it specify mechanisms by which the language is transformed for use by such a system.

Terms and Definitions
---------------------

TODO

multi-file

internal command

jump

subrountine

compare flag

global string constant


Notation
---------------------

TODO

Elements
---------------------

The lexical grammar of the language is context-sensitive. As such, the lexical elements and the syntactic elements will be presented together.

### Source Code

Source code is a stream of printable ASCII characters plus the control codes line feed (`\n`), horizontal tab (`\t`) and carriage return (`\r`).

```
ascii_char := ascii_printable | ascii_control ;
ascii_printable := /* printable ASCII characters */ ;
ascii_control := '\n' | '\t' | '\r' ;
```

Carriage returns should appear only before a line feed.

Lowercase letters in the stream should be interpreted as its uppercase equivalent.

Space, horizontal tab, parentheses and comma are defined as whitespace characters.

```
whitespace := ' ' | '\t' | '(' | ')' | ',' ;
```

A line is a sequence of characters delimited by a newline. The start of the stream begins a line. The end of the stream finishes a line.

```
newline := ['\r'] `\n` ;
```

Each line should be interpreted as if there was no whitespaces in either ends of the line.

We also define `atom_char` which will be the building blocks for identifiers.

```
atom_char := ascii_printable - (ascii_control | whitespace)
```

### Token Separator and End Of Line

To simplify future definitions, we define the productions: `eol` as the end of a line, and `sep` as a token separator.

 + `sep` is a token separator.
 + `eol` is the end of a line.

```
sep := whitespace {whitespace}
eol := newline | EOF
```

### Comments

Comments serve as program documentation.

```
comment := line_comment | block_comment ;
line_comment := '//' {ascii_char} eol
block_comment := '/*' {block_comment | ascii_char} '*/'
```

There are two forms:

 + *Line comments* starts with the character sequence `//` and stop at the end of the line.
 + *Block comments* starts with the character sequence `/*` and stop with its matching `*/`. Block comments can be nested inside each other.

The contents of comments shall be interpreted as if it were whitespaces in the source code.

Comments cannot start inside string literals.

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
argument := sep ( integer_literal | floating_literal | text_label_literal | label_literal | string_constant | string_literal | filename_literal | variable )
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

Variable Declaration
---------------------------

A variable declaration happens by placing a declaration command followed by the variable names to be declared.

The declaration command names are a pair of the variable scoping rules and the variable static type.

```
command_var_decl_name := 'VAR_INT' | 'LVAR_INT' | 'VAR_FLOAT' | 'LVAR_FLOAT'
command_var_decl_arg := sep variable
command_var_decl := command_var_decl_name command_var_decl_arg {command_var_decl_arg} eol
```

A variable declaration should have at least one variable declared.

A array is declared if a subscript happens on the `variable` argument. The subscript must be use an integer literal, behaviour is otherwise unspecified.

A local variable should only be declared inside a [scope].

Expressions
-------------------------

A script is built not only of commands, but of expressions as weel. Those expressions are also mapped to commands in later compilation phrases. Meaning, when we say *command*, we may also be talking about expressions.

An expression may be an assignment to a variable, an equality test, a relational operation, a binary operation or an unary operation.

```
expression := expr_assignment | expr_equality | expr_relational | expr_binary | expr_unary
```

### Assignment Expression

```
asop := '=' | '+=' | '-+' | '*=' | '/=' | '+=@' | '-=@' | '=#'
expr_assignment := variable {whitespace} asop {whitespace} argument eol
```

### Equality Expression

```
expr_equality := argument {whitespace} '=' {whitespace} argument eol
```

### Relational Operation

```
relop := '<' | '>' | '>=' | '<='
expr_relational := argument {whitespace} relop {whitespace} argument eol
```

### Binary Operation

```
binop := '+' | '-' | '*' | '/' | '+@' | '-@'
expr_binary := variable {whitespace} '=' {whitespace} argument {whitespace} binop argument eol
```

### Unary Operation

```
unaryop := '--' | '++'
expr_unary := (unaryop {whitespace} variable eol) 
            | (variable {whitespace} unaryop eol)
```

TODO use limited arguments (no string literal)

Statements
--------------------------------

A statement specifies an action to be executed.

```
statement := labeled_statement 
           | embedded_statement
```

### Labeled Statements

Statements may be prefixed with a label.

```
label_name := {atom_char}
labeled_statement := label_name ':' (sep embedded_statement | empty_statement)
```

**Constraints**

The name of a label must be unique across the multi-file.

**Semantics**

This label may be referenced in certain commands to transfer (or start) control-flow of execution to the statement it prefixes. Labels themselves do not alter the flow of control, which continues to the statement it enbodies.

The name of a label may be empty. The name of a label may contain characters that do not match the `text_literal` production. In such cases, the label cannot be used as arguments to commands.

### Empty Statements

An empty statement does nothing.

```
empty_statement := eol
```

### Embedded Statements

Embedded statements are statements not prefixed by a label.

```
embedded_statement := empty_statement
                     | primary_statement
                     | scope_statement
                     | if_statement
                     | ifnot_statement
                     | while_statement
                     | whilenot_statement
                     | repeat_statement

```

### Primary Statement

```
primary_statement := (command | expression)
```

**Constraints**

The command it enbodies cannot be any of the internal commands.

**Semantics**

The execution of a primary statement takes place by executing the command or expression it embodies.

### Scope Statement

```
command_scope_activate = '{' eol
command_scope_finish = '}' eol

scope_statement := command_scope_activate
                   {statement}
                   command_scope_finish
```

**Constraints**

Lexical scopes cannot be nested.

**Semantics**

The command `{` activates a lexical scope where local variables can be declared or used.

The command `}` finishes such a lexical scope.

The active scope is finished when control-flow of a script is transfered to outside the active lexical scope by a jump.

The transfer of control to the middle of a inactive lexical scope activates it.

Transfer of control to a subroutine shall not deactivate the active scope. The behaviour of the script is unspecified if such a subroutine activates another lexical scope.

### Conditional Statements

Conditional statements produce changes in the script compare flag.

```
conditional_statement := ['NOT' sep] primary_statement

and_conditional_stmt := 'AND' sep conditional_statement
or_conditional_stmt := 'OR' sep conditional_statement

conditional_list := conditional_statement
                    ({and_conditional_stmt} | {or_conditional_stmt})
```

**Semantics**

The compare flag of a conditional statement is the same as the primary statement it enbodies.

The compare flag is negated by prepending the statement by a `NOT`. 

A conditional list is either a conditional statement or a combination of these by the use of either `AND` or `OR` tokens.

The compare flag is set to true if the compare flag of all conditional statements in a `AND` list holds true.

The compare flag is set to true if the compare flag of at least one conditional statement in a `OR` list holds true.

In any other case, the compare flag is set to false.

There is no short-circuit evaluation. All conditional statements in a conditional list are executed. They are also executed in order.

### Selection Statements

Selection statements selects statements to execute from a set of statements depending on a list of conditions.

#### IF Statement

```
command_if := 'IF' sep conditional_list
command_else := 'ELSE' eol
command_endif := 'ENDIF' eol

if_statement := command_if
                {statement}
                [command_else
                {statement}]
                command_endif
```

**Semantics**

The `IF` command executes a conditional list, grabs its compare flag and chooses between two set of statements to execute.

If the compare flag is true, control is transfered to the first set of statements. Otherwise, to the second set (if an `ELSE` exists) or to the end of the construct.

#### IFNOT Statement

```
command_ifnot := 'IFNOT' sep conditional_list

ifnot_statement := command_ifnot
                   {statement}
                   [command_else
                   {statement}]
                   command_endif
```

**Semantics**

The behaviour of this statement is the same as of the IF statement, except the `IFNOT` command acts differently.

The `IFNOT` command executes a conditional list, grabs the complement of its compare flag, then chooses between the two sets of statements to execute.

### Iteration Statements

#### WHILE Statement

```
command_while := 'WHILE' sep conditional_list
command_endwhile := 'ENDWHILE' eol

while_statement := command_while
                   {statement}
                   command_endwhile
```

**Semantics**

The while statement executes a set of statements while the conditional list holds true.

The `WHILE` command executes a conditional list, grabs its compare flag, and transfers control to after the `ENDWHILE` if it's false. Otherwise, it executes the set of statements given, and then transfers control back again to the `WHILE` command.

#### WHILENOT Statement

```
command_whilenot := 'WHILENOT' sep conditional_list

whilenot_statement := command_whilenot
                      {statement}
                      command_endwhile
```

**Semantics**

This is the analogous to the IFNOT statement in relation to the IF statement, meaning the statements are executed while the conditional list holds false.

#### REPEAT Statement

```
command_repeat := 'REPEAT' sep integer_literal sep variable eol
command_endrepeat = 'ENDREPEAT' eol

repeat_statement := command_repeat
                    {statement}
                    command_endrepeat
```

**Constraints**

The first argument to `REPEAT` must be a integer literal.

The second argument must be a global variable of integer type.

**Semantics**

The repeat statement executes a set of statements until a counter variable reaches a threshold.

More precisely, the counter variable is set to zero, the statements are executed, then the variable is incremented and if it is still less than the threshold, control is transfered back to the statements again.

The statements are always executed at least once.

Remarks
------------

 + The lexical grammar is not regular because of the nestable *multi-line comments*.
 + The lexical grammar is not context-free either. Contextual information is needed in order to match each lexical category.
 + THIS IS A BROKEN LANGUAGE :)
 + NO SHORTCIRCUIT IN CONDITIONAL LIST
 + miss2 allows other chars other than the ones specified in source representation thus why we specify it (it is buggy)
 + control chars behave in a weird way in miss2 (including CR)

miss2 cannot be the reference implementation because of bugs such as

```
IF {
ENDIF
```




TODO exclude string from arguments?
TODO do note arguments are ambigous
TODO alternators
TODO mission directives
TODO SAN ANDREAS ALLOWS VARIABLES AND STRING CONSTANTS TO BEGIN WITH UNDERSCORES 
TODO commands such as var decl can be implemented at compiler or command def level
TODO types
TODO scripts subscripts and such
TODO translation limits
TODO initial value of locals are undefined
TODO describe goto and such inside a lexical scope to another lexical scope (or none)
TODO what about commands that do not produce compare flag changes but may appear in a conditional statement


[string literals]:
[scope]:


[Wesser]: https://web.archive.org/web/20170111193059/http://www.gtamodding.com/wiki/GTA3script
[Wesser2]: http://pastebin.com/raw/YfLWLXJw

[miss2.exe]: https://www.dropbox.com/s/7xgvqo8b9u1qw02/gta3sc_v413.rar
[miss2_strings]: http://pastebin.com/raw/Pjb0Ezkx
[gtasa_listing]: https://pastebin.com/2VczpwK7


