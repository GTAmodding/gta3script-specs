**Note:** This is a draft. It may be wrong, incomplete and subject to change.

Introduction
---------------------

This is an attempt to produce a formal language specification for the GTA3script language. 

GTA3script is an imperative, strong and statically typed scripting language built by DMA Design (now Rockstar North) to design the mission scripts in Grand Theft Auto game series.

The language is very basic and contains a huge amount of quirks uncommon to other languages. This document attempts to pull together all those tricks in a coherent way.

Scope
---------------------

This document is targeted at implementation writers and perhaps curious community members.

This document specifies the syntax, constraints and semantic rules of the GTA3script language.

This document does not specify a runtime system nor does it specify mechanisms by which the language is transformed for use by such a system.

Terms and Definitions
---------------------

**behaviour**

external appearance or action.

**behaviour, implementation-defined**

behavior specific to an implementation, where that implementation must document that behavior.

**behaviour, undefined**

behavior which is not guaranteed to produce any specific result.

**behaviour, unspecified**

behavior for which this specification provides no requirements.

**constraint**

restriction, either syntactic or semantic, on how language elements can be used.

**execution environment**

the software on which the result of translation is executed on.

**translation environment**

the software on which the language is translated for use by an execution environment.

**implementation**

particular set of software, running in a particular translation environment under particular control options, that performs translation of programs for, and supports execution of commands in, a particular execution environment.

**value**

precise meaning of the contents of an name when interpreted as having a specific type.

**argument**

a value passed to a command that is intended to map to a corresponding parameter.

**parameter**

the value to be received in a specific argument position of a command.

Notation
---------------------

TODO

Concepts
--------------------

### Scripts

A **script** is a unit of execution which containts its own *program counter*, *local variables* and *compare flag*.

A **variable** is a named storage location. This location holds a value of specific type.

There are global and local variables. **Global variables** are stored in a way they are accessible from any script. **Local variables** are said to pertain to the particular script and only accessible from it.

The lifetime of a *global variable* is the same as of the execution of all scripts. The lifetime of a *local variable* is the same as its script and lexical scope.

A **command** is an operation to be performed by a script. Commands may produce several **side-effects** which are described by each command description.

A possible side-effect of executing a command is the updating of the *compare flag*. The **compare flag** of a command is the boolean result it produces. The **compare flag of a script** is the *compare flag* of the its last executed command. The *compare flag* is useful for conditionally changing the *flow of control*.

The **program counter** of a script indicates its currently executing command. Unless one of the *side-effects* of a command is to change the *program counter*, the counter goes from the current command to the next sequentially. An explicit change in the *program counter* is said to be a change in the *flow of control*.

A command is said to perform a **jump** if it changes the *flow of control* irreversibly.

A command is said to call a **subroutine** if it changes the *flow of control* but saves the current *program counter* in a stack to be restored later.

A command is said to **terminate** a script if it halts and reclaims storage and states of such a script.

### Script Files

A **script file** is a source file containing a sequence of commands. Those commands may be executed concurrently by multiple scripts.

The **multi-file** is a collection of *script files*. Hereafter being the collection of *script files* being translated.

The **main script file** is the entry script file. This is where the first script (called the **main script**) starts execution. Translation begins here.

Other script files are **required** to become part of the *multi-file* by the means of require statements within the *main script file*. Many kinds of script files may be *required*.

A **main extension file** (or **foreign gosub file**) is a script file required by the means of a *GOSUB_FILE statement*. Other script files may be required from here as well.

A **subscript file** is a script file required by the means of the *LAUNCH_MISSION statement*. A **subscript** is a script started by the same statement.

A **mission script file** is a script file required by the means of the *LOAD_AND_LAUNCH_MISSION statement*. A **mission script** is a script started by the same statement. Only a single *mission script* may be running at once.

Commands in the *main script file*, *main extension files* and *subscript files* shall not refer to labels in *mission script files*. A *mission script file* shall not refer to labels in other *mission script files*.

The *main script file* is found in a unspecified manner. The other *script files* are found by recursively searching a directory with the same filename (excluding extension) as the *main script file*. This directory is in the same path as the *main script file*. The search for the *script files* should be case-insensitive. All *script files* must have a `.sc` extension. If multiple script files with the same name are found, behaviour is unspecified.

### Types

Due to the command-driven nature of the language, typing rules are applied to *argument* and *parameters* of commands.

The language is statically typed. The type of every *argument* and *parameter* is known by the translator.

The language is strongly typed. One type of *argument* cannot be converted to another in order to fit the requirement of a *parameter*.

A **integer** is a binary, signed integral number. It represents 32 bits of data and the range of values *-2147483648* through *2147483647*.

A **floating-point** is a representation of a real number. Its exact representation, precision and range of values is implementation-defined.

A **label** is a name specifying the location of a command.

A **text label** is a name whose value is only known in the execution environment.

A **constant** is a name whose value is known in the translation environment. The value of a *constant* is an *integer* value but these types are distinct.

A **string** is a sequence of zero or more characters.

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

A graphical character is any printable character excluding whitespaces and quotation marks.

```
graph_char := ascii_printable - (whitespace | '"') ;
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

The contents of comments shall be interpreted as if it were whitespaces in the source code. More specifically: 

 + A *line comment* should be interpreted as an `eol`.
 + A single, nested, *block comment* should be interpreted as an `eol` on each line boundary it crosses. On its last line (i.e. the one it does not cross), it should be interpreted as one or more `whitespace` characters.

Comments cannot start inside string literals.

### Commands

A command describes an operation a script should perform.

```
command_name := graph_char {graph_char} ;
command := command_name { sep argument } ;
```

There are several types of arguments.

```
argument := integer
          | floating 
          | identifier
          | variable 
          | string_literal ;
```

### Integer Literals

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
floating_form1 := '.' digit { digit | '.' | 'F' } ;
floating_form2 := digit { digit } ('.' | 'F') { digit | '.' | 'F' } ;
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

### Identifiers

```
identifier := ('$' | 'A'..'Z') {graph_char} ;
```

**Constraints**

An identifier should not end with a `:` character.

**Semantics**

The type of a string identifier is a text label.

The type of a string constant is a constant.

The type of a label identifier is a label.

TODO explain semantics better (also note how string identifier cannot start with `$`).

### String Literals

A string literal holds a string delimited by quotation marks.

```
string_literal := '"' { ascii_char - (newline | '"') } '"' ;
```

**Semantics**

The type of a string literal is a string.

### Variable References

The name of a variable is a sequence of graphical characters, except the characters `[` and `]` cannot happen.

```
variable_char := graph_char - ('[' | ']') ;
variable_name := ('$' | 'A'..'Z') {variable_char} ;
```

A reference to a variable is a variable name optionally followed by an array subscript. Any character following the subscript should be ignored. A subscript cannot happen twice.

```
subscript := '[' (variable_name | integer_literal) ']' ;
variable := variable_name [ subscript {variable_char} ] ;
```

**Constraints**

A variable name should not end with a `:` character.

**Semantics**

The subscript may use a integer literal or another variable name of integer type.

The type of a variable reference is the inner type of the variable name being referenced.

Some commands may accept either local variables or global variables, not both.

Argument Matching
------------------------

A command may accept parameters of either integer, float, label, text label or string type.

A command may also accept a **multi-parameter**. A *multi-parameter* is a restricted union of the integer and float type.

A command parameter may only accept variables (of either kinds), only accept local variables or only accept global variables. A parameter accepting only variables should have an identifier argument matching a variable reference.

Each command have its own parameters description which should be described with the command.

### Integer

TODO

### Float

TODO

### Label

A parameter of type label should match a identifier argument. Such a identifier must be the name of a label in the multi-file.

### Text Label

A parameter of type text label should match an identifier argument.

If the parameter only accepts variables, the identifier should match a variable reference. Otherwise, if the head of the identifier is a `$` character, the tail of the identifier should match a variable reference.

TODO

### String

A parameter of type string should match a string literal argument.

TODO

TODO arg count

TODO reminder text string => label, string identifier, string constant, variable reference


Command Selectors
------------------------

A command selector (or alternator) is a kind of command which gets rewriten by the translator to another command based on the supplied argument types.

A command selector consists of its name and a set of commands which are alternatives for replacement.

Once a command name is identified as a selector, the argument list is tested over each command in the set of alternatives. The translation then behaves as if the command name was rewriten as the matching command name.

The behaviour is unspecified if more than one command in the set produces a match.

A list of selectors and theirs selection sets can be found in the appendix (TODO).

**Example** 

As an example, consider the command selector `SET` used in the following contexts:

| Selector Used As              | Rewriten As                                        |
| ----------------------------- | -------------------------------------------------- |
| `SET lvar_int 10`             | `SET_LVAR_INT lvar_int 10`                         |
| `SET lvar_flt var_flt`        | `SET_LVAR_FLOAT_TO_VAR_FLOAT lvar_flt var_flt`     |
| `SET var_int STRING_CONSTANT` | `SET_VAR_INT_TO_CONSTANT var_int STRING_CONSTANT`  |

For the first example, each command in the collection of alternatives for `SET` was evaluated with the arguments `lvar_int 10`. One must have produced a successful match, and that one was choosen as the replacement command.

The same happens for the other examples in the table.

Expressions
-------------------------

A expression is a shortcut to one or more command selectors.

The arguments of an expression may not allow string literals.

Any variable, constant or identifier which contains any of `asop`, `relop`, `binop` or `unop` in its name cannot be used in a expression. Integers with a minus anywhere but in the beggining of its token cannot be used as well.

The name of commands used to require script files (see Require Statements) cannot be on the left hand side of a expression.

### Assignment Expressions

```
binop := '+' | '-' | '*' | '/' | '+@' | '-@' ;
asop := '=' | '=#' | '+=' | '-=' | '*=' | '/=' | '+=@' | '-=@' ;
unop := '--' | '++' ;

