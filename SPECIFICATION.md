**Note:** This is a draft. It may be wrong, incomplete and subject to change.

Introduction
---------------------

This is an attempt to produce a formal language specification for the GTA3script language. 

GTA3script is an imperative, strong and statically typed scripting language built by DMA Design (now Rockstar North) to design the mission scripts in Grand Theft Auto.

The DMA Design compiler is very basic and contains a huge amount of bugs. These bugs introduce a lot of inconsistencies and quirks to the language. This document attempts to resolve these issues and set a coherent language.

The language specified by this document is thus a subset of the language accepted by the in-house compiler. Any source code translated by an implementation of this should be able to be translated by the original compiler. The reverse is not true. A non-exhaustive list of differences is presented on the appendix.

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

A **program** is a collection of scripts running concurrently.

A **variable** is a named storage location. This location holds a value of specific type.

There are global and local variables. **Global variables** are stored in a way they are accessible from any script. **Local variables** are said to pertain to the particular script and only accessible from it.

The lifetime of a *global variable* is the same as of the execution of all scripts. The lifetime of a *local variable* is the same as its script and lexical scope.

A **command** is an operation to be performed by a script. Commands may produce several **side-effects** which are described by each command description.

A possible side-effect of executing a command is the updating of the *compare flag*. The **compare flag** of a command is the boolean result it produces. The **compare flag of a script** is the *compare flag* of the its last executed command. The *compare flag* is useful for conditionally changing the *flow of control*.

The **program counter** of a script indicates its currently executing command. Unless one of the *side-effects* of a command is to change the *program counter*, the counter goes from the current command to the next sequentially. An explicit change in the *program counter* is said to be a change in the *flow of control*.

A command is said to perform a **jump** if it changes the *flow of control* irreversibly.

A command is said to call a **subroutine** if it changes the *flow of control* but saves the current *program counter* in a stack to be restored later.

A command is said to **terminate** a script if it halts and reclaims storage of such a script.

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

A token character is any character capable of forming a single token.

```
token_char := ascii_printable - (whitespace | '"' | '+' | '-' | '*' | '/' | '=' | '<' | '>') ;
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
 + A single, nested, *block comment* should be interpreted as an `eol` on each line boundary it crosses. On its last line (i.e. the one it does not cross), it should be interpreted as one or more whitespace characters.

Comments cannot start inside string literals.

### Commands

A command describes an operation a script should perform.

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
digit := '0'..'9';
integer := ['-'] digit {digit} ;
```

A integer literal is a sequence of digits optionally preceded by a minus sign.

If the literal begins with a minus, the number following it should be negated.

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
identifier := ('$' | 'A'..'Z') {token_char} ;
```

**Constraints**

An identifier should not end with a `:` character.

**Semantics**

The type of a variable is TODO.

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

**Variable Reference (TODO where to put this)**

The name of a variable is a sequence of token characters, except the characters `[` and `]` cannot happen.

```
variable_char := token_char - ('[' | ']') ;
variable_name := ('$' | 'A'..'Z') {variable_char} ;
```

A reference to a variable is a variable name optionally followed by an array subscript. Any character following the subscript should be ignored. A subscript shall not happen more than once.

```
subscript := '[' (variable_name | integer_literal) ']' ;
variable := variable_name [ subscript {variable_char} ] ;
```

The subscript may use a integer literal or another variable name of integer type.

The type of a variable reference is the inner type of the variable name being referenced.

Command Selectors
------------------------

TODO this is confusing, rewrite once the argument matching section is done.

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

An expression is a shortcut to one or more command selectors.

The arguments of an expression may not allow string literals.

The name of commands used to require script files (see Require Statements) cannot be on the left hand side of a expression.

### Assignment Expressions

```
binop := '+' | '-' | '*' | '/' | '+@' | '-@' ;
asop := '=' | '=#' | '+=' | '-=' | '*=' | '/=' | '+=@' | '-=@' ;
unop := '--' | '++' ;

