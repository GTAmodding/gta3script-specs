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

multiscripts

script file

internal command

jump

subrountine

compare flag

global string constant


Notation
---------------------

TODO

Concepts
--------------------

### Scripts

A script is a unit of execution which containts its own program counter, local variables and compare flag.

A command is an action to be performed by such a script during an instant of time.

A script file is a source file containing a sequence of commands. Those commands may be executed concurrently by multiple scripts.

### Types

A integer is a signed 32-bit integral number.

A floating-point is a representation of a real number.

A label is the location of a command.

A text label is a identifier mapping to a runtime value which is yet unknown during the compilation phrase.

TODO string constants have their own type (we call it constant?)

TODO string type (of string literal)

TODO probably should describe better this stuff.


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

A graphical character is any printable character excluding whitespaces.

```
graph_char := ascii_printable - whitespace ;
```

To simplify future definitions, we define the productions `eol` as the end of a line, and `sep` as a token separator.

```
sep := whitespace {whitespace} ;
eol := newline | EOF ;
```

### Comments

Comments serve as program documentation.

```
comment := line_comment | block_comment ;
line_comment := '//' {ascii_char} eol ;
block_comment := '/*' {block_comment | ascii_char} '*/' ;
```

There are two forms:

 + *Line comments* starts with the character sequence `//` and stop at the end of the line.
 + *Block comments* starts with the character sequence `/*` and stop with its matching `*/`. Block comments can be nested inside each other.

The contents of comments shall be interpreted as if it were whitespaces in the source code.

Comments cannot start inside string literals.

### Command

A command describes an action a script should perform.

```
command_name := graph_char {graph_char} ;
command := command_name { argument } eol ;
```

There are several types of arguments.

```
argument := sep (
               integer
             | floating 
             | variable 
             | label
             | filename 
             | string_identifier 
             | string_constant
             | string_literal 
             );
```

### Integer Literal

```
digit := '0'..'9';
integer := ['-'] digit {digit | '-'} ;
```

A integer literal is a sequence of digits and minus signs.

If the literal begins with a minus, the number following it should be negated.

If the `-` character happens anywhere but in the first character, all characters following and including the minus should be ignored.

To make it clear, the following literals are valid and act as if they were the literal on the right.

| Literal | Same As |
| ------  | ------- |
| 1       | 1       |
| 010     | 10      |
| -39     | -39     |
| -432-10 | -432    |

**Semantics**

The type of a integer literal is a integer.

### Floating-Point Literals

```
floating_form1 := '.' digit { digit | '.' | 'f' | 'F' } ;
floating_form2 := digit { digit } ('.' | 'f' | 'F') { digit | '.' | 'f' | 'F' } ;
floating := ['-'] (floating_form1 | floating_form2) ;
```

A floating-point literal is a nonempty sequence of digits which must contain at least one occurence of the characters `.`, `f` or `F`.

Once the `f` or `F` characters are found, all characters including and following it should be ignored. The same should happen when the character `.` is found a second time.

The literal may be preceeded by a minus sign, which should negate the floating-point number.

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

**Semantics**

The type of a floating-point literal is a float.

### String Identifiers

A string identifier is a identifier which is resolved during runtime.

```
string_identifier := ('A'..'Z') [ {graph_char} (graph_char - ':') ] ;
```

**Semantics**

The type of a string identifier is a text label.

### String Constant

A string constant is category of identifier which is resolved to integers during compilation.

```
string_constant := ('A'..'Z') [ {graph_char} (graph_char - ':') ] ;
```

**Semantics**

The type of a string constant is a constant.

### String Literal

A string literals holds a sequence of ASCII characters delimited by quotation marks.

```
string_literal := '"' { ascii_char - (newline | '"') } '"' ;
```

**Semantics**

The type of a string literal is a string.

### Label Identifiers

A label identifier is a identifier referencing a script label.

```
label := ('A'..'Z') [ {graph_char} (graph_char - ':') ] ;
```

**Semantics**

The type of a label identifier is a label.

### Filename Identifiers

A filename identifier is a identifier referencing another script file.

```
filename := {graph_char} '.SC' ;
```

