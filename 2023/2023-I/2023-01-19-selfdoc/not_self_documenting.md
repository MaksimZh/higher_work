# Несамодокументирующийся код
[Полный код](https://github.com/MaksimZh/sintez/blob/master/nodes.py)

Поскольку узлы-значения и узлы-процедуры связаны единой логикой,
в начале модуля добавлен общий комментарий:
```Python
# Nodes implement the calculation scheme logic.
#
# ValueNode can be linked only to ProcedureNodes and vice versa.
# All links have one and only one direction, no loops allowed.
# The basic concepts of calculation are invalidation and validation.
# Value change invalidates all succeeding nodes.
# Procedure validation also validates all its output nodes.
# When node is invalidated it invalidates all succeeding nodes.
# When node is validated it requests validation of all preceding nodes.
#
# When node is created its build is incomplete.
# Inputs and outputs can be added only before build is complete.
# Manipulations concerning calculation logic are forbidden until build is complete.
```

Отдельно для каждого типа узлов:
```Python
# Implements value node part of calculation scheme logic.
# Can have only one (optional) input procedure.
# So there is only one component responsible for value update.
#
# Note that value must be validated before 'get' query is used.
#
# Contains:
#     - input procedure node (optional)
#     - output procedure nodes (any number)
#     - value type
#     - build status
#     - value state (INVALID, NEW, REGULAR)
#     - value (optional)
#     - outputs that have not used NEW value
#
@final
class ValueNode:
    ...
```
```Python
# Implements procedure node part of calculation scheme logic.
#
# Contains:
#     - input value nodes (any number)
#     - output procedure nodes (any number)
#     - build status
#     - procedure
#
@final
class ProcedureNode:
    ...
```
Раздел `Contains` - это не внутреннее устройство класса,
а список элементов логики.
Все пред- и постусловия теперь переписаны так, чтобы они оперировали
с этими элементами, например:
```Python
# Contains:
#     - input procedure node (optional)
#     - output procedure nodes (any number)
#     ...
#     - build status
#     ...
#
@final
class ValueNode:
    ...

    # add output node
    # PRE: build not complete
    # PRE: 'output' is not in input or outputs
    # POST: 'output' added to output nodes
    def add_output(self, output: "ProcedureNode") -> None:
        ...
```

А вот и оставшиеся два класса из того же модуля:
```Python
# Base class for the internal procedure of ProcedureNode
# 
# When the user gets any output value it must be up to date with input values.
# Procedure implementation must take care of the (protected) status fields.
#
# Contains:
#     - named and typed input values
#     - named output values 
#
class Procedure(ABC):
    ...
```
```Python
# Special kind of procedure that contains calculation scheme built using
# its declarative description sent to constructor.
#
# The description is list of value and procedure patterns.
# Value pattern is the following tuple:
#     ("name", ValueType).
# Procedure pattern is the following tuple:
#     (ProcedureType, <input_dictionary>, <output_dictionary>).
# Entries in input and output dictionaries are of the following two kinds:
#     "name_in_procedure": "value_node_name" - link to value node by name
#     "name_in_procedure_and_outside": Type - create value node and link to it
# If multiple I/O entries of the 2nd kind have the same name
# then their types must match. 
#
class Simulator(Procedure):
    ...
```