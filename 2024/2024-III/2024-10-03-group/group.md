# Группировка в функциях и файлах

## 1. Теория
Узнал вот какой лайфхак: если функция (класс, модуль) получилась большой,
и/или явно состоит из нескольких частей, то не нужно сразу стараться
разбить её на части.



## 2. Практика

```Python
def solve(
            self, initial: Tensor, mesh: Tensor,
            shift: float | Tensor = 0, scale: float | Tensor = 1,
            atol: Optional[float] = None, rtol: Optional[float] = None,
            ) -> Tensor:
        #region: Check and prepare args...

        #region: Prepare raw data...
        
        #region: Solve the ODE...

        #region: Pack the result...

```

```Python
class Tensor(MROChain, np.lib.mixins.NDArrayOperatorsMixin):
    #region: Fields and properties...

    #region: Initialization...

    #region: Array interface...

    #region: Auxiliary functions...
```

```Python
class Test_Tensor(TensorTest):

    #region: Core stuff...

    #region: Simple initialization tests...

    #region: Complex packing tests...
```
