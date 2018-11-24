Parameters
=======================

A command receives several arguments. Every argument must obey the rules of its corresponding *parameter definition*.

A *parameter definition* is a set of definitions regarding a single parameter for a specific command.

A command must have the same amount of arguments as its amount of parameter definitions, unless the missing arguments correspond to *optional parameters* (defined below).

If a variable is used in the same command both as an input and as an output, the input shall be evaluated before any output is assigned to the variable.

## String Constants

A *string constant* is a name associated with an integer value. Such association is known in the translation environment.

An *enumeration* is a collection of string constants.

A parameter definition can have an associated enumeration. A string constant is said to be a match if an identifier in an argument refers to a name in its parameter's enumeration.

There is an special enumeration called the *global string constants enumeration* which semantics are defined along this specification. Other enumerations can be defined by an implementation.

If a parameter definition specifies an enumeration, the global string constants enumeration cannot be matched in the said parameter.

## Entities

An *entity* is an object of the execution environment. Each entity has an *entity type*, which defines its purposes.

A parameter definition can have an associated entity type.

An entity can be assigned to a variable. In such case, the variable is said to be of that specific entity type from that line of code on. Previous lines of code are not affected.

If an entity type is associated with an parameter and a variable is used as argument, the variable must have the same entity type as the parameter.

Further semantics for entities are defined along this document.

## Parameter Types

### INT

An *INT parameter* accepts an argument only if it is an integer literal or an identifier matching a global string constant.

### FLOAT

A *FLOAT parameter* accepts an argument only if it is a floating-point literal.

### VAR_INT

A *VAR_INT parameter* accepts an argument only if it is an identifier referencing a global variable of integer type.

### VAR_FLOAT

A *VAR_FLOAT parameter* accepts an argument only if it is an identifier referencing a global variable of floating-point type.

### LVAR_INT

A *LVAR_INT parameter* accepts an argument only if it is an identifier referencing a local variable of integer type.

### LVAR_FLOAT

A *LVAR_FLOAT parameter* accepts an argument only if it is an identifier referencing a local variable of floating-point type.

### INPUT_INT

An *INPUT_INT parameter* accepts an argument only if it is an integer literal or an identifier either matching a string constant, global string constant or referencing a variable of integer type (in this order).

### INPUT_FLOAT

An *INPUT_FLOAT parameter* accepts an argument only if it is a floating-point literal or an identifier referencing a variable of floating-point type.

### OUTPUT_INT

An *OUTPUT_INT parameter* accepts an argument only if it is an identifier referencing a variable of integer type.

If an entity type is associated with the parameter, the variable must have the same entity type as the parameter, unless there is no entity type associated with the variable. In the latter case, the parameter's entity type is assigned to the variable.

### OUTPUT_FLOAT

An *OUTPUT_FLOAT parameter* accepts an argument only if it is a identifier referencing a variable of floating-point type.

### LABEL

A *LABEL parameter* accepts an argument only if it is an identifier whose name is a label in the multi-file.

### TEXT_LABEL

A *TEXT_LABEL parameter* accepts an argument only if it is an identifier. If the identifier begins with a dollar character (`$`), its suffix must reference a variable of text label type and such a variable is the actual argument. Otherwise, the identifier is a text label.

### VAR_TEXT_LABEL

A *VAR_TEXT_LABEL parameter* accepts an argument only if it is an identifier referencing a global variable of text label type.

### LVAR_TEXT_LABEL

A *LVAR_TEXT_LABEL parameter* accepts an argument only if it is an identifier referencing a local variable of text label type.

### STRING

A *STRING parameter* accepts an argument only if it is a string literal.

### Optional Parameters

Additionally, the following parameters are defined as behaving equivalently to their correspondent parameters above, except that in case an argument is absent, parameter checking stops as if there are no more parameters to be checked.

 + *VAR_INT_OPT*
 + *VAR_FLOAT_OPT*
 + *LVAR_INT_OPT*
 + *LVAR_FLOAT_OPT*
 + *VAR_TEXT_LABEL_OPT*
 + *LVAR_TEXT_LABEL_OPT*
 + *INPUT_OPT*

Such parameters are always trailing parameters.

The *INPUT_OPT parameter* accepts an argument only if it is an integer literal, floating-point literal, or identifier referencing a variable of integer, floating-point or text label type.

