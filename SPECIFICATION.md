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

A **script** is a unit of execution which contains its own *program counter*, *local variables* and *compare flag*.

A **program** is a collection of scripts running concurrently in a cooperative fashion.

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

An **integer** is a binary signed two's-complement integral number. It represents 32 bits of data and the range of values *-2147483648* through *2147483647*.

A **floating-point** is a representation of a real number. Its exact representation, precision and range of values is implementation-defined.

A **label** is a name specifying the location of a command.

A **text label** is a name whose value is only known in the execution environment.

A **string** is a sequence of zero or more characters.

An **array** is a collection of one or more elements of the same type. Each element is indexed by an integer key.

Elements
---------------------

The lexical grammar of the language is context-sensitive. As such, the lexical elements and the syntactic elements will be presented together.

### Source Code

*Source code* is a stream of printable ASCII characters plus the control codes line feed (`\n`), horizontal tab (`\t`) and carriage return (`\r`).

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

A *line* is a sequence of characters delimited by a newline. The start of the stream begins a line. The end of the stream finishes a line.

```
newline := ['\r'] `\n` ;
```

Each line should be interpreted as if there was no whitespaces in either ends of the line.

A *token character* is any character capable of forming a single token.

```
graph_char := ascii_printable - (whitespace | '"') ;
token_char := graph_char - ('+' | '-' | '*' | '/' | '=' | '<' | '>') ;
```

To simplify future definitions, we define the productions `eol` as the end of a line, and `sep` as a token separator.

```
sep := whitespace {whitespace} ;
eol := newline | EOF ;
```

### Comments

*Comments* serve as program documentation.

```
comment := line_comment | block_comment ;
line_comment := '//' {ascii_char} eol ;
block_comment := '/*' {block_comment | ascii_char} '*/' ;
```

There are two forms:

 + *Line comments* starts with the character sequence `//` and stop at the end of the line.
 + *Block comments* starts with the character sequence `/*` and stop with its matching `*/`. Block comments can be nested inside each other.