**Semantics**

The type of a filename identifier is a label.

Filename identifiers cannot be used in the same context as labels. Only specific commands (described later) may use this class of identifier.

### Variable Reference

The name of a variable is a sequence of graphical characters, except the characters `[` and `]` cannot happen.

```
variable_char := graph_char - ('[' | ']') ;
variable_name := ('A'..'Z') [ {variable_char} (variable_char - ':') ] ;
```

A reference to a variable is a variable name optionally followed by an array subscript. Any character following the subscript should be ignored. A subscript cannot happen twice.

```
subscript := '[' (variable_name | integer_literal) ']' ;
variable := variable_name [ subscript {variable_char} ] ;
```

**Semantics**

The subscript may use a integer literal or another variable name of integer type.

The type of a variable reference is the inner type of the variable name being referenced.

Some commands may accept either local variables or global variables, not both.

Command Selectors
------------------------

A command selector (or alternator) is a kind of command which gets rewriten by the compiler to another command based on the supplied argument types.

A command selector consists of its name and a set of commands which are alternatives for replacement.

Once a command name is identified as a selector, the argument list is tested over each command in the set of alternatives. The compilation then behaves as if the command name was rewriten as the matching command name.

The behaviour is unspecified if more than one command in the set produces a match.

A list of selectors and theirs selection sets can be found in the appendix (TODO).

**Example** 

As an example, consider the command selector `SET` used in the following contexts:

| Selector Used As              | Rewriten As                                        |
| ----------------------------- | -------------------------------------------------- |
| `SET lvar_int 10`             | `SET_LVAR_INT lvar_int 10`                         |
| `SET lvar_flt var_flt`        | `SET_LVAR_FLOAT_TO_VAR_FLOAT lvar_flt var_flt`     |
| `SET var_int STRING_CONSTANT` | `SET_VAR_INT_TO_CONSTANT var_int STRING_CONSTANT`  |

For the first example, each command in the collection of alternatives for `SET` was evaluated with the arguments `lvar_int 10`. One must have produced a successful compilation, and that one was choosen as the replacement command.

The same happens for the other examples in the table.

Expressions
-------------------------

A expression is a shortcut for one or more command selectors.

```
expression := expr_rtol
            | expr_binary 
            | expr_unary ;
```

The arguments of an expression may not allow string literals.

### Assignment, Equality and Relational Operators

```
asop := '=' | '+=' | '-=' | '*=' | '/=' | '+=@' | '-=@' | '=#' ;
relop := '<' | '>' | '>=' | '<=' ;
expr_rtol := argument {whitespace} (asop | relop) {whitespace} argument eol ;
```

These expressions should be rewritten as the following selectors:

| Operation | Command Selector                               |
| --------- | ---------------------------------------------- |
| `a = b`   | `SET a b`                                      |
| `a = b`   | `IS_THING_EQUAL_TO_THING a b`                  |
| `a =# b`  | `CSET a b`                                     |
| `a += b`  | `ADD_THING_TO_THING a b`                       |
| `a -= b`  | `SUB_THING_FROM_THING a b`                     |
| `a *= b`  | `MULT_THING_BY_THING a b`                      |
| `a /= b`  | `DIV_THING_BY_THING a b`                       |
| `a +=@ b` | `ADD_THING_TO_THING_TIMED a b`                 |
| `a -=@ b` | `SUB_THING_FROM_THING_TIMED a b`               |
| `a > b`   | `IS_THING_GREATER_THAN_THING a b`              |
| `a >= b`  | `IS_THING_GREATER_OR_EQUAL_TO_THING a b`       |
| `a < b`   | `IS_THING_GREATER_THAN_THING b a`              |
| `a <= b`  | `IS_THING_GREATER_OR_EQUAL_TO_THING b a`       |

A rule to differentiate between assignment and equality (`=`) is given in the definition of conditional statements.

### Binary Operations

```
binop := '+' | '-' | '*' | '/' | '+@' | '-@' ;
expr_binary := argument {whitespace} '=' {whitespace} argument {whitespace} binop argument eol ;
```

