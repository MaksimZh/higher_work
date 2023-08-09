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


# 3.
```Python
class EnvelopeHamiltonian(Operator):
    __band_axes: tuple[str, str]

    def __init__(
            self,
            array: NDArray[Any, Any],
            *axes: str | tuple[str, Basis],
            ) -> None:
        super().__init__(array, *axes)
        envelope_axes = [
            name for name, basis in self.bases.items() \
                if isinstance(basis, EnvelopeBasis)]
        dual_envelope_axes = [
            name for name, basis in self.bases.items() \
                if isinstance(basis, DualBasis) and \
                    isinstance(basis.origin, EnvelopeBasis)]
        assert len(envelope_axes) == 1
        assert len(dual_envelope_axes) == 1
        self.__band_axes = (envelope_axes[0], dual_envelope_axes[0])
        band_basis = self.get_basis(self.band_left_axis)
        assert isinstance(band_basis, EnvelopeBasis)
        dual_band_basis = self.get_basis(self.band_right_axis)
        assert isinstance(dual_band_basis, DualBasis)
        assert dual_band_basis.origin is band_basis

    ...
```


# 4.
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