The contents of comments shall be interpreted as if it were whitespaces in the source code. More specifically: 

 + A line comment should be interpreted as an `eol`.
 + A single, nested, block comment should be interpreted as an `eol` on each line boundary it crosses. On its last line (i.e. the one it does not cross), it should be interpreted as one or more whitespace characters.

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
digit := '0'..'9' ;
integer := ['-'] digit {digit} ;
```

A *integer literal* is a sequence of digits optionally preceded by a minus sign.

If the literal begins with a minus, the number following it should be negated.

### Floating-Point Literals

```
floating_form1 := '.' digit { digit | '.' | 'F' } ;
floating_form2 := digit { digit } ('.' | 'F') { digit | '.' | 'F' } ;
floating := ['-'] (floating_form1 | floating_form2) ;
```

A *floating-point literal* is a nonempty sequence of digits which must contain at least one occurrence of the characters `.` or `F`.

Once the `F` characters is found, all characters including and following it should be ignored. The same should happen when the character `.` is found a second time.

The literal may be preceded by a minus sign, which should negate the floating-point number.

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

An identifier should not end with a `:` character.

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

A *variable reference* is a variable name optionally followed by an array subscript. Any character following the subscript should be ignored. A subscript shall not happen more than once.

```
subscript := '[' (variable_name | integer) ']' ;
variable := variable_name [ subscript {variable_char} ] ;
```

The subscript may use a integer literal or another variable name of integer type. The indexing is zero-based.

The integer literal in a subscript must be positive.

The type of a variable reference is the inner type of the variable name being referenced.

Parameters
-----------------------

A command receives several arguments. Every argument must obey the rules of its corresponding *parameter definition*.

A *parameter definition* is a set of definitions regarding a single parameter for a specific command.

A command must have the same amount of arguments as its amount of parameter definitions, unless the missing arguments correspond to *optional parameters* (defined below).

### String Constants

A *string constant* is a name associated with an integer value. Such association is known in the translation environment.

An *enumeration* is a collection of string constants.

A parameter definition may have an associated enumeration. A string constant is said to be a match if an identifier in an argument refers to a name in its parameter's enumeration.

There is an special enumeration called the *global string constants enumeration* which semantics are defined along this specification. Other enumerations may be defined by an implementation.

If a parameter definition specifies an enumeration, the global string constants enumeration cannot be matched in the said parameter.

### Parameter Types

#### INT

An *INT parameter* accepts an argument only if it is an integer literal or an identifier matching a global string constant.

### FLOAT

A *FLOAT parameter* accepts an argument only if it is an floating-point literal.

#### VAR_INT

A *VAR_INT parameter* accepts an argument only if it is an identifier referencing a global variable of integer type.

#### VAR_FLOAT

A *VAR_FLOAT parameter* accepts an argument only if it is an identifier referencing a global variable of floating-point type.

#### LVAR_INT

A *LVAR_INT parameter* accepts an argument only if it is an identifier referencing a local variable of integer type.

#### LVAR_FLOAT

A *LVAR_FLOAT parameter* accepts an argument only if it is an identifier referencing a local variable of floating-point type.

#### INPUT_INT

An *INPUT_INT parameter* accepts an argument only if it is an integer literal or an identifier either matching a string constant, global string constant or referencing a variable of integer type (in this order).

#### INPUT_FLOAT

An *INPUT_FLOAT parameter* accepts an argument only if it is an floating-point literal or an identifier referencing a variable of floating-point type.

#### OUTPUT_INT

An *OUTPUT_INT parameter* accepts an argument only if it is an identifier referencing a variable of integer type.

#### OUTPUT_FLOAT

An *OUTPUT_FLOAT parameter* accepts an argument only if it is a identifier referencing a variable of floating-point type.

#### LABEL

A *LABEL parameter* accepts an argument only if it is an identifier whose name is a label in the multi-file.

#### TEXT_LABEL

An *TEXT_LABEL parameter* accepts an argument only if it is an identifier. If the identifier begins with a dollar character (`$`), its suffix must reference a variable of text label type and such a variable is the actual argument. Otherwise, the identifier is a text label.

#### VAR_TEXT_LABEL

A *VAR_TEXT_LABEL parameter* accepts an argument only if it is an identifier referencing a global variable of text label type.

#### LVAR_TEXT_LABEL

A *LVAR_TEXT_LABEL parameter* accepts an argument only if it is an identifier referencing a local variable of text label type.

#### STRING

A *STRING parameter* accepts an argument only if it is a string literal.

#### Optional Parameters

Additionally, the following parameters are defined as behaving equivalently to their correspondent parameters above, except that in case an argument is absent, parameter matching stops as if there are no more parameters.

 + *VAR_INT_OPT*
 + *VAR_FLOAT_OPT*
 + *LVAR_INT_OPT*
 + *LVAR_FLOAT_OPT*
 + *VAR_TEXT_LABEL_OPT*
 + *LVAR_TEXT_LABEL_OPT*
 + *INPUT_OPT*

Such parameters are always trailing parameters.

The *INPUT_OPT parameter* accepts an argument only if it is an integer literal, floating-point literal, or identifier referencing a variable of integer, floating-point or text label type.

Command Selectors
------------------------

A *command selector* (or *alternator*) is a kind of command which gets rewritten by the translator to another command based on the supplied argument types.

A command selector consists of a name and a finite sequence of commands which are alternatives for replacement.

A command name which is the name of a selector shall behave as if its command name was rewritten as a *matching alternative* before any parameter checking takes place.

A *matching alternative* is the first command in the alternative sequence to have the same amount of parameters as arguments in the actual command, and to obey the following rules for every argument and its corresponding parameter:

+ An integer literal argument must have a parameter of type *INT*.
+ A floating-point literal argument must have a parameter of type *FLOAT*.
+ For identifiers, the following applies (in the given order):
  1. If the identifier matches a global string constant, the parameter type must be *INT*.
  2. If the identifier references a global variable, the parameter type must be either (depending on the type of the said variable) *VAR_INT*, *VAR_FLOAT* or *VAR_TEXT_LABEL*.
  3. If the identifier references a local variable, the same rule as above applies, except by using *LVAR_INT*, *LVAR_FLOAT* and *LVAR_TEXT_LABEL*.
  4. If the identifier matches any string constant in any enumeration, the parameter type must be *INPUT_INT* and the argument shall behave as if it was rewritten as an integer literal corresponding to the string constant's value.
  5. Otherwise, the parameter type must be *TEXT_LABEL*.

If no matching alternative is found, the program is ill-formed.

Expressions
-------------------------

An expression is a shortcut to one or more command selectors.

**Constraints**

No argument in an expression can be a string literal.

The name of commands used to require script files (e.g. `GOSUB_FILE`) and its directive commands (i.e. `MISSION_START` and `MISSION_END`) cannot be on the left hand side of a expression.

### Assignment Expressions


```
binop := '+' | '-' | '*' | '/' | '+@' | '-@' ;
asop := '=' | '=#' | '+=' | '-=' | '*=' | '/=' | '+=@' | '-=@' ;
unop := '--' | '++' ;

expr_assign_abs := identifier {whitespace} '=' {whitespace} 'ABS' {whitespace} argument ;
expr_assign_binary := identifier {whitespace} asop {whitespace} argument ;
expr_assign_ternary := identifier {whitespace} '=' {whitespace} argument {whitespace} binop {whitespace} argument ;
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
label_prefix := label_def sep ;

labeled_statement := label_prefix embedded_statement 
                   | label_def empty_statement ;
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

The command it embodies cannot be any of the commands specified by this section (e.g. `VAR_INT`, `ELSE`, `ENDWHILE`, `{`, `GOSUB_FILE`, `MISSION_START`, etc).

### Expression Statements

```
expression_statement := assignment_expression eol
                      | conditional_expression eol ;
```

**Semantics**

An expression statement executes the expression it embodies.

The execution of the assignment expression `a = b` is favored over the execution of the conditional expression of the same form.

### Scope Statements

```
scope_statement := '{' eol
                   {statement}
                   [label_prefix] '}' eol ;
```

**Constraints**

