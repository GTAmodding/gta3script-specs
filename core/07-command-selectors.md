Command Selectors
========================

A *command selector* (or *alternator*) is a kind of command which gets rewritten by the translator to another command based on the supplied argument types.

A command selector consists of a name and a finite sequence of commands which are alternatives for replacement.

A command name which is the name of a selector shall behave as if its command name is rewritten as a *matching alternative* before any parameter checking takes place.

A *matching alternative* is the first command in the alternative sequence to have the same amount of parameters as arguments in the actual command, and to obey the following rules for every argument and its corresponding parameter:

+ An integer literal argument must have a parameter of type *INT*.
+ A floating-point literal argument must have a parameter of type *FLOAT*.
+ For identifiers, the following applies (in the given order):
  1. If the identifier matches a global string constant, the parameter type must be *INT*.
  2. If the identifier references a global variable, the parameter type must be either (depending on the type of the said variable) *VAR_INT*, *VAR_FLOAT* or *VAR_TEXT_LABEL*.
  3. If the identifier references a local variable, the same rule as above applies, except by using *LVAR_INT*, *LVAR_FLOAT* and *LVAR_TEXT_LABEL*.
  4. If the identifier matches any string constant in any enumeration, the parameter type must be *INPUT_INT* and the argument shall behave as if rewritten as an integer literal corresponding to the string constant's value.
  5. Otherwise, the parameter type must be *TEXT_LABEL*.

If no matching alternative is found, the program is ill-formed.