expr_assign_abs := argument {whitespace} '=' {whitespace} 'ABS' {whitespace} argument ;
expr_assign_binary := argument {whitespace} asop {whitespace} argument ;
expr_assign_ternary := argument {whitespace} '=' {whitespace} argument {whitespace} binop argument ;
expr_assign_unary := (unop {whitespace} argument) 
                   | (argument {whitespace} unop) ;

assignment_expression := expr_assign_unary
                       | expr_assign_binary
                       | expr_assign_ternary
                       | expr_assign_abs ;
```

The unary assignments `++a` and `a++` should behave as if `ADD_THING_TO_THING a 1` was executed.

The unary assignments `--a` and `a--` should behave as if `SUB_THING_FROM_THING a 1` was executed.

The binary assignment expressions should behave as if the following was executed:

| Operation | Command Selector                               |
| --------- | ---------------------------------------------- |
| `a = b`   | `SET a b`                                      |
| `a =# b`  | `CSET a b`                                     |
| `a += b`  | `ADD_THING_TO_THING a b`                       |
| `a -= b`  | `SUB_THING_FROM_THING a b`                     |
| `a *= b`  | `MULT_THING_BY_THING a b`                      |
| `a /= b`  | `DIV_THING_BY_THING a b`                       |
| `a +=@ b` | `ADD_THING_TO_THING_TIMED a b`                 |
| `a -=@ b` | `SUB_THING_FROM_THING_TIMED a b`               |

The absolute assignment `a = ABS b` should behave as if the following was executed:

 + `ABS a` if the name `a` is the same as the name `b`.
 + `SET a b` followed by `ABS a` otherwise.

The ternary assignment `a = b + c` should behave as if the following was executed:
 
 + `ADD_THING_TO_THING a c` if the name `a` is the same as the name `b`.
 + `ADD_THING_TO_THING a b` if the name `a` is the same as the name `c`.
 + `SET a b` followed by `ADD_THING_TO_THING a c` otherwise.

The ternary assignment `a = b - c` should behave as if the following was executed:

 + `SUB_THING_FROM_THING a c` if the name `a` is the same as the name `b`.
 + Implementation-defined if `a` is the same name as `c`.
 + `SET a b` followed by `SUB_THING_BY_THING a c` otherwise.

The ternary assignment `a = b * c` should behave as if `a = b + c`, except by using `MULT_THING_BY_THING` instead of `ADD_THING_TO_THING`.

The ternary assignment `a = b / c` should behave as if `a = b - c`, except by using `DIV_THING_BY_THING` instead of `SUB_THING_FROM_THING`.

The ternary assignments `a = b +@ c` and `a = b -@ c` should behave as if `a = b - c`, except by using `ADD_THING_TO_THING_TIMED` and `SUB_THING_FROM_THING_TIMED`, respectively, instead of `SUB_THING_FROM_THING`.

The left hand side of every assignment expression must be an identifier, except for absolute assignments, ternary assignments, and the binary assignments `a = b` and `a =# b`.

### Conditional Expressions