Lexical scopes cannot be nested.

**Semantics**

The command `{` activates a lexical scope where local variables can be declared.

The command `}` leaves the active lexical scope.

The transfer of control to any of the statements within the scope block activates it.

The execution of a jump to outside the scope block leaves the lexical scope.

Performing a subroutine call does not leave the active scope. The name of local variables become hidden if the subroutine is not within the scope block. The behaviour of the program is unspecified if such a subroutine activates another lexical scope.

Leaving a lexical scope causes the storage for the declared local variables to be reclaimed.

### Variable Declaration Statements

```
command_var_name := 'VAR_INT' 
                    | 'LVAR_INT'
                    | 'VAR_FLOAT'
                    | 'LVAR_FLOAT' ;
                    | 'VAR_TEXT_LABEL'
                    | 'LVAR_TEXT_LABEL' ;
command_var_param := sep variable ;

var_statement := command_var_name command_var_param {command_var_param} eol ;
```

The name of the command is a pair of storage duration and variable type.

The commands with the `VAR_` prefix declares global variables. The ones with `LVAR_` declares local variables. The `INT` suffix declares variables capable of storing integers. The `FLOAT` suffix declares floating-point ones. Finally, the `TEXT_LABEL` one declares variables capable of storing text labels.

**Constraints**

Global variable names must be unique across the multi-file.

Local variables must be declared inside a lexical scope.

Local variables may have identical names as long as they are in different lexical scopes.

Local variables shall not have the same name as any global variable.

A variable shall not have the same name as any string constant in any enumeration (except for the global enumeration).

The array dimensions of the variable (if any) must be specified by an integer literal greater than zero.

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

**Constraints**

The command it embodies cannot be any of the commands specified by this section (e.g. `VAR_INT`, `ELSE`, `ENDWHILE`, `{`, `GOSUB_FILE`, `MISSION_START`, etc).

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
                [[label_prefix] 'ELSE' eol
                {statement}]
                [label_prefix] 'ENDIF' eol ;
```

**Semantics**

This statement executes a list of conditions, grabs its compare flag and chooses between two set of statements to execute.

If the compare flag is true, control is transferred to the first set of statements. Otherwise, to the second set if an `ELSE` exists. Execution of the `ELSE` or the `ENDIF` command causes control to leave the IF block.

#### IFNOT Statement

```
ifnot_statement := 'IFNOT' sep conditional_list
                   {statement}
                   [[label_prefix] 'ELSE' eol
                   {statement}]
                   [label_prefix] 'ENDIF' eol ;
```

**Semantics**

The behaviour of this is the same as of the IF statement, except the complement of the compare flag is used to test which set of statements to execute.

#### IF GOTO Statement

```
if_goto_statement := 'IF' sep conditional_element sep 'GOTO' sep identifier eol ;
```

**Semantics**

This statement performs a jump to the label specified by identifier if the compare flag of the conditional element holds true. Otherwise, the flow of control is unchanged.

#### IFNOT GOTO Statement

```
ifnot_goto_statement := 'IFNOT' sep conditional_element sep 'GOTO' sep identifier eol ;
```

**Semantics**

The behaviour of this is the same as of the IF GOTO statement, except the complement of the compare flag is used to test whether to jump.

### Iteration Statements

#### WHILE Statement

```
while_statement := 'WHILE' sep conditional_list
                   {statement}
                   [label_prefix] 'ENDWHILE' eol ;
```

**Semantics**

The WHILE statement executes a set of statements while the compare flag of the conditional list holds true.

The statement executes by grabbing the compare flag of the list of conditions and transferring control to after the WHILE block if it holds false. Otherwise, it executes the given set of statements. Execution of the `ENDWHILE` command causes control to be transferred to beginning of the block, where the conditions are evaluated again.

#### WHILENOT Statement

```
whilenot_statement := 'WHILENOT' sep conditional_list
                      {statement}
                      [label_prefix] 'ENDWHILE' eol ;
```

**Semantics**

The behaviour of this is the same as of the WHILE statement, except the complement of the compare flag is used to test whether to continue executing the set of statements.

#### REPEAT Statement

```
repeat_statement := 'REPEAT' sep integer sep identifier eol
                    {statement}
                    [label_prefix] 'ENDREPEAT' eol ;
