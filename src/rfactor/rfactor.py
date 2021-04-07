from subprocess import check_call
import os
from pathlib import Path


def compute_rfactor(rainfall_inputdata_folder, results_folder, engine="matlab", debug=False):
    """Compute the R-factor

    Parameters
    ----------
    rainfall_inputdata_folder: pathlib.Path
        Folder path to directory holding rainfall data. Rainfall data are
        stored in separate *.txt files per station and year. For the format of
        the `txt`-files, see :func:`rfactor.rfactor.load_rainfall_data`
    results_folder: str or pathlib.path
        Folder path to write results to.
    engine: 'matlab' or 'python'
        Engine used to compute rfactor.
    debug: optional, default False
        Debug flag to leave matlab open.
    """
    results_folder = Path(results_folder)
    if not results_folder.exists():
        results_folder.mkdir()
    if engine not in ["matlab", "python"]:
        msg = f"Either select 'matlab' or 'python' as calculation engine for the rfactor scripts."
        raise IOError(msg)
    if engine == "matlab":
        os.chdir(Path(__file__).parent)

        exitcode="exit;" if debug else ""

        cmd = [
            "matlab",
            "-nodesktop",
            "-r",
            f"main('{str(rainfall_inputdata_folder.resolve())}','{str(results_folder)}');"+exitcode,
        ]
        check_call(cmd)
    else:
        rfactor_python(rainfall_inputdata_folder)


def rfactor_python(rainfall_inputdata_folder):
    """Compute the R-factor with Python (>3.0.0)

    Parameters
    ----------
    rainfall_inputdata_folder: pathlib.Path
        Folder path to directory holding rainfall data. Rainfall data are
        stored in separate *.txt files per station and year. For the format of
        the `txt`-files, see :func:`rfactor.rfactor.load_rainfall_data`
    """

    print("TO DO")
