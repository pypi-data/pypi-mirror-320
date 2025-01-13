import tempfile
from packaging import version

import pytest

import zarr.storage
import zarr

from ngff_zarr import Methods, to_multiscales, to_ngff_zarr, from_ngff_zarr

from ._data import verify_against_baseline

zarr_version = version.parse(zarr.__version__)

# Skip tests if zarr version is less than 3.0.0b1
pytestmark = pytest.mark.skipif(
    zarr_version < version.parse("3.0.0b1"), reason="zarr version < 3.0.0b1"
)


def test_gaussian_isotropic_scale_factors(input_images):
    dataset_name = "cthead1"
    image = input_images[dataset_name]
    baseline_name = "2_4/RFC3_GAUSSIAN.zarr"
    multiscales = to_multiscales(image, [2, 4], method=Methods.ITKWASM_GAUSSIAN)
    store = zarr.storage.MemoryStore()

    version = "0.5"
    to_ngff_zarr(store, multiscales, version=version)
    multiscales = from_ngff_zarr(store, version=version)
    # store_new_multiscales(dataset_name, baseline_name, multiscales, version=version)
    verify_against_baseline(dataset_name, baseline_name, multiscales, version=version)

    array0 = zarr.open_array(store=store, path="scale0/image", mode="r", zarr_format=3)
    dimension_names = array0.metadata.dimension_names
    for idx, ax in enumerate(multiscales.metadata.axes):
        assert ax.name == dimension_names[idx]


def test_gaussian_isotropic_scale_factors_tensorstore(input_images):
    pytest.importorskip("tensorstore")

    dataset_name = "cthead1"
    image = input_images[dataset_name]
    baseline_name = "2_4/RFC3_GAUSSIAN.zarr"
    multiscales = to_multiscales(image, [2, 4], method=Methods.ITKWASM_GAUSSIAN)

    version = "0.5"
    with tempfile.TemporaryDirectory() as tmpdir:
        to_ngff_zarr(tmpdir, multiscales, version=version, use_tensorstore=True)
        multiscales = from_ngff_zarr(tmpdir, version=version)
        # store_new_multiscales(dataset_name, baseline_name, multiscales, version=version)
        verify_against_baseline(
            dataset_name, baseline_name, multiscales, version=version
        )

        array0 = zarr.open_array(
            store=tmpdir, path="scale0/image", mode="r", zarr_format=3
        )
        dimension_names = array0.metadata.dimension_names
        for idx, ax in enumerate(multiscales.metadata.axes):
            assert ax.name == dimension_names[idx]