```

**Constraints**

The first argument to REPEAT must be an integer literal.

The second argument must be a variable of integer type.

**Semantics**

The REPEAT statement executes a set of statements until a counter variable reaches a threshold.

The `REPEAT` command causes the variable to be set to zero. Execution of the `ENDREPEAT` command causes the variable to be incremented and if it compares less than the threshold, it transfers control back to the set of statements. Otherwise, it leaves the block.

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

Only a single *mission script* may be running at once.

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
                  [label_prefix] 'MISSION_END' eol
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

In order to perform useful computation the following supporting commands are defined.

An implementation is not required to provide support to any of these commands.

### WAIT

**Parameters**

```
WAIT INPUT_INT
```

**Side-effects**

Yields control to another script. The current script is not resumed for at least the specified number of milliseconds.

This command is useful due to the cooperative multitasking nature of the execution environment.

### GOTO

**Parameters**

```
GOTO LABEL
```

**Side-effects**

Performs a jump to the specified location.

### GOSUB

**Parameters**

```
GOSUB LABEL
```

**Side-effects**

Calls the subroutine in the specified location.

### RETURN

**Parameters**

```
RETURN
```

**Side-effects**

Returns from the last called subroutine.

The behaviour is undefined if there is no active subroutine.

### RETURN_TRUE

**Parameters**

```
RETURN_TRUE
```

**Side-effects**

Returns true (as in any command updating the compare flag to true).

### RETURN_FALSE

**Parameters**

```
RETURN_FALSE
```

**Side-effects**

Returns false (as in any command updating the compare flag to false).

### SCRIPT_NAME

**Parameters**

```
SCRIPT_NAME TEXT_LABEL
```

**Side-effects**

Associates a name to the executing script.

**Constraints**

The translation environment must enforce the following constraints.

The name of a script must be unique across the multi-file.

The behaviour of the translation is unspecified if the name is given by a text label variable.

### TERMINATE_THIS_SCRIPT

**Parameters**

```
TERMINATE_THIS_SCRIPT
```

**Side-effects**

Terminates the executing script.

### START_NEW_SCRIPT

**Parameters**

```
START_NEW_SCRIPT LABEL INPUT_OPT...
```

**Side-effects**

Creates a script and sets its program counter to the specified label location.

The first few local variables at the scope of the target label are set to the values of the optional input arguments. That is, the first declared local variable is set to the first optional argument. The second variable to the second optional argument, and so on.

**Constraints**

The translation environment must enforce the following constraints.

The specified label location must be within a scope.

The type of a local variable and its respective input argument must match. For instance, if an input argument is an integer literal or variable of integer type, its corresponding local variable in the target scope must be of integer type.

If there are not enough local variables in the target scope to accomodate the input arguments the program is ill-formed.

Supporting Command Selectors
-------------------------------

To further enchance the set of minimal commands for useful computation, the following command selectors and its supportive alternatives are defined.

An implementation is required to support these selectors, but not all of its alternative commands.

### SET

**Alternatives**

    SET_VAR_INT VAR_INT INT
    SET_VAR_FLOAT VAR_FLOAT INT
    SET_LVAR_INT LVAR_INT INT
    SET_LVAR_FLOAT LVAR_FLOAT FLOAT
    SET_VAR_INT_TO_VAR_INT VAR_INT TVAR_INT
    SET_LVAR_INT_TO_LVAR_INT LVAR_INT LVAR_INT
    SET_VAR_FLOAT_TO_VAR_FLOAT VAR_FLOAT VAR_FLOAT
    SET_LVAR_FLOAT_TO_LVAR_FLOAT LVAR_FLOAT LVAR_FLOAT
    SET_VAR_FLOAT_TO_LVAR_FLOAT VAR_FLOAT LVAR_FLOAT
    SET_LVAR_FLOAT_TO_VAR_FLOAT LVAR_FLOAT VAR_FLOAT
    SET_VAR_INT_TO_LVAR_INT VAR_INT LVAR_INT
    SET_LVAR_INT_TO_VAR_INT LVAR_INT VAR_INT
    SET_VAR_INT_TO_CONSTANT VAR_INT ANY_INT
    SET_LVAR_INT_TO_CONSTANT VAR_INT ANY_INT
    SET_VAR_TEXT_LABEL VAR_TEXT_LABEL TEXT_LABEL
    SET_LVAR_TEXT_LABEL LVAR_TEXT_LABEL TEXT_LABEL

**Side-effects**

Sets the variable on the left to the value on the right.

### CSET

**Alternatives**

    CSET_VAR_INT_TO_VAR_FLOAT VAR_INT VAR_FLOAT
    CSET_VAR_FLOAT_TO_VAR_INT VAR_FLOAT VAR_INT 
    CSET_LVAR_INT_TO_VAR_FLOAT LVAR_INT VAR_FLOAT 
    CSET_LVAR_FLOAT_TO_VAR_INT LVAR_FLOAT VAR_INT 
    CSET_VAR_INT_TO_LVAR_FLOAT VAR_INT LVAR_FLOAT 
    CSET_VAR_FLOAT_TO_LVAR_INT VAR_FLOAT LVAR_INT 
    CSET_LVAR_INT_TO_LVAR_FLOAT LVAR_INT LVAR_FLOAT 
    CSET_LVAR_FLOAT_TO_LVAR_INT LVAR_FLOAT LVAR_INT 

**Side-effects**

Sets the variable on the left to the value of the variable on the right converted to the left type.

### ADD_THING_TO_THING

**Alternatives**

    ADD_VAL_TO_INT_VAR VAR_INT INT
    ADD_VAL_TO_FLOAT_VAR VAR_FLOAT FLOAT
    ADD_VAL_TO_INT_LVAR LVAR_INT INT
    ADD_VAL_TO_FLOAT_LVAR LVAR_FLOAT FLOAT
    ADD_INT_VAR_TO_INT_VAR VAR_INT VAR_INT
    ADD_FLOAT_VAR_TO_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    ADD_INT_LVAR_TO_INT_LVAR LVAR_INT LVAR_INT
    ADD_FLOAT_LVAR_TO_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    ADD_INT_VAR_TO_INT_LVAR LVAR_INT VAR_INT
    ADD_FLOAT_VAR_TO_FLOAT_LVAR LVAR_FLOAT VAR_FLOAT
    ADD_INT_LVAR_TO_INT_VAR VAR_INT LVAR_INT
    ADD_FLOAT_LVAR_TO_FLOAT_VAR VAR_FLOAT LVAR_FLOAT

**Side-effects**

Adds the value on the right to the variable on the left.

### SUB_THING_FROM_THING

**Alternatives**

    SUB_VAL_FROM_INT_VAR VAR_INT INT
    SUB_VAL_FROM_FLOAT_VAR VAR_FLOAT FLOAT
    SUB_VAL_FROM_INT_LVAR LVAR_INT INT
    SUB_VAL_FROM_FLOAT_LVAR LVAR_FLOAT FLOAT
    SUB_INT_VAR_FROM_INT_VAR VAR_INT VAR_INT
    SUB_FLOAT_VAR_FROM_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    SUB_INT_LVAR_FROM_INT_LVAR LVAR_INT LVAR_INT
    SUB_FLOAT_LVAR_FROM_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    SUB_INT_VAR_FROM_INT_LVAR LVAR_INT VAR_INT
    SUB_FLOAT_VAR_FROM_FLOAT_LVAR LVAR_FLOAT VAR_FLOAT
    SUB_INT_LVAR_FROM_INT_VAR VAR_INT LVAR_INT
    SUB_FLOAT_LVAR_FROM_FLOAT_VAR VAR_FLOAT LVAR_FLOAT

**Side-effects**

Substracts the value on the right from the variable on the left.

### MULT_THING_BY_THING

**Alternatives**

    MULT_INT_VAR_BY_VAL VAR_INT INT
    MULT_FLOAT_VAR_BY_VAL VAR_FLOAT FLOAT
    MULT_INT_LVAR_BY_VAL LVAR_INT INT
    MULT_FLOAT_LVAR_BY_VAL LVAR_FLOAT FLOAT
    MULT_INT_VAR_BY_INT_VAR VAR_INT VAR_INT
    MULT_FLOAT_VAR_BY_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    MULT_INT_LVAR_BY_INT_LVAR LVAR_INT LVAR_INT
    MULT_FLOAT_LVAR_BY_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    MULT_INT_VAR_BY_INT_LVAR VAR_INT LVAR_INT
    MULT_FLOAT_VAR_BY_FLOAT_LVAR VAR_FLOAT LVAR_FLOAT
    MULT_INT_LVAR_BY_INT_VAR LVAR_INT VAR_INT
    MULT_FLOAT_LVAR_BY_FLOAT_VAR LVAR_FLOAT VAR_FLOAT

**Side-effects**

Multiplites the variable on the left by the value on the right.

### DIV_THING_BY_THING

**Alternatives**

    DIV_INT_VAR_BY_VAL VAR_INT INT
    DIV_FLOAT_VAR_BY_VAL VAR_FLOAT FLOAT
    DIV_INT_LVAR_BY_VAL LVAR_INT INT
    DIV_FLOAT_LVAR_BY_VAL LVAR_FLOAT FLOAT
    DIV_INT_VAR_BY_INT_VAR VAR_INT VAR_INT
    DIV_FLOAT_VAR_BY_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    DIV_INT_LVAR_BY_INT_LVAR LVAR_INT LVAR_INT
    DIV_FLOAT_LVAR_BY_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    DIV_INT_VAR_BY_INT_LVAR VAR_INT LVAR_INT
    DIV_FLOAT_VAR_BY_FLOAT_LVAR VAR_FLOAT LVAR_FLOAT
    DIV_INT_LVAR_BY_INT_VAR LVAR_INT VAR_INT
    DIV_FLOAT_LVAR_BY_FLOAT_VAR LVAR_FLOAT VAR_FLOAT

**Side-effects**

Divides the variable on the left by the value on the right.

### ABS

**Alternatives**

    ABS_VAR_INT VAR_INT
    ABS_LVAR_INT LVAR_INT
    ABS_VAR_FLOAT VAR_FLOAT
    ABS_LVAR_FLOAT LVAR_FLOAT

**Side-effects**

Computes the absolute value of a variable's value and store the result in the same variable.

### ADD_THING_TO_THING_TIMED

**Alternatives**

    ADD_TIMED_VAL_TO_FLOAT_VAR VAR_FLOAT FLOAT
    ADD_TIMED_VAL_TO_FLOAT_LVAR LVAR_FLOAT FLOAT
    ADD_TIMED_FLOAT_VAR_TO_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    ADD_TIMED_FLOAT_LVAR_TO_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    ADD_TIMED_FLOAT_LVAR_TO_FLOAT_VAR VAR_FLOAT LVAR_FLOAT
    ADD_TIMED_FLOAT_VAR_TO_FLOAT_LVAR LVAR_FLOAT VAR_FLOAT

**Side-effects**

Adds the value on the right multipled by the frame delta time to the variable on the left.

### SUB_THING_FROM_THING_TIMED

**Alternatives**

    SUB_TIMED_VAL_FROM_FLOAT_VAR VAR_FLOAT FLOAT
    SUB_TIMED_VAL_FROM_FLOAT_LVAR LVAR_FLOAT FLOAT
    SUB_TIMED_FLOAT_VAR_FROM_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    SUB_TIMED_FLOAT_LVAR_FROM_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    SUB_TIMED_FLOAT_LVAR_FROM_FLOAT_VAR VAR_FLOAT LVAR_FLOAT
    SUB_TIMED_FLOAT_VAR_FROM_FLOAT_LVAR LVAR_FLOAT VAR_FLOAT

**Side-effects**

Substracts the value on the right multipled by the frame delta time from the variable on the left.

### IS_THING_EQUAL_TO_THING

**Alternatives**

    IS_INT_VAR_EQUAL_TO_NUMBER VAR_INT INT
    IS_INT_LVAR_EQUAL_TO_NUMBER LVAR_INT INT
    IS_INT_VAR_EQUAL_TO_INT_VAR VAR_INT VAR_INT
    IS_INT_LVAR_EQUAL_TO_INT_LVAR LVAR_INT LVAR_INT
    IS_INT_VAR_EQUAL_TO_INT_LVAR VAR_INT LVAR_INT
    IS_FLOAT_VAR_EQUAL_TO_NUMBER VAR_FLOAT FLOAT
    IS_FLOAT_LVAR_EQUAL_TO_NUMBER LVAR_FLOAT FLOAT
    IS_FLOAT_VAR_EQUAL_TO_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    IS_FLOAT_LVAR_EQUAL_TO_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    IS_FLOAT_VAR_EQUAL_TO_FLOAT_LVAR VAR_FLOAT LVAR_FLOAT
    IS_INT_VAR_EQUAL_TO_CONSTANT VAR_INT ANY_INT
    IS_INT_LVAR_EQUAL_TO_CONSTANT LVAR_INT ANY_INT
    IS_VAR_TEXT_LABEL_EQUAL_TO_TEXT_LABEL VAR_TEXT_LABEL TEXT_LABEL
    IS_LVAR_TEXT_LABEL_EQUAL_TO_TEXT_LABEL LVAR_TEXT_LABEL TEXT_LABEL
    IS_INT_LVAR_EQUAL_TO_INT_VAR LVAR_INT VAR_INT
    IS_FLOAT_LVAR_EQUAL_TO_FLOAT_VAR LVAR_FLOAT VAR_FLOAT

**Side-effects**

Returns whether the value on the left is equal the value on the right.

### IS_THING_GREATER_THAN_THING

**Alternatives**

    IS_INT_VAR_GREATER_THAN_NUMBER VAR_INT INT
    IS_INT_LVAR_GREATER_THAN_NUMBER LVAR_INT INT
    IS_NUMBER_GREATER_THAN_INT_VAR INT VAR_INT
    IS_NUMBER_GREATER_THAN_INT_LVAR INT LVAR_INT
    IS_INT_VAR_GREATER_THAN_INT_VAR VAR_INT VAR_INT
    IS_INT_LVAR_GREATER_THAN_INT_LVAR LVAR_INT LVAR_INT
    IS_INT_VAR_GREATER_THAN_INT_LVAR VAR_INT LVAR_INT
    IS_INT_LVAR_GREATER_THAN_INT_VAR LVAR_INT VAR_INT
    IS_FLOAT_VAR_GREATER_THAN_NUMBER VAR_FLOAT FLOAT
    IS_FLOAT_LVAR_GREATER_THAN_NUMBER LVAR_FLOAT FLOAT
    IS_NUMBER_GREATER_THAN_FLOAT_VAR FLOAT VAR_FLOAT
    IS_NUMBER_GREATER_THAN_FLOAT_LVAR FLOAT LVAR_FLOAT
    IS_FLOAT_VAR_GREATER_THAN_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    IS_FLOAT_LVAR_GREATER_THAN_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    IS_FLOAT_VAR_GREATER_THAN_FLOAT_LVAR VAR_FLOAT LVAR_FLOAT
    IS_FLOAT_LVAR_GREATER_THAN_FLOAT_VAR LVAR_FLOAT VAR_FLOAT
    IS_INT_VAR_GREATER_THAN_CONSTANT VAR_INT ANY_INT
    IS_INT_LVAR_GREATER_THAN_CONSTANT LVAR_INT ANY_INT
    IS_CONSTANT_GREATER_THAN_INT_VAR ANY_INT VAR_INT
    IS_CONSTANT_GREATER_THAN_INT_LVAR ANY_INT LVAR_INT

**Side-effects**

Returns whether the value on the left is greater than the value on the right.

### IS_THING_GREATER_OR_EQUAL_TO_THING

**Alternatives**

    IS_INT_VAR_GREATER_OR_EQUAL_TO_NUMBER VAR_INT INT
    IS_INT_LVAR_GREATER_OR_EQUAL_TO_NUMBER LVAR_INT INT
    IS_NUMBER_GREATER_OR_EQUAL_TO_INT_VAR INT VAR_INT
    IS_NUMBER_GREATER_OR_EQUAL_TO_INT_LVAR INT LVAR_INT
    IS_INT_VAR_GREATER_OR_EQUAL_TO_INT_VAR VAR_INT VAR_INT
    IS_INT_LVAR_GREATER_OR_EQUAL_TO_INT_LVAR LVAR_INT LVAR_INT
    IS_INT_VAR_GREATER_OR_EQUAL_TO_INT_LVAR VAR_INT LVAR_INT
    IS_INT_LVAR_GREATER_OR_EQUAL_TO_INT_VAR LVAR_INT VAR_INT
    IS_FLOAT_VAR_GREATER_OR_EQUAL_TO_NUMBER VAR_FLOAT FLOAT
    IS_FLOAT_LVAR_GREATER_OR_EQUAL_TO_NUMBER LVAR_FLOAT FLOAT
    IS_NUMBER_GREATER_OR_EQUAL_TO_FLOAT_VAR FLOAT VAR_FLOAT
    IS_NUMBER_GREATER_OR_EQUAL_TO_FLOAT_LVAR FLOAT LVAR_FLOAT
    IS_FLOAT_VAR_GREATER_OR_EQUAL_TO_FLOAT_VAR VAR_FLOAT VAR_FLOAT
    IS_FLOAT_LVAR_GREATER_OR_EQUAL_TO_FLOAT_LVAR LVAR_FLOAT LVAR_FLOAT
    IS_FLOAT_VAR_GREATER_OR_EQUAL_TO_FLOAT_LVAR VAR_FLOAT LVAR_FLOAT
    IS_FLOAT_LVAR_GREATER_OR_EQUAL_TO_FLOAT_VAR LVAR_FLOAT VAR_FLOAT
    IS_INT_VAR_GREATER_OR_EQUAL_TO_CONSTANT VAR_INT ANY_INT
    IS_INT_LVAR_GREATER_OR_EQUAL_TO_CONSTANT LVAR_INT ANY_INT
    IS_CONSTANT_GREATER_OR_EQUAL_TO_INT_VAR ANY_INT VAR_INT
    IS_CONSTANT_GREATER_OR_EQUAL_TO_INT_LVAR ANY_INT LVAR_INT

**Side-effects**

Returns whether the value on the left is greater than or equal to the value on the right.

Appendix
------------

### Regular Lexical Grammar

```
# A Regular Lexical Grammar for GTA3script
sep := sep ;
eol := eol ;
token := token_char {token_char} 
       | '-' (digit | '.') {token_char} ;
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

