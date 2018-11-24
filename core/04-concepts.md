Concepts
====================

## Scripts

A *script* is a unit of execution which contains its own *program counter*, *local variables* and *compare flag*.

A *program* is a collection of scripts running concurrently in a cooperative fashion.

A *variable* is a named storage location. This location holds a value of specific type.

There are global and local variables. *Global variables* are stored in a way they are accessible from any script. *Local variables* are said to pertain to the particular script and only accessible from it.

The lifetime of a *global variable* is the same as of the execution of all scripts. The lifetime of a *local variable* is the same as its script and lexical scope.

A *command* is an operation to be performed by a script. Commands produces *side-effects* which are described by each command description.

A possible side-effect of executing a command is the updating of the *compare flag*. The *compare flag* of a command is the boolean result it produces. The *compare flag of a script* is the *compare flag* of the its last executed command. The *compare flag* is useful for conditionally changing the *flow of control*.

The *program counter* of a script indicates its currently executing command. Unless one of the *side-effects* of a command is to change the *program counter*, the counter goes from the current command to the next sequentially. An explicit change in the *program counter* is said to be a change in the *flow of control*.

A command is said to perform a *jump* if it changes the *flow of control* irreversibly.

A command is said to call a *subroutine* if it changes the *flow of control* but saves the current *program counter* in a stack to be restored later.

A command is said to *terminate* a script if it halts and reclaims storage of such a script.

## Script Files

A *script file* is a source file containing a sequence of commands. Those commands are executed concurrently by multiple scripts.

The *multi-file* is a collection of *script files*. Hereafter being the collection of *script files* being translated.

The *main script file* is the entry script file. This is where the first script (called the *main script*) starts execution. Translation begins here.

Other script files are *required* to become part of the *multi-file* by the means of require statements within the *main script file*. The *main script file* itself is required from the translation environment.

Many kinds of script files can be *required*.

A *main extension file* (or *foreign gosub file*) is a script file required by the means of a *GOSUB_FILE statement*. Other script files can be required from here as well.

A *subscript file* is a script file required by the means of the *LAUNCH_MISSION statement*. A *subscript* is a script started by the same statement.

A *mission script file* is a script file required by the means of the *LOAD_AND_LAUNCH_MISSION statement*. A *mission script* is a script started by the same statement. Only a single *mission script* can be running at once.

Commands in the *main script file*, *main extension files* and *subscript files* shall not refer to labels in *mission script files*. A *mission script file* shall not refer to labels in other *mission script files*.

The *main script file* is found in a unspecified manner. The other *script files* are found by recursively searching a directory with the same filename (excluding extension) as the *main script file*. This directory is in the same path as the *main script file*. The search for the *script files* shall be case-insensitive. All *script files* must have a `.sc` extension. If multiple script files with the same name are found, behaviour is unspecified.

A script type is said to come before another script type under the following total order:

 1. Main script.
 2. Main extension script.
 3. Subscript.
 4. Mission script.

A script file *A* (first required from *X*) is said to come before a script file *B* (first required from *Y*) under the following total order:

 1. If *A*'s script type is not the same as *B*'s, then *A* comes before *B* if and only if *A*'s script type comes before *B*'s script type.
 2. Otherwise, if *X* is not the same as *Y*, *A* comes before *B* if and only if *X* comes before *Y*.
 3. Otherwise, *A* comes before *B* if and only if the line on which *A* is first required from (in *X*) comes before the line on which *B* is first required from.

A line of code *A* in a script file *X* is said to come before a line *B* in a script file *Y* different from *X* if and only if *X* comes before *Y*.

## Types

An *integer* is a binary signed two's-complement integral number. It represents 32 bits of data and the range of values *-2147483648* through *2147483647*.

A *floating-point* is a representation of a real number. Its exact representation, precision and range of values is implementation-defined.

A *label* is a name specifying the location of a command.

A *text label* is a name whose value is only known in the execution environment.

A *string* is a sequence of zero or more characters.

An *array* is a collection of one or more elements of the same type. Each element is indexed by an integer key.