expr_assign_abs := identifier {whitespace} '=' {whitespace} 'ABS' {whitespace} argument ;
expr_assign_binary := identifier {whitespace} asop {whitespace} argument ;
expr_assign_ternary := identifier {whitespace} '=' {whitespace} argument {whitespace} binop argument ;
expr_assign_unary := (unop {whitespace} identifier) 
                   | (identifier {whitespace} unop) ;

assignment_expression := expr_assign_unary
                       | expr_assign_binary
                       | expr_assign_ternary
                       | expr_assign_abs ;
```

The unary assignments `++a` and `a++` should behave as if `ADD_THING_TO_THING a 1` was executed.

The unary assignments `--a` and `a--` should behave as if `SUB_THING_FROM_THING a 1` was executed.

The binary assignment expressions should behave as if the following was executed:

| Expression | Behaves As If                                  |
| ---------- | ---------------------------------------------- |
| `a = b`    | `SET a b`                                      |
| `a =# b`   | `CSET a b`                                     |
| `a += b`   | `ADD_THING_TO_THING a b`                       |
| `a -= b`   | `SUB_THING_FROM_THING a b`                     |
| `a *= b`   | `MULT_THING_BY_THING a b`                      |
| `a /= b`   | `DIV_THING_BY_THING a b`                       |
| `a +=@ b`  | `ADD_THING_TO_THING_TIMED a b`                 |
| `a -=@ b`  | `SUB_THING_FROM_THING_TIMED a b`               |

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

### Conditional Expressions

```
relop := '=' | '<' | '>' | '>=' | '<=' ;
conditional_expression := argument {whitespace} relop {whitespace} argument ;
```

These expressions should behave as if the following was executed:

