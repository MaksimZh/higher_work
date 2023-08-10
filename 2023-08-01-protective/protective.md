# Защитный код

# 1.
```Python
class WaveMatrices:
    __tensor: Tensor
    __axes: WaveMatrixAxes

    def __init__(
            self,
            tensor: Tensor,
            dir: str,
            components: str | set[str],
            extra: set[str] = set()) -> None:
        if isinstance(components, str):
            components = {components}
        assert all_str_unique(dir, components, extra)
        assert to_str_set(dir, components, extra) <= tensor.axes
        assert dir not in components
        assert tensor.get_dim(dir) == 2
        wave_axes = WaveAxes(dir, extra)
        wave_dims = [tensor.get_dim(ax) for ax in to_str_set(wave_axes)]
        wave_dims_combined = reduce(mul, wave_dims, 1)
        component_dims = [tensor.get_dim(ax) for ax in components]
        component_dims_combined = reduce(mul, component_dims, 1)
        assert wave_dims_combined == component_dims_combined
        self.__tensor = tensor
        self.__axes = WaveMatrixAxes(wave_axes, components)

    ...
```
```Python
class WaveMatrices(Tensor):

    def __init__(
            self,
            array: NDArray[Any, Any],
            *axes: Axis) -> None:
        super().__init__(array, *axes)
        dir_axes = self.get_axes(WaveDirAxis)
        assert len(dir_axes) == 1
        dir_axis = dir_axes.pop()
        assert self.get_dim(dir_axis) == 2
        wave_dims = [self.get_dim(ax) for ax in self.get_axes(WaveAxis)]
        wave_dims_combined = reduce(mul, wave_dims, 1)
        component_dims = [self.get_dim(ax) for ax in self.get_axes(ComponentAxis)]
        component_dims_combined = reduce(mul, component_dims, 1)
        assert wave_dims_combined == component_dims_combined
    
    ...
```


# 2.
```Python
class MatchMatrices:
    __tensor: Tensor
    __axes: MatchMatrixAxes

    def __init__(
            self,
            tensor: Tensor,
            row_dir: str, col_dir: str,
            extra: dict[str, str] = {}) -> None:
        assert all_str_unique(row_dir, col_dir, extra.keys(), extra.values())
        assert to_str_set(row_dir, col_dir, extra.keys(), extra.values()) <= tensor.axes
        assert tensor.get_dim(row_dir) == 2
        assert tensor.get_dim(col_dir) == 2
        assert all([(tensor.get_dim(a) == tensor.get_dim(b)) for (a, b) in extra.items()])
        self.__tensor = tensor
        self.__axes = MatchMatrixAxes(row_dir, col_dir, extra)

    ...
```
```Python
class MatchMatrices(Tensor):
    __row_links: dict[WaveAxis, WaveAxis]
    __col_links: dict[WaveAxis, WaveAxis]
    
    def __init__(
            self,
            array: NDArray[Any, Any],
            *axes: Axis | LinkedAxes) -> None:
        self.__row_links = dict()
        self.__col_links = dict()
        tensor_axes = list[Axis]()
        for ax in axes:
            if isinstance(ax, LinkedAxes):
                assert ax.row not in self.__row_links
                self.__row_links[ax.row] = ax.col
                assert ax.col not in self.__col_links
                self.__col_links[ax.col] = ax.row
                tensor_axes.append(ax.col)
                continue
            tensor_axes.append(ax)
        super().__init__(array, *tensor_axes)
        row_dir_axes = set(self.get_axes(WaveDirAxis) & self.__row_links.keys())
        assert len(row_dir_axes) == 1
        col_dir_axes = set(self.get_axes(WaveDirAxis) & self.__col_links.keys())
        assert len(col_dir_axes) == 1
        assert self.row_axis_for(self.col_dir_axis) == self.row_dir_axis
        assert self.col_axis_for(self.row_dir_axis) == self.col_dir_axis
        assert self.get_dim(self.row_dir_axis) == 2
        assert self.get_dim(self.col_dir_axis) == 2
        assert (self.__row_links.keys() | self.__col_links.keys()) == self.get_axes(WaveAxis)
        for row, col in self.__row_links.items():
            assert self.get_dim(row) == self.get_dim(col)
    
    ...
```


# 3.
```Python
def calc_transfer_matrices(
        left_wave: WaveMatrices, right_wave: WaveMatrices,
        row_suffix: str, col_suffix: str,
        ) -> TransferMatrices:
    assert row_suffix != col_suffix
    assert left_wave.dir_axis == right_wave.dir_axis
    assert left_wave.extra_wave_axes == right_wave.extra_wave_axes
    assert left_wave.component_axes == right_wave.component_axes
    assert left_wave.array_axes == right_wave.array_axes
    dir_axis = left_wave.dir_axis
    extra_axes = tuple(left_wave.extra_wave_axes)
    component_axes = tuple(left_wave.component_axes)
    array_axes = tuple(left_wave.array_axes)
    array_shape = tuple(left_wave.tensor.get_dim(ax) for ax in array_axes)
    assert all(
        left_wave.tensor.get_dim(ax) == right_wave.tensor.get_dim(ax) \
        for ax in left_wave.tensor.axes)
    ...
```
```Python
def calc_transfer_matrices(
        left_wave: WaveMatrices, right_wave: WaveMatrices,
        *col_axes: LinkedAxes
        ) -> TransferMatrices:
    assert left_wave.axes == right_wave.axes
    axes_tuple = tuple(left_wave.axes)
    assert left_wave.get_array(*axes_tuple).shape == right_wave.get_array(*axes_tuple).shape
    __row_links = dict[WaveAxis, WaveAxis]((ax.row, ax.col) for ax in col_axes)
    assert __row_links.keys() == left_wave.get_axes(WaveAxis)
    ...
```
