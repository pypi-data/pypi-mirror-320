import os

import numpy as np
import tifffile
from pathlib import Path


def make_json_serializable(obj):
    """Convert metadata to JSON serializable format."""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    else:
        return obj


def get_metadata(file: os.PathLike | str):
    """
    Extract metadata from a TIFF file. This can be a raw ScanImage TIFF or one
    processed via [lbm_caiman_python.save_as()](#save_as).

    Parameters
    ----------
    file: os.PathLike
        Path to the TIFF file.

    Returns
    -------
    dict
        Metadata extracted from the TIFF file.

    Raises
    ------
    ValueError
        If no metadata is found in the TIFF file. This can occur when the file is not a ScanImage TIFF.
    """
    if not file:
        return None

    tiff_file = tifffile.TiffFile(file)
    if (
            hasattr(tiff_file, 'shaped_metadata')
            and tiff_file.shaped_metadata is not None
            and isinstance(tiff_file.shaped_metadata, (list, tuple))
            and tiff_file.shaped_metadata
            and tiff_file.shaped_metadata[0] not in ([], (), None)
    ):
        if 'image' in tiff_file.shaped_metadata[0]:
            return tiff_file.shaped_metadata[0]['image']

    if hasattr(tiff_file, 'scanimage_metadata'):
        meta = tiff_file.scanimage_metadata
        if meta is None:
            return None

        si = meta.get('FrameData', {})
        if not si:
            print(f"No FrameData found in {file}.")
            return None

        series = tiff_file.series[0]
        pages = tiff_file.pages

        # Extract ROI and imaging metadata
        roi_group = meta["RoiGroups"]["imagingRoiGroup"]["rois"]

        num_rois = len(roi_group)
        num_planes = len(si["SI.hChannels.channelSave"])
        scanfields = roi_group[0]["scanfields"]  # assuming single ROI scanfield configuration

        # ROI metadata
        size_xy = scanfields["sizeXY"]
        num_pixel_xy = scanfields["pixelResolutionXY"]

        # TIFF header-derived metadata
        sample_format = pages[0].dtype.name
        objective_resolution = si["SI.objectiveResolution"]
        frame_rate = si["SI.hRoiManager.scanFrameRate"]

        # Field-of-view calculations
        # TODO: We may want an FOV measure that takes into account contiguous ROIs
        # As of now, this is for a single ROI
        fov_x = round(objective_resolution * size_xy[0])
        fov_y = round(objective_resolution * size_xy[1])
        fov_xy = (fov_x, fov_y / num_rois)

        # Pixel resolution (dxy) calculation
        pixel_resolution = (fov_x / num_pixel_xy[0], fov_y / num_pixel_xy[1])

        return {
            "num_planes": num_planes,
            "num_frames": int(len(pages) / num_planes),
            "fov": fov_xy,  # in microns
            "num_rois": num_rois,
            "frame_rate": frame_rate,
            "pixel_resolution": np.round(pixel_resolution, 2),
            "ndim": series.ndim,
            "dtype": 'uint16',
            "size": series.size,
            "raw_height": pages[0].shape[0],
            "raw_width": pages[0].shape[1],
            "tiff_pages": len(pages),
            "roi_width_px": num_pixel_xy[0],
            "roi_height_px": num_pixel_xy[1],
            "sample_format": sample_format,
            "objective_resolution": objective_resolution,
        }
    else:
        raise ValueError(f"No metadata found in {file}.")


def get_files(
        pathnames: os.PathLike | str | list[os.PathLike | str],
        ext: str = 'tif',
        exclude_pattern: str = '_plane_',
) -> list[os.PathLike | str] | os.PathLike:
    """
    Expands a list of pathname patterns to form a sorted list of absolute filenames.

    Parameters
    ----------
    pathnames: os.PathLike
        Pathname(s) or pathname pattern(s) to read.
    ext: str
        Extention, string giving the filetype extention.
    exclude_pattern: str | list
        A string or list of strings that match to files marked as excluded from processing.

    Returns
    -------
    List[PathLike[AnyStr]]
        List of absolute filenames.
    """
    if '.' in ext or 'tiff' in ext:
        ext = 'tif'  #glob tiff and tif
    if isinstance(pathnames, (list, tuple)):
        out_files = []
        excl_files = []
        for fpath in pathnames:
            if exclude_pattern not in str(fpath):
                if Path(fpath).is_file():
                    out_files.extend([fpath])
                elif Path(fpath).is_dir():
                    fnames = [x for x in Path(fpath).expanduser().glob(f"*{ext}*")]
                    out_files.extend(fnames)
            else:
                excl_files.extend(fpath)
        return sorted(out_files)
    if isinstance(pathnames, (os.PathLike, str)):
        pathnames = Path(pathnames).expanduser()
        if pathnames.is_dir():
            files_with_ext = [x for x in pathnames.glob(f"*{ext}*")]
            return sorted(files_with_ext)
        elif pathnames.is_file():
            if exclude_pattern not in str(pathnames):
                return pathnames
            else:
                raise FileNotFoundError(f"No {ext} files found in directory: {pathnames}")
    else:
        raise ValueError(
            f"Input path should be an iterable list/tuple or PathLike object (string, pathlib.Path), not {pathnames}")


def get_files_ext(base_dir, extension, max_depth) -> list:
    """
    Recursively searches for files with a specific extension up to a given depth and stores their paths in a pickle file.

    Parameters
    ----------
    base_dir : str or Path
        The base directory to start searching.
    extension : str
        The file extension to look for (e.g., '.txt').
    max_depth : int
        The maximum depth of subdirectories to search.

    Returns
    -------
    list
        A list of full file paths matching the given extension.
    """
    base_path = Path(base_dir).expanduser().resolve()
    if not base_path.exists():
        raise FileNotFoundError(f"Directory '{base_path}' does not exist.")
    if not base_path.is_dir():
        raise NotADirectoryError(f"'{base_path}' is not a directory.")

    return [
        str(file)
        for file in base_path.rglob(f'*{extension}')
        if len(file.relative_to(base_path).parts) <= max_depth + 1
    ]


def get_pickle_files(data_path: str | Path) -> list:
    """
    Get all .pickle files in a directory and its subdirectories.
    """
    files = get_files_ext(data_path, '.pickle', 3)
    if not files:
        raise ValueError(f"No .pickle files found in {data_path} or its subdirectories.")
    return files


def get_metrics_path(fname: Path) -> Path:
    """
    Get the path to the computed metrics file for a given data file.
    Assumes the metrics file is to be stored in the same directory as the data file,
    with the same name stem and a '_metrics.npz' suffix.

    Parameters
    ----------
    fname : Path
        The path to the input data file.

    Returns
    -------
    metrics_path : Path
        The path to the computed metrics file.
    """
    fname = Path(fname)
    return fname.with_stem(fname.stem + '_metrics').with_suffix('.npz')