There are only operators, separators, unclassified tokens, and string literals.

Each unclassified token requires parsing context in order to be classified.

Comments are excluded from this grammar because nested block comments are context-free.

This regular grammar is not capable of handling the complete set of words generated by `filename`. For instance, `file-name.sc` would not be interpreted properly. A translator should be careful to handle this case properly.

The following are examples of context dependency for token classification:

```
// for the sake of simplicity separation tokens are omitted.

WORD: WORD:    // label(WORD:) command(WORD:)

WORD WORD      // command(WORD) identifier(WORD)

1234 1234      // command(1234) integer(1234)

X = Y          // identifier(X) '=' identifier(Y)
X Y            // command(X) identifier(Y)

X --           // identifier(X) '--'
X -1           // command(X) integer(-1)

LAUNCH_MISSION a.sc // command(LAUNCH_MISSION) filename(a.sc)
OTHER_COMMAND a.sc  // command(OTHER_COMMAND) identifier(a.sc)
// NOTE: filename is not an identifier because, for instance,
// filename(4x4.sc) cannot be classified as an identifier.

OR             // command(AND)
NOT            // command(NOT)
IF SOMETHING   //
OR OR          // 'OR' command(OR)
OR NOT NOT     // 'OR' 'NOT' command(NOT)
    NOP        //
ENDIF          //

// NOTE: that is a defect actually, see following example:
IF SOMETHING
    AND var    // 'AND' command(var) -- not what we want
    // same problem for OR.
    // NOT is affected by IF NOT var.
ENDIF
```