| Expression | Behaves As If                                  |
| ---------- | ---------------------------------------------- |
| `a = b`    | `IS_THING_EQUAL_TO_THING a b`                  |
| `a > b`    | `IS_THING_GREATER_THAN_THING a b`              |
| `a >= b`   | `IS_THING_GREATER_OR_EQUAL_TO_THING a b`       |
| `a < b`    | `IS_THING_GREATER_THAN_THING b a`              |
| `a <= b`   | `IS_THING_GREATER_OR_EQUAL_TO_THING b a`       |

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
label_def := identifier ':' ;
labeled_statement := label_def (sep embedded_statement | empty_statement) ;
```

**Constraints**

The name of a label must be unique across the multi-file.

**Semantics**

This declares a label named after the given identifier.

The label may be referenced in certain commands to transfer (or start) control of execution to the statement it prefixes. Labels themselves do not alter the flow of control, which continues to the statement it embodies.

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

The command it embodies cannot be any of the commands specified by this section (e.g. `VAR_INT`, `IF`, `ENDWHILE`, `{`, `GOSUB_FILE`, `MISSION_START`, etc).

### Expression Statements

```
expression_statement := assignment_expression eol
                      | conditional_expression eol ;
```

**Semantics**

An expression statement executes the expression it embodies.

The execution of the assignment expression `a = b` is favored over the the execution of the conditional expression of the same form.

### Scope Statements

```
scope_statement := '{' eol
                   {statement}
                   '}' eol ;
```

**Constraints**

Lexical scopes cannot be nested.

**Semantics**

The command `{` activates a lexical scope where local variables can be declared.

The command `}` leaves the active lexical scope.

The transfer of control to any of the statements within the scope block activates it.

The execution of a jump to outside the scope block leaves the lexical scope.

Performing a subroutine call shall not leave the active scope. The name of local variables become hidden if the subroutine is not within the scope block. The behaviour of the program is unspecified if such a subroutine activates another lexical scope.

Leaving a lexical scope causes the storage for the declared local variables to be reclaimed.

### Variable Statements

```
command_var_name := 'VAR_INT' 
                    | 'LVAR_INT'
                    | 'VAR_FLOAT'
                    | 'LVAR_FLOAT' ;
command_var_param := sep identifier ;

var_statement := command_var_name command_var_param {command_var_param} eol ;
```

The name of the command is a pair of storage duration and variable type.

The commands with the `VAR_` prefix declares global variables. The ones with `LVAR_` declares local variables. The `INT` suffix declares variables capable of storing integers. The `FLOAT` suffix declares floating-point ones.

**Constraints**

Global variable names must be unique across the multi-file.

Local variables may have identical names as long as they are in different lexical scopes.

Local variables shall not have the same name as any global variable.

A variable shall not have the same name as a string constant.

**Semantics**

This command declares one or more names with the specified storage duration, type, and array dimensions.

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

A conditional element executes the command or expression it embodies. The execution of a command follows the same semantic rules of a command statement. The compare flag of the executed element is negated if the `NOT` prefix is used.

A conditional list is a sequence of one or more conditional elements separated by either `AND` or `OR` tokens.

The compare flag is set to true if the compare flag of all conditional elements in a `AND` list holds true. Otherwise it is set to false.

The compare flag is set to true if the compare flag of at least one conditional elements in a `OR` list holds true. Otherwise it is set to false.

A conditional list shall not be short-circuit evaluated. All conditional elements are executed in order.

### Selection Statements

Selection statements selects which statement to execute depending on certain conditions.

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

If the compare flag is true, control is transfered to the first set of statements. Otherwise, to the second set if an `ELSE` exists. After the set of statements are executed, control is transfered to the end of the IF block, unless execution of the statements resulted in a jump out of the block.

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

The statement executes by grabbing the compare flag of the list of conditions and transfering control to after the WHILE block if it holds false. Otherwise, it executes the given set of statements. After the set of statements are executed, control is transfered again to beggining of the block, unless execution of the statements resulted in a jump out of the block.

#### WHILENOT Statement

```
whilenot_statement := 'WHILENOT' sep conditional_list
                      {statement}
                      'ENDWHILE' eol ;
```

**Semantics**

The behaviour of this is the same as of the WHILE statement, except the complement of the compare flag is used to test whether to continue executing the set of statements.

#### REPEAT Statement

```
repeat_statement := 'REPEAT' sep integer sep identifier eol
                    {statement}
                    'ENDREPEAT' eol ;
```

**Constraints**

The first argument to REPEAT must be an integer literal.

The second argument must be a variable of integer type.

**Semantics**

The REPEAT statement executes a set of statements until a counter variable reaches a threshold.

The counter variable is set to zero and the statements are executed. After the statements are executed, and none of them resulted in a jump out of the block, the variable is incremented and if it compares less than the threshold, control is transfered back to the set of statements. Otherwise, it leaves the block.

The statements are always executed at least once.

### Require Statements

```
filename := {token_char} '.SC' ;

require_statement := command_gosub_file
                   | command_launch_mission
                   | command_load_and_launch_mission ;
```

Require statements request script files to become part of the multi-file being translated.

**Constraints** 

Require statements shall only appear in the *main script file* or *main extension files*.

#### GOSUB_FILE Statement

```
command_gosub_file := 'GOSUB_FILE' sep identifier sep filename eol ;
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

It also starts a new subscript with the program counter at the `MISSION_START` directive of the specified script file.

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
main_script_file := {statement} ;
```

A main script file is a sequence of zero or more statements.

**Semantics**

The main script starts execution at the first statement of the main script file. If there is no statement to be executed, behaviour is unspecified.

### Main Extension Files

```
main_extension_file := {statement} ;
```

A main extension file is a sequence of zero or more statements.

### Subscript Files

```
subscript_file := 'MISSION_START' eol
                  {statement}
                  [label_def sep] 'MISSION_END' eol
                  {statement} ;
```

A subscript file is a sequence of zero or more statements in a `MISSION_START` and `MISSION_END` block. More statements may follow.

**Constraints**

The `MISSION_START` command shall be the very first line of the subscript file and shall not be preceded by anything but ASCII spaces (` `) and horizontal tabs (`\t`). Even comments are disallowed.

**Semantics**

The `MISSION_END` command should behaviour as if by executing the `TERMINATE_THIS_SCRIPT` command.

### Mission Script Files

```
mission_script_file := subscript_file ;
```

A mission script file has the same structure of a subscript file.


Supporting Commands
-----------------------

In order to perform useful computations the following supporting commands are defined.

An implementation is not required to provide support to any of these commands.

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

### RETURN_TRUE

TODO

### RETURN_FALSE

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


Appendix
------------

### Notes

 + The lexical grammar is not regular because of the nestable *multi-line comments*.
 + The lexical grammar is not context-free either. Contextual information is needed in order to match each lexical category (TODO check this again after the change to a subset of miss2)
 + Examples of dependence on context for lexing:
    - `LABEL: COMMAND:` is `label(LABEL:) command(COMMAND:)`.
    - `X = Y` is `command(X) '=' identifier(Y)` whereas `X Y` is `command(X) identifier(Y)`.
    - `X --` is `identifier(X) '--'` whereas `X -1` is `command(X) integer(-1)`.
    - `NAME NAME` is `command(NAME) identifier(NAME)`,
    - `AND x` is `command(AND) identifier(x)` outside of an IF. Same for `NOT` and `OR`.
    - `AND AND x` is `'AND' command(AND) identifier(x)` if within an IF.
    - `1234 1234` is `command(1234) integer(1234)`.

### Regular Lexical Grammar

A regular lexical grammar can be defined as follow:

```
# A Simple Lexical Grammar
sep := sep ;
eol := eol ;
token := token_char {token_char} ;
string_literal := string_literal ;
plus := '+' ;
minus := '-' ;
star := '*' ;
slash := '/' ;
plus_at := '+@' ;
minus_at := '-@' ;
equal := '=' ;
equal_hash := '=#' ;
plus_equal := '+=' ;
minus_equal := '-=' ;
star_equal := '*=' ; 
slash_equal := '/=' ;
plus_equal_at := '+=@' ;
minus_equal_at := '-=@' ;
minus_minus := '--' ;
plus_plus := '++' ;
```

There are only operators, separators, unclassified tokens, and string literals. Further information about each unclassified token may be discovered by the parser.

### How to MISS2

The leaked script compiler is full of bugs. It was written for in-house use, so it's meant to work and recognize at least the intended language. The problem is, the language is too inconsistent in this buggy superset. After constantly trying to make those bugs part of this specification, I strongly believe we shouldn't. For the conservative, the following is a list of known things miss2 accepts that this specification does not.

**Unrestricted character set**

More control codes than the specified are *accepted* by miss2 (such as `\r` anywhere or `\v`). The compiler behaves in weird ways when those are used.

You may use custom characters (c > 127), but you may clash with the characters DMA used to tokenize string literals.

**A string literal is the same as four tokens**

```
SAVE_STRING_TO_DEBUG_FILE "OO AR AZ WERTY"
SAVE_STRING_TO_DEBUG_FILE FOO BAR BAZ QWERTY
// both are recognized by miss2 and produce the same bytecode
// this specification only accepts the string literal one
``` 

**A string literal ends a line**

As part of transforming a string literal into tokens, miss2 puts a null terminator in the line. Thus, any argument following it is kinda of ignored.

```
SAVE_STRING_TO_DEBUG_FILE "this is a string" and this is ignored
// this specification does not accept this
```

**Accepts internal compiler commands**

Remove the constraint that commands that conflict with grammar definitions cannot be used in a `command_statement` and you get atrocities like:

```
IF { // does not begin a lexical scope
ENDIF

IF WHILE 0 // it's like an ANDOR within an ANDOR
ENDIF

// there is probably a lot more of these
```

**WHILENOT is incomplete**

WHILENOT only accepts equality comparision

```
WHILENOT x = 1
ENDWHILE

WHILENOT x < 1 // not recognized
ENDWHILE

// since we accept the above, we are not a subset anymore.
// to fix this (and become a subset again) only allow equality
// on WHILENOT.
```

**AND/OR behaves differently than IF/WHILE/expressions**

```
WHILENOT x < 1 // not recognized
AND x < 1      // recognized
ENDWHILE
// this specification accepts both

WHILE WAIT 1-1 // not recognized
AND WAIT 1-1   // recognized
// this specification accepts neither

WHILE WAIT-1   // the command WAIT with a -1 argument
AND WAIT-1     // a command named WAIT-1
// this specification accepts neither
```

**INT tokens allow minus in the middle**

```
WAIT 1-1
WAIT 1-
// this specification does not accept this
```

**Commands may have operator characters**

```
--b   // recognized as '--' identifier(b)
--b b // recognized as command(--b) identifier(b)
// this makes the lexer context sensitive
// but this spec disallow the later form based
// on the belief the IF/WHILE/expressions parser
// is the correct one (details above).
```

**anything may follow MISSION_START**

```
MISSION_START anythin"may follow" this thing
MISSION_END the same "happens"with mission_end
// this specification does not accept this
```

**labels may contain any printable character (except quotation marks)**

```
e-=1:                  // recognized (we don't accept this)
GOTO e-=1              // not recognized
LAUNCH_MISSION e/=.sc  // recognized (we don't accept this)
```

**label may be empty or not match identifier**

The name of a label may be empty. The name of a label may contain characters that do not match the `identifier` production.

```
:     // recognized
::::  // recognized
@abc: // recognized
// this specification does not accept this
```

**non-identifiers on the lhs of assignment expressions**

Some expressions implement this correctly in miss2, some don't.

```
1 = ABS 2 // recognized
--1       // recognized for every unary expression
1 = 2 * 3 // recognized for every ternary expression
1 = 2     // recognized
1 =# 2    // recognized
1 *= 2    // not recognized for every other binary expression
// this specification does not accept any of this
```

**STILL NEED TO THINK ABOUT**

more interesting stuff

```
VAR_INT = 4 // works
LOAD_AND_LAUNCH_MISSION = 4 // does not work
```

mm

```
SET_CAR_COLOUR 0 ON 0 // global string constant ON does not work
```


TODO shall should must cannot could may etc
TODO SAN ANDREAS ALLOWS IDENTIFIERS TO BEGIN WITH UNDERSCORES 
TODO scripts subscripts mission script and such (what are the execution differences)
TODO translation limits
TODO what about commands that do not produce compare flag changes but may appear in a conditional statement
TODO timera timerb
TODO better name for what we are calling require statements
TODO interesting NOP is not compiled
TODO rockstar does not know if it calls arg 17 a text string or a string identifier. I will go for identifier.
TODO note var_text_label (and such) parameter type matches without dollar
TODO uhh GOTO may clash with argument when used  in IF...GOTO
TODO specify array access pattern (is first index 0? is a[0] valid for non-array? for sure a[2] does not if out-of-bounds)
TODO is MISSION_START/END a command?
TODO SAVE_VAR_INT
TODO should we fix the floating point literals (e.g. '1.9.2')? I think there are DMA scripts that need this.
TODO maybe move the semantic definition that we cannot use mission script labels from outside it from concepts to the script file structure section
TODO the rationale for global having unspecified initial value: Stories variable sharing (must read more though).

[string literals]:
[scope]:


[Wesser]: https://web.archive.org/web/20170111193059/http://www.gtamodding.com/wiki/GTA3script
[Wesser2]: http://pastebin.com/raw/YfLWLXJw

[miss2.exe]: https://www.dropbox.com/s/7xgvqo8b9u1qw02/gta3sc_v413.rar
[miss2_strings]: http://pastebin.com/raw/Pjb0Ezkx
[gtasa_listing]: https://pastebin.com/2VczpwK7

[gta2script.7z]: gtamp.com/GTA2/gta2script.7z