```
relop := '=' | '<' | '>' | '>=' | '<=' ;
conditional_expression := argument {whitespace} relop {whitespace} argument ;
```

These expressions should behave as if the following was executed:

| Operation | Command Selector                               |
| --------- | ---------------------------------------------- |
| `a = b`   | `IS_THING_EQUAL_TO_THING a b`                  |
| `a > b`   | `IS_THING_GREATER_THAN_THING a b`              |
| `a >= b`  | `IS_THING_GREATER_OR_EQUAL_TO_THING a b`       |
| `a < b`   | `IS_THING_GREATER_THAN_THING b a`              |
| `a <= b`  | `IS_THING_GREATER_OR_EQUAL_TO_THING b a`       |

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

The name of a label may be empty. The name of a label may contain characters that do not match the `identifier` production. In such cases, the label cannot be used as arguments to commands.

### Empty Statements

```
empty_statement := eol ;
```

**Semantics**

An empty statement does nothing.

### Embedded Statements

Embedded statements are statements not prefixed by a label.

```
embedded_statement := empty_statement
                     | command_statement
                     | expression_statement
                     | scope_statement
                     | var_statement
                     | if_statement
                     | ifnot_statement
                     | if_goto_statement
                     | ifnot_goto_statement
                     | while_statement
                     | whilenot_statement
                     | repeat_statement
                     | require_statement ;
```

### Command Statements

```
command_statement := command eol ;
```

**Constraints**

The command it enbodies cannot be any of the commands specified by this section (e.g. `VAR_INT`, `IF`, `ENDWHILE`, `{`, `GOSUB_FILE`, etc).

### Expression Statements

```
expression_statement := assignment_expression eol
                      | conditional_expression eol ;
```

**Semantics**

The execution of the assignment expression `a = b` is favored over the the execution of the conditional expression of the same form.

### Scope Statements

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

The active scope is finished when control-flow of a script is transferred to outside the active lexical scope by a jump.

The transfer of control to the middle of a inactive lexical scope activates it.

Transfer of control to a subroutine shall not deactivate the active scope. The behaviour of the script is unspecified if such a subroutine activates another lexical scope.

### Variable Statements

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

A variable shall not have the same name as a string constant.

**Semantics**

This command declares one or more names with the specified storage duration, data type, and array dimensions.

Global variable names can be seen by the entire multi-file.

Local variable names can be seen by their entire lexical scope.

The initial value of variables is unspecified.

### Conditional Statements

Conditional statements produce changes in the script compare flag.

```
conditional_element := ['NOT' sep] (command | conditional_expression) ;

and_conditional_stmt := 'AND' sep conditional_element eol ;
or_conditional_stmt := 'OR' sep conditional_element eol ;

conditional_list := conditional_element eol
                    ({and_conditional_stmt} | {or_conditional_stmt}) ;
```

**Semantics**

The execution of a conditional element takes place by executing the command or expression it embodies.

The execution of a command should follows the same semantic rules of a command statement.

The compare flag of the executed element is negated if the statement is prefixed with a `NOT`.

A conditional list is a sequence of one or more conditional elements separated by either `AND` or `OR` tokens.

A conditional list shall not be short-circuit evaluated. All conditional elements are executed in order.

The compare flag is set to true if the compare flag of all conditional elements in a `AND` list holds true. Otherwise it is set to false.

The compare flag is set to true if the compare flag of at least one conditional elements in a `OR` list holds true. Otherwise it is set to false.

### Selection Statements

Selection statements selects which statements to execute depending on certain conditions.

#### IF Statement

```
if_statement := 'IF' sep conditional_list
                {statement}
                ['ELSE'
                {statement}]
                'ENDIF' ;
```

**Semantics**

This statement executes a list of conditions, grabs its compare flag and chooses between two set of statements to execute.

If the compare flag is true, control is transfered to the first set of statements. Otherwise, to the second set if an `ELSE` exists. After the set of statements are executed, control is transfered to the end of the IF block, unless execution of the statements resulted in a jump out of it.

#### IFNOT Statement

```
ifnot_statement := 'IFNOT' sep conditional_list
                   {statement}
                   ['ELSE'
                   {statement}]
                   'ENDIF' ;
```

**Semantics**

The behaviour of this is the same as of the IF statement, except the complement of the compare flag is used to test which set of statements to execute.

#### IF GOTO Statement

```
if_goto_statement := 'IF' sep conditional_element sep 'GOTO' identifier eol ;
```