A operation of the form `a = b + c` should be rewritten as either:
 
 + `ADD_THING_TO_THING a c` if the name `a` is the same as the name `b`.
 + `ADD_THING_TO_THING a b` if the name `a` is the same as the name `c`.
 + `SET a b` followed by `ADD_THING_TO_THING a c` otherwise.

A operation of the form `a = b - c` should be rewritten as either:

 + `SUB_THING_FROM_THING a c` if the name `a` is the same as the name `b`.
 + Implementation-defined if `a` is the same name as `c`.
 + `SET a b` followed by `SUB_THING_BY_THING a c` otherwise.

A operation of the form `a = b * c` should be rewritten under the same rules as `a = b + c`, except by using `MULT_THING_BY_THING` instead of `ADD_THING_TO_THING`.

A operation of the form `a = b / c` should be rewritten under the same rules as `a = b - c`, except by using `DIV_THING_BY_THING` instead of `SUB_THING_FROM_THING`.

A operation of the form `a = b +@ c` and `a = b -@ c` should be rewritten under the same rules as `a = b - c`, except by using `ADD_THING_TO_THING_TIMED` and `SUB_THING_FROM_THING_TIMED`, respectively, instead of `SUB_THING_FROM_THING`.

### Unary Operation

```
unop := '--' | '++' ;
expr_unary := (unop {whitespace} argument eol) 
            | (argument {whitespace} unop eol) ;
```

The operations `++a` and `a++` should be rewritten as `ADD_THING_TO_THING a 1`.

The operations `--a` and `a--` should be rewritten as `SUB_THING_FROM_THING a 1`.

Both prefix and postfix unary operations are the same.

Statements
--------------------------------

A statement specifies an action to be executed.

```
statement := labeled_statement 
           | embedded_statement ;
```

### Labeled Statements

Statements may be prefixed with a label.

```
label_name := {graph_char} ;
labeled_statement := label_name ':' (sep embedded_statement | empty_statement) ;
```

**Constraints**

The name of a label must be unique across the multi-file.

**Semantics**

This label may be referenced in certain commands to transfer (or start) control-flow of execution to the statement it prefixes. Labels themselves do not alter the flow of control, which continues to the statement it enbodies.

The name of a label may be empty. The name of a label may contain characters that do not match the `text_literal` production. In such cases, the label cannot be used as arguments to commands.

### Empty Statements

An empty statement does nothing.

```
empty_statement := eol ;
```

### Embedded Statements

Embedded statements are statements not prefixed by a label.

```
embedded_statement := empty_statement
                     | primary_statement
                     | scope_statement
                     | var_statement
                     | if_statement
                     | ifnot_statement
                     | while_statement
                     | whilenot_statement
                     | repeat_statement ;

```

### Primary Statement

```
primary_statement := (command | expression) ;
```

**Constraints**

The command it enbodies cannot be any of the internal commands.

**Semantics**

The execution of a primary statement takes place by executing the command or expression it embodies.

### Scope Statement

```
command_scope_activate := '{' eol ;
command_scope_finish := '}' eol ;

scope_statement := command_scope_activate
                   {statement}
                   command_scope_finish ;
```

**Constraints**

Lexical scopes cannot be nested.

**Semantics**

The command `{` activates a lexical scope where local variables can be declared or used.

The command `}` finishes such a lexical scope.

The active scope is finished when control-flow of a script is transfered to outside the active lexical scope by a jump.

The transfer of control to the middle of a inactive lexical scope activates it.

Transfer of control to a subroutine shall not deactivate the active scope. The behaviour of the script is unspecified if such a subroutine activates another lexical scope.

### Variable Statement

```
command_var_name := 'VAR_INT' 
                    | 'LVAR_INT'
                    | 'VAR_FLOAT'
                    | 'LVAR_FLOAT' ;
command_var_param := sep variable ;

var_statement := command_var_name command_var_param {command_var_param} eol ;
```

The declaration command name is a pair of storage duration and variable type.

The commands with the `VAR_` prefix declares global variables. The ones with `LVAR_` declares local variables. The `INT` suffix declares variables capable of storing and having type integer. The `FLOAT` suffix declares floating-point ones.

**Constraints**

Global variable names must be unique across the multi-file.