### Ambiguity

Not only the language, but the grammar presented in this document is ambiguous. Here are all the instances of ambiguity, which is the correct derivation, and suggestions to avoid users getting trapped in them.

#### IF GOTO

```
IF COMMAND goto other
COMMAND goto other
```

The first line could mean an command, taking two arguments, `goto` and `other`. Or, it could mean that if the command returns true, a jump should be performed into the `other` label. The correct interpretation is the latter.

The second line is unambiguous due to context.

We suggest an implementation to emit an warnings to declarations of names and the use of text labels equal to `goto`.

#### Ternary Minus One

```
x = 1-1
x = 1 -1
x = 1 - 1
x = 1--1
x = 1- -1
```

The first line could mean `1` minus `1`, or it could mean `1` and then the number `-1`. The latter is the correct interpretation. And yes, it is a syntax error.

The second line has the same ambiguity and its interpretation should be the same as the first line.

The third line is not ambiguous.

The fourth line is ambiguous. Its actual meaning is `1` followed by the unary operator `--` and it is a syntax error.

The fifth line is not ambiguous.

The token stream produced by the regular lexical grammar in the appendix should solve this issue naturally.

### How to MISS2

The leaked script compiler is full of bugs. It was written for in-house use, so it's meant to work and recognize at least the intended language. The problem is, the language is too inconsistent in this buggy superset. After constantly trying to make those bugs part of this specification, I strongly believe we shouldn't. For the conservative, the following is a list of known things miss2 accepts that this specification does not.

