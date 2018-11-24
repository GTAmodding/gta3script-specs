Statements
================================

A statement specifies an action to be executed.

```
statement := labeled_statement 
           | embedded_statement ;
```

## Labeled Statements

Statements can be prefixed with a label.

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

The label can be referenced in certain commands to transfer (or start) control of execution to the statement it prefixes. Labels themselves do not alter the flow of control, which continues to the statement it embodies.

## Empty Statements

```
empty_statement := eol ;
```

**Semantics**

An empty statement does nothing.

## Embedded Statements

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

## Command Statements

```
command_statement := command eol ;
```

**Constraints**

The command it embodies cannot be any of the commands specified by this section (e.g. `VAR_INT`, `ELSE`, `ENDWHILE`, `{`, `GOSUB_FILE`, `MISSION_START`, etc).

## Expression Statements

```
expression_statement := assignment_expression eol
                      | conditional_expression eol ;
```

**Semantics**

An expression statement executes the expression it embodies.

The execution of the assignment expression `a = b` is favored over the execution of the conditional expression of the same form.

## Scope Statements

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

## Variable Declaration Statements

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

Local variables can have identical names as long as they are in different lexical scopes.

Local variables shall not have the same name as any global variable.

A variable shall not have the same name as any string constant in any enumeration (except for the global enumeration).

The array dimensions of the variable (if any) must be specified by an integer literal greater than zero.

**Semantics**

This command declares one or more names with the specified storage duration, type, and array dimensions.

Global variable names can be seen by the entire multi-file.

Local variable names can be seen by their entire lexical scope.

The initial value of variables is unspecified.

## Conditional Statements

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

## Selection Statements

Selection statements selects which statement to execute depending on certain conditions.

### IF Statement

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

### IFNOT Statement

```
ifnot_statement := 'IFNOT' sep conditional_list
                   {statement}
                   [[label_prefix] 'ELSE' eol
                   {statement}]
                   [label_prefix] 'ENDIF' eol ;
```

**Semantics**

The behaviour of this is the same as of the IF statement, except the complement of the compare flag is used to test which set of statements to execute.

### IF GOTO Statement

```
if_goto_statement := 'IF' sep conditional_element sep 'GOTO' sep identifier eol ;
```

**Semantics**

This statement performs a jump to the label specified by identifier if the compare flag of the conditional element holds true. Otherwise, the flow of control is unchanged.

### IFNOT GOTO Statement

```
ifnot_goto_statement := 'IFNOT' sep conditional_element sep 'GOTO' sep identifier eol ;
```

**Semantics**

The behaviour of this is the same as of the IF GOTO statement, except the complement of the compare flag is used to test whether to jump.

## Iteration Statements

### WHILE Statement

```
while_statement := 'WHILE' sep conditional_list
                   {statement}
                   [label_prefix] 'ENDWHILE' eol ;
```

**Semantics**

The WHILE statement executes a set of statements while the compare flag of the conditional list holds true.

The statement executes by grabbing the compare flag of the list of conditions and transferring control to after the WHILE block if it holds false. Otherwise, it executes the given set of statements. Execution of the `ENDWHILE` command causes control to be transferred to beginning of the block, where the conditions are evaluated again.

### WHILENOT Statement

```
whilenot_statement := 'WHILENOT' sep conditional_list
                      {statement}
                      [label_prefix] 'ENDWHILE' eol ;
```

**Semantics**

The behaviour of this is the same as of the WHILE statement, except the complement of the compare flag is used to test whether to continue executing the set of statements.

### REPEAT Statement

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

## Require Statements

```
filename := {graph_char} '.SC' ;

require_statement := command_gosub_file
                   | command_launch_mission
                   | command_load_and_launch_mission ;
```

Require statements request script files to become part of the multi-file being translated.

**Constraints** 

Require statements shall only appear in the *main script file* or *main extension files*.

### GOSUB_FILE Statement

```
command_gosub_file := 'GOSUB_FILE' sep identifier sep filename eol ;
```

**Semantics**

The `GOSUB_FILE` command requires a *main extension file* to become part of the multi-file.

It also calls the subroutine specified by label.

The behaviour is unspecified if the label is not part of the required file.

### LAUNCH_MISSION Statement

```
command_launch_mission := 'LAUNCH_MISSION' sep filename eol ;
```

**Semantics**

The `LAUNCH_MISSION` command requires a *subscript file* to become part of the multi-file. 

It also starts a new subscript with the program counter at the `MISSION_START` directive of the specified script file.

### LOAD_AND_LAUNCH_MISSION Statement

```
command_load_and_launch_mission := 'LOAD_AND_LAUNCH_MISSION' sep filename eol ;
```

**Constraints**

Only a single *mission script* can be running at once.

**Semantics**

The `LOAD_AND_LAUNCH_MISSION` command requires a *mission script file* to become part of the multi-file. 

It also starts a new *mission script* with the program counter at the `MISSION_START` directive of the specified script file.