Local variable may have identical names as long as they are in different lexical scopes.

Local variables cannot have the same name as any global variable.

**Semantics**

This command declares one or more names with the specified storage duration, data type, and array dimensions.

Global variable names can be seen by the entire multi-file.

Local variable names can be seen by their entire lexical scope.

### Conditional Statements

Conditional statements produce changes in the script compare flag.

```
conditional_statement := ['NOT' sep] primary_statement ;

and_conditional_stmt := 'AND' sep conditional_statement ;
or_conditional_stmt := 'OR' sep conditional_statement ;

conditional_list := conditional_statement
                    ({and_conditional_stmt} | {or_conditional_stmt}) ;
```

**Semantics**

The compare flag of a conditional statement is the same as the primary statement it enbodies.

The compare flag is negated by prepending the statement by a `NOT`. 

A conditional list is either a conditional statement or a combination of these by the use of either `AND` or `OR` tokens.

The compare flag is set to true if the compare flag of all conditional statements in a `AND` list holds true.

The compare flag is set to true if the compare flag of at least one conditional statement in a `OR` list holds true.

In any other case, the compare flag is set to false.

There is no short-circuit evaluation. All conditional statements in a conditional list are executed. They are also executed in order.

If the primary statement of a conditional statement is a expression with a operator of type `=`, equality comparision is choosen over assignment.

### Selection Statements

Selection statements selects statements to execute from a set of statements depending on a list of conditions.

#### IF Statement

```
command_if := 'IF' sep conditional_list ;
command_else := 'ELSE' eol ;
command_endif := 'ENDIF' eol ;

if_statement := command_if
                {statement}
                [command_else
                {statement}]
                command_endif ;
```

**Semantics**

The `IF` command executes a conditional list, grabs its compare flag and chooses between two set of statements to execute.

If the compare flag is true, control is transfered to the first set of statements. Otherwise, to the second set (if an `ELSE` exists) or to the end of the construct.

#### IFNOT Statement

```
command_ifnot := 'IFNOT' sep conditional_list ;

ifnot_statement := command_ifnot
                   {statement}
                   [command_else
                   {statement}]
                   command_endif ;
```

**Semantics**

The behaviour of this statement is the same as of the IF statement, except the `IFNOT` command acts differently.

The `IFNOT` command executes a conditional list, grabs the complement of its compare flag, then chooses between the two sets of statements to execute.

### Iteration Statements

#### WHILE Statement

```
command_while := 'WHILE' sep conditional_list ;
command_endwhile := 'ENDWHILE' eol ;

while_statement := command_while
                   {statement}
                   command_endwhile ;
```

**Semantics**

The while statement executes a set of statements while the conditional list holds true.

The `WHILE` command executes a conditional list, grabs its compare flag, and transfers control to after the `ENDWHILE` if it's false. Otherwise, it executes the set of statements given, and then transfers control back again to the `WHILE` command.

#### WHILENOT Statement

```
command_whilenot := 'WHILENOT' sep conditional_list ;

whilenot_statement := command_whilenot
                      {statement}
                      command_endwhile ;
```

**Semantics**

This is the analogous to the IFNOT statement in relation to the IF statement, meaning the statements are executed while the conditional list holds false.

#### REPEAT Statement

```
command_repeat := 'REPEAT' sep integer sep variable eol ;
command_endrepeat := 'ENDREPEAT' eol ;

repeat_statement := command_repeat
                    {statement}
                    command_endrepeat ;
```

**Constraints**

The first argument to `REPEAT` must be a integer literal.

The second argument must be a variable of integer type.

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
TODO timera timerb
TODO shall should must etc



[string literals]:
[scope]:


[Wesser]: https://web.archive.org/web/20170111193059/http://www.gtamodding.com/wiki/GTA3script
[Wesser2]: http://pastebin.com/raw/YfLWLXJw

[miss2.exe]: https://www.dropbox.com/s/7xgvqo8b9u1qw02/gta3sc_v413.rar
[miss2_strings]: http://pastebin.com/raw/Pjb0Ezkx
[gtasa_listing]: https://pastebin.com/2VczpwK7