**Semantics**

This statement performs a jump to the label specified by identifier if the compare flag of the conditional element holds true. Otherwise, the flow of control is unchanged.

#### IFNOT GOTO Statement

```
ifnot_goto_statement := 'IFNOT' sep conditional_element sep 'GOTO' identifier eol ;
```

**Semantics**

The behaviour of this is the same as of the IF GOTO statement, except the complement of the compare flag is used to test whether to jump.

### Iteration Statements

#### WHILE Statement

```
while_statement := 'WHILE' sep conditional_list
                   {statement}
                   'ENDWHILE' eol ;
```

**Semantics**

The WHILE statement executes a set of statements while the compare flag of the conditional list holds true.

The statement executes by grabbing the compare flag of the list of conditions and transfers control to after the WHILE block if it holds false. Otherwise, it executes the given set of statements. After the set of statements are executed, control is transfered to beggining of the block, unless execution of the statements resulted in a jump out of it.

#### WHILENOT Statement

```
command_whilenot := 'WHILENOT' sep conditional_list ;

whilenot_statement := command_whilenot
                      {statement}
                      command_endwhile ;
```

**Semantics**

The behaviour of this is the same as of the WHILE statement, except the complement of the compare flag is used to test whether to continue executing the set of statements.

#### REPEAT Statement

```
repeat_statement := 'REPEAT' sep integer sep variable eol
                    {statement}
                    'ENDREPEAT' eol ;
```

**Constraints**

The first argument to `REPEAT` must be a integer literal.

The second argument must be a variable of integer type.

**Semantics**

The REPEAT statement executes a set of statements until a counter variable reaches a threshold.

The counter variable is set to zero and the statements are executed. After the statements are executed, and none of them resulted in a jump out of the block, the variable is incremented and if it compares less than the threshold, control is transfered back to the set of statements.

The statements are always executed at least once.

### Require Statements

```
filename := {graph_char} '.SC' ;

require_statement := command_gosub_file
                   | command_launch_mission
                   | command_load_and_launch_mission ;
```

Require statements request script files to become part of the multi-file being translated.

**Constraints** 

Require statements shall only appear as part of the content of the *main script file* and of *main extension files*.

#### GOSUB_FILE Statement

```
command_gosub_file := 'GOSUB_FILE' sep label sep filename eol ;
```

**Semantics**

The `GOSUB_FILE` command requires a *main extension file* to become part of the multi-file.

It also calls the subroutine specified by label.

The behaviour is unspecified if the label is not part of the required file.

#### LAUNCH_MISSION Statement

```
command_launch_mission := 'LAUNCH_MISSION' sep filename eol ;
```

**Semantics**

The `LAUNCH_MISSION` command requires a *subscript file* to become part of the multi-file. 

It also starts a new script with the program counter at the `MISSION_START` directive of the specified script file.

#### LOAD_AND_LAUNCH_MISSION Statement

```
command_load_and_launch_mission := 'LOAD_AND_LAUNCH_MISSION' sep filename eol ;
```

**Constraints**

Only a single *mission script* may be runinng at once.

**Semantics**

The `LOAD_AND_LAUNCH_MISSION` command requires a *mission script file* to become part of the multi-file. 

It also starts a new *mission script* with the program counter at the `MISSION_START` directive of the specified script file.


Script File Structure
----------------------------

### Main Script Files

```
main_script_goal := {statement} ;
```

A main script file contains a sequence of zero or more statements.

**Semantics**

The main script starts execution at the first statement of the main script file. If there is no statement to be executed, behaviour is unspecified.

### Main Extension Files

```
main_extension_goal := {statement} ;
```

A main extension file contains a sequence of zero or more statements.

**Semantics**

There is no startup semantics for main extension files. They are not entry point for scripts.

### Subscript Files

```
mission_start_directive := 'MISSION_START' [sep {whitespace | graph_char | string_literal}] eol
mission_end_directive := 'MISSION_END' [sep {whitespace | graph_char | string_literal}] eol

subscript_goal := mission_start_directive
                  {statement}
                  [label_name ':' sep] mission_end_directive
                  {statement} ;
```

A subscript file contains a sequence of zero or more statements in between a `MISSION_START` and a `MISSION_END` directive. More statements may follow.

The directives may contain arbitrary characters at their tail. Those should be ignored. Appearance of quotation marks should form pairs.

