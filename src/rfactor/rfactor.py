import multiprocessing as mp
import os
from pathlib import Path
from subprocess import check_call

import numpy as np
from dotenv import find_dotenv, load_dotenv
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map


def compute_rfactor(
    rainfall_inputdata_folder, results_folder, engine="matlab", debug=False, ncpu=-1
):
    """Compute the R-factor

    Parameters
    ----------
    rainfall_inputdata_folder: pathlib.Path
        Folder path to directory holding rainfall data. Rainfall data are
        stored in separate .txt files per station and year. For the format of
        the `txt`-files, see :func:`rfactor.process.load_rainfall_data`
    results_folder: str or pathlib.path
        Folder path to write results to.
    engine: 'matlab' or 'octave'
        Engine used to compute rfactor.
    debug: bool, default False
        Debug flag to leave matlab open (Matlab engine) / run single core
        (Octave).
    ncpu: int, default -1
        Number of processors to use.

    """
    results_folder = Path(results_folder)
    if not results_folder.exists():
        results_folder.mkdir()
    if not Path(rainfall_inputdata_folder).exists():
        raise IOError(f"Input {rainfall_inputdata_folder}folder does not exist")
    if engine not in ["matlab", "octave"]:
        msg = (
            "Either select 'matlab' or 'octave' as calculation engine "
            "for the rfactor scripts."
        )
        raise IOError(msg)
    if engine == "matlab":
        os.chdir(Path(__file__).parent)

        exitcode = "exit;" if debug else ""

        cmd = [
            "matlab",
            "-nodesktop",
            "-r",
            f"main('{str(rainfall_inputdata_folder.resolve())}',"
            f"'{str(results_folder)}');" + exitcode,
        ]
        check_call(cmd)
    else:
        rfactor_octave(
            Path(rainfall_inputdata_folder), results_folder, debug, ncpu=ncpu
        )


def rfactor_octave(rainfall_inputdata_folder, results_folder, debug=False, ncpu=-1):
    """Compute R-factor with octave engine

    The octave engine is slow, therefore multiprocessing is used as a way to
    speed up execution.

    Parameters
    ----------
    rainfall_inputdata_folder: pathlib.Path
        See :func:`rfactor.rfactor.compute_rfactor`
    results_folder: str or pathlib.path
        See :func:`rfactor.rfactor.compute_rfactor`
    debug: bool, default False
        Run single cores
    ncpu: int, default -1
        See :func:`rfactor.rfactor.compute_rfactor`
    """
    if not Path(rainfall_inputdata_folder).exists():
        msg = f"Input folder '{rainfall_inputdata_folder}' does not exist"
        raise IOError(msg)
    if debug:
        files = [file for file in rainfall_inputdata_folder.iterdir()]
        for file in tqdm(files, total=len(files)):
            print(file)
            single_file([file, results_folder])
    else:
        lst_input = [
            [file, results_folder] for file in rainfall_inputdata_folder.iterdir()
        ]
        if ncpu == -1:
            ncpu = mp.cpu_count()
        process_map(single_file, lst_input, max_workers=ncpu)


def single_file(lst_inputs):
    """Compute R-factor based on a single file.

    This function uses Octave to compute the matlab `core.m` function, using
    one input file as function input.

    Parameters
    ----------
    lst_inputs: list
        List of inputs
    """
    filename = lst_inputs[0]
    path_results = lst_inputs[1]

    check_oct()
    from oct2py import Oct2Py, Oct2PyError

    year = filename.stem.split("_")[1]
    inputdata = np.loadtxt(str(filename.resolve()))

    with Oct2Py() as oc:
        try:
            oc.addpath(str(Path(__file__).parent.resolve()))
            cumEI = oc.core(year, inputdata)
            filename_out = path_results / (filename.stem + "new cumdistr salles.txt")
            np.savetxt(filename_out, cumEI.T, "%.3f %.2f %.1f")
            oc.exit()
        except Oct2PyError as e:
            raise SystemError(e)


def check_oct():
    """Check octave installation"""
    load_dotenv(find_dotenv())
    try:
        oct_exe = Path(os.environ.get("OCTAVE_EXECUTABLE"))
        if not Path(oct_exe).exists():
            raise SystemError(
                "Octave is not referred to correctly in the 'rfactor/.env'-file. "
                "Please check the executable path. "
            )
    except SystemError:
        raise SystemError(
            "No 'OCTAVE_EXECUTABLE' is defined in 'rfactor/.env'-file. Please check "
            "the documentation for information on installing Octave!"
        )
