from pathlib import Path
from contextlib import closing
import json
from functools import partial
import datetime
import gzip
import shutil
import tempfile

import traceback
import dask.array as da
from distributed import Client, LocalCluster, as_completed
import xarray as xr
import zarr
from imaxt_image.io import TiffImage
import click
import logging

from .stptlib.stptraw import StptRaw


__version__ = "0.2.1"
__author__ = "Mo Alsad and Eduardo Gonzalez Solares"
__email__ = "msa51@cam.ac.uk"
_credits__ = ["Mo Alsad", "Eduardo Gonzalez Solares"]


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

if "owl2.pipeline" in logger.manager.loggerDict:
    logger = logging.getLogger("owl2.pipeline")


def _write_dataset(s, *, output, dtype):
    """Write array for each section
    """
    logger.info('Preprocessing section {}'.format(s.num))
    s_name = 'S{}'.format(str(s.num).zfill(3))
    ds = xr.Dataset()

    # create a temporary folder: usually to store extracted tif images in case gz files are provided
    tmp_dir_h = tempfile.TemporaryDirectory()
    tmp_dir = Path(tmp_dir_h.name)

    n_layers = s.meta['layers']
    columns = s.meta['columns']
    rows = s.meta['rows']
    n_channels = s.n_channels
    tiles = []
    # build cube for each section
    for t in s.tiles:
        channels = []
        for ch in range(n_channels):
            layers = []
            for layer in range(n_layers):
                f_idx = ch + layer * n_channels
                f_info = t.files[f_idx]
                if not f_info['missing']:
                    file_path = f_info['fp']
                    tif_path = file_path
                    if file_path.suffix == '.gz':
                        tif_path = tmp_dir.joinpath(file_path.stem)
                        with gzip.open(file_path, 'rb') as f_in:
                            with open(tif_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    with TiffImage(tif_path) as img:
                        dimg = img.to_dask()
                else:
                    dimg = da.zeros(dtype=dtype, shape=(rows, columns))
                layers.append(dimg)
            layers = da.stack(layers)
            channels.append(layers)
        channels = da.stack(channels)
        tiles.append(channels)
    tiles = da.stack(tiles)

    # construct array
    ntiles, nchannels, nz, ny, nx = tiles.shape
    arr = xr.DataArray(
        tiles,
        dims=('tile', 'channel', 'z', 'y', 'x'),
        name=s_name,
        coords={
            'tile': range(ntiles),
            'channel': range(nchannels),
            'z': range(nz),
            'y': range(ny),
            'x': range(nx),
        },
    )

    # assign section metadata to array
    arr.attrs['raw_meta'] = [json.loads(json.dumps(s.meta, default=str))]
    arr.attrs['missing_images'] = s.missing_images

    ds[s_name] = arr

    # append section to existing dataset and execute
    ds.to_zarr(output, mode='a')

    # clean up temp directory
    tmp_dir_h.cleanup()

    return f'{output}[{s_name}]'


def _infer_data_type(sections):
    dtype = 'uint16'
    f_info = [f for s in sections for t in s.tiles for f in t.files if not f['missing']]
    if len(f_info) > 1:
        f_info = f_info[0]
        file_path = f_info['fp']
        tif_path = file_path
        if file_path.suffix == '.gz':
            tmp_dir_h = tempfile.TemporaryDirectory()
            tmp_dir = Path(tmp_dir_h.name)
            tif_path = tmp_dir.joinpath(file_path.stem)
            with gzip.open(file_path, 'rb') as f_in:
                with open(tif_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        with TiffImage(tif_path) as img:
            dtype = img.dtype

    return dtype


def convert2zarr(stpt: StptRaw, output: Path, nparallel: int = 2, nsections: int = 0, reset: bool = False):
    """Convert STPT raw format to Xarray

        Read all files for each section and write an Xarr using
        the Zarr backend.

        Parameters
        ----------
            :param stpt: StptRaw instance to be converted to zarr
            :param output: Output zarr filepath
            :param nparallel: number of units/sections to run in parallel
            :param nsections: limit conversion on a specified number of sections (for debugging purposes)
        """
    # reset existing data
    ds = xr.Dataset()
    try:
        cds = xr.open_zarr(output)
        sections_done = list(cds)
    except Exception:
        sections_done = []
        reset = True

    if reset:
        ds.to_zarr(output, mode='w')

    # filter out missing sections
    sections = [s for s in stpt.sections if (not s.missing) and (f"S{s.num:03d}" not in sections_done)]
    if nsections != 0:
        sections = sections[:nsections]

    # infer source data type
    dtype = _infer_data_type(sections)

    # submit job for each section
    client = Client.current()
    j = nparallel if len(sections) > nparallel else len(sections)
    func = partial(_write_dataset, output=output, dtype=dtype)
    futures = client.map(func, sections[:j])

    # wait for futures to complete
    seq = as_completed(futures)
    for fut in seq:
        if not fut.exception():
            logger.info('Converted {}'.format(str(fut.result())))
            fut.cancel()
            if j < len(sections):  # submit new jobs if there are more sections
                fut = client.submit(func, sections[j])
                seq.add(fut)
                j += 1
        else:
            logger.error(str(fut.exception()))
            tb = fut.traceback()
            logger.error(traceback.format_tb(tb))

    # assign raw metadata to root attrs
    meta = {
        "scan_type": "STPT",
        "run_code": stpt.code,
        "run_name": stpt.name,
        "missing_sections": [x.num for x in stpt.sections if x.missing],
        "raw_meta": json.loads(json.dumps(stpt.meta, default=str)),
        "date": datetime.datetime.now().isoformat(),
    }
    ds = zarr.open(f"{output}", mode="a")
    ds.attrs.update(meta)


def stpt2zarr(input_path, output_path, append_name=True, local_cluster=True):
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise Exception(f'Input path {input_path} does not exist')
    elif not input_path.is_dir():
        raise Exception(f'Input path {input_path} is not a directory')
    elif not output_path.exists():
        raise Exception(f'Output path {output_path} does not exist')

    stpt = StptRaw(input_path)
    stpt.parse()
    # assign output filename based on STPT code
    if append_name:
        output_fn = Path(output_path).joinpath('{}'.format(stpt.name))
    else:
        output_fn = output_path
    if local_cluster:
        with closing(LocalCluster(processes=False, dashboard_address=None)) as cluster:
            Client(cluster)
            convert2zarr(stpt, output_fn, nparallel=1)
    else:
        convert2zarr(stpt, output_fn, nparallel=1)

    # copy the additional metadata
    settings_actual_path = input_path.joinpath('Settings_actual')
    if settings_actual_path.exists():
        shutil.copytree(settings_actual_path, output_fn.joinpath('Settings_actual'), dirs_exist_ok=True)

    return f"{output_fn}"


@click.command()
@click.argument('input_path')
@click.argument('output_path')
def main(input_path, output_path):
    try:
        stpt2zarr(input_path, output_path)
    except Exception as err:
        logger.error('Error: {}'.format(str(err)))
        logger.error('Details: {}'.format(traceback.format_exc()))