**Constraints**

The `MISSION_START` directive shall be in the very first line of the subscript file and may not be preceded by anything but ASCII spaces (` `) and horizontal tabs (`\t`). Even comments are disallowed.

The `MISSION_END` directive does not have the same restriction.

**Semantics**

The entry point of the subscript specified by this script file is at the `MISSION_START` directive.

The `MISSION_END` directive should have the same behaviour as of the `TERMINATE_THIS_SCRIPT` command.

### Mission Script Files

```
mission_goal := subscript_goal ;
```

A mission script file has the same structure as of a subscript file.


Supporting Commands
-----------------------

In order to perform useful computations the following supporting commands are defined.

A implementation is not required (although recommended) to provide support to any of these commands.

### WAIT

TODO

### GOTO

TODO

### GOSUB

TODO

### GOSUB_FILE

TODO (hmm already defined)

### RETURN

TODO

### START_NEW_SCRIPT

TODO

### LAUNCH_MISSION

TODO (hmm already defined)

### LOAD_AND_LAUNCH_MISSION

TODO (hmm already defined)

### TERMINATE_THIS_SCRIPT

TODO

### SCRIPT_NAME

TODO


Supporting Command Selectors
-------------------------------

### SET

TODO

### ADD_THING_TO_THING

TODO

### SUB_THING_FROM_THING

TODO

### MULT_THING_BY_THING

TODO

### DIV_THING_BY_THING

TODO

### IS_THING_GREATER_THAN_THING

TODO

### IS_THING_GREATER_OR_EQUAL_TO_THING

TODO

### IS_THING_EQUAL_TO_THING

TODO

### IS_THING_NOT_EQUAL_TO_THING

TODO

### ADD_THING_TO_THING_TIMED

TODO

### SUB_THING_FROM_THING_TIMED

TODO

### CSET

TODO

### ABS

TODO


Remarks
------------

 + The lexical grammar is not regular because of the nestable *multi-line comments*.
 + The lexical grammar is not context-free either. Contextual information is needed in order to match each lexical category.
 + THIS IS A BROKEN LANGUAGE :)
 + NO SHORTCIRCUIT IN CONDITIONAL LIST
 + miss2 allows other chars other than the ones specified in source representation thus why we specify it (it is buggy)
 + control chars behave in a weird way in miss2 (including CR)
 + in miss2, string literals are limited and also broken (quite a hack indeed). we do not follow its broken behaviours. Like: only one string per command; the end of a string ends the line (basically);

miss2 cannot be the reference implementation because of bugs such as

```
IF {
ENDIF
```

interesting stuff

```
--b // '--' variable(b)
--b b // command(--b) variable(b)
// happens with other expressions as well
```

more interesting stuff

```
VAR_INT = 4 // works
LOAD_AND_LAUNCH_MISSION = 4 // does not work
```

mm

```
SET_CAR_COLOUR 0 ON 0 // global string constant ON does not work
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
TODO shall should must cannot could etc
TODO casing of filenames should not matter
TODO better name for what we are calling require statements
TODO interesting NOP is not compiled
TODO rockstar does not know if it calls arg 17 a text string or a string identifier. I will go for identifier.
TODO note var_text_label (and such) parameter type matches without dollar
TODO x = ABS y (which game introduced this even? see code patterns)
TODO IF/IFNOT GOTO
TODO WHILENOT is not implemented properly in miss2 (only has =)
TODO lhs of assignment-like and binary expr must be identifier, except in '=' due to a bug and ambiguity with equality
TODO disallow binary ops in IF/AND/OR (spreading over more than one line)
TODO miss2 docs from gta2script has lots of insights, read and re-read it once in a while
TODO ugh maybe GOTO is a reserved word becaues of IF...GOTO

RATIONALE for global having unspecified initial value: Stories variable sharing (must read more though).

[string literals]:
[scope]:


[Wesser]: https://web.archive.org/web/20170111193059/http://www.gtamodding.com/wiki/GTA3script
[Wesser2]: http://pastebin.com/raw/YfLWLXJw

[miss2.exe]: https://www.dropbox.com/s/7xgvqo8b9u1qw02/gta3sc_v413.rar
[miss2_strings]: http://pastebin.com/raw/Pjb0Ezkx
[gtasa_listing]: https://pastebin.com/2VczpwK7

[gta2script.7z]: gtamp.com/GTA2/gta2script.7z
