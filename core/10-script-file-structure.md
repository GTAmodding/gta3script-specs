Script File Structure
============================

## Main Script Files

```
main_script_file := {statement} ;
```

A main script file is a sequence of zero or more statements.

**Semantics**

The main script starts execution at the first statement of the main script file. If there is no statement to be executed, behaviour is unspecified.

## Main Extension Files

```
main_extension_file := {statement} ;
```

A main extension file is a sequence of zero or more statements.

## Subscript Files

```
subscript_file := 'MISSION_START' eol
                  {statement}
                  [label_prefix] 'MISSION_END' eol
                  {statement} ;
```

A subscript file is a sequence of zero or more statements in a `MISSION_START` and `MISSION_END` block. More statements can follow.

**Constraints**

The `MISSION_START` command shall be the very first line of the subscript file and shall not be preceded by anything but ASCII spaces (` `) and horizontal tabs (`\t`). Even comments are disallowed.

**Semantics**

The `MISSION_END` command behaves as if by executing the `TERMINATE_THIS_SCRIPT` command.

## Mission Script Files

```
mission_script_file := subscript_file ;
```

A mission script file has the same structure of a subscript file.