Do note a regular lexical grammar (like above) cannot be built for the language recognized by miss2.

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

WHILENOT only accepts equality comparison

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

**labels in AND/OR**

miss2 allows labels to prefix AND/OR conditions. However, it produces weird code. As such, this specification does not accept it.

```
IF x = 0
lab_or: OR x = 1 // goes to the WAIT 0 after the last condition
OR x = 2         // this specification does not accept this
    WAIT 1
ELSE
    WAIT 2
ENDIF
```

**weird closing blocks**

stuff like the following is recognized by miss2

```
WHILE x = 0
    IF y = 1
        WAIT 0
ENDWHILE
    ENDIF
// this specification does not accept this (nor variations of this)
```

this happens with scopes, IFs, REPEATs, WHILEs, `MISSION_END`, and what not.

it is very interesting actually, but clearly a language bug (would not say a implementation bug though).

**exclusive scripts**

we don't really what are these, so we won't specify them.



TODO shall should must cannot could may etc
TODO SAN ANDREAS ALLOWS IDENTIFIERS TO BEGIN WITH UNDERSCORES 
TODO scripts subscripts mission script and such (what are the execution differences)
TODO translation limits
TODO what about commands that do not produce compare flag changes but may appear in a conditional statement
TODO timera timerb (remember, only within scope; cannot declare var with same name; global shall not be named timera/timerb)
TODO better name for what we are calling require statements
TODO interesting NOP is not compiled
TODO rockstar does not know if it calls arg 17 a text string or a string identifier. I will go for identifier.
TODO specify array access pattern (is first index 0? is a[0] valid for non-array? for sure a[2] does not if out-of-bounds)
TODO SAVE_VAR_INT
TODO should we fix the floating point literals (e.g. '1.9.2')? I think there are DMA scripts that need this.
TODO maybe move the semantic definition that we cannot use mission script labels from outside it from concepts to the script file structure section
TODO the rationale for global having unspecified initial value: Stories variable sharing (must read more though).
TODO read gta3sc issues and source for quirks
TODO re-read Wesser's PM
TODO fix AND OR NOT defect?
TODO list of special command names (user cannot write these)
TODO creating packages and such are declarations too (not only var decls)
TODO correctly specify that a[1] = a[1]abc + 2 is not the same as a[1] = a[1] + 2
TODO unclosed nested comments is a error
TODO talk about repetion of filenames and using in different script types
TODO no duplicate script name
TODO define semantics for `arr` (no brackets)
TODO declarations, entities and variable usage
TODO label semantics of start new script (GTA3 allows label: {})
TODO remember GTASA INPUT_OPT does not accept text label vars at all (not at runtime level)

LIMITS
TODO gxtsema gxt key length <8
TODO gxtsema filename (excluding extension must be) <16
TODO label name <=38
TODO varname <40
TODO scriptname <=7
TODO scriptnames <= 300
TODO <=9216 gvar storage words
TODO <=16 lvars storage words
TODO <=255 array size
TODO <=35000 label refs
TODO <=255 line
TODO <=127 string


Arachniography
--------------------

 1. [Official GTA2script Compiler V9.6](http://gtamp.com/GTA2/gta2script.7z) by DMA Design.
 2. [Official GTA2script Scripting Information](https://public.thelink2012.xyz/gta3/GTA2%20Scripting.html) by DMA Design. 
 3. [Official GTA3 Script Compiler V413](https://www.dropbox.com/s/7xgvqo8b9u1qw02/gta3sc_v413.rar) by Rockstar North.
 4. [GTA III 10th Anniversary Multiscripts Source Code](https://public.thelink2012.xyz/gta3/gta3_main_source.7z) by Rockstar North, War Drum Studios.
 5. [GTA3 Script Compiler V413 Strings](http://pastebin.com/raw/Pjb0Ezkx) organized by Wesser.
 6. [GTA3 Script Compiler V413 Definitions](https://www.dropbox.com/s/zkn59hrw7o76ry7/gta3vc_sc_defines.rar) organized by Wesser.
 7. [GTASA Mobile Symbol Listing](https://pastebin.com/raw/2VczpwK7) organized by LINK/2012.
 8. [Work-In-Progress SCM Language Article](http://pastebin.com/raw/YfLWLXJw) by Wesser.
 9. [Ancient SCM Language Article](http://web.archive.org/web/20170111193059/http://www.gtamodding.com/wiki/GTA3script) by Wesser.

