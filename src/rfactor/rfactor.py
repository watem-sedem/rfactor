import subprocess
import os
from pathlib import Path


def compute_rfactor(rainfall_inputdata_folder, engine="matlab"):

    if engine not in ["matlab", "python"]:
        msg = f"Either select 'matlab' or 'python' as calculation engine for the rfactor scripts."
        raise IOError(msg)
    if engine == "matlab":
        os.chdir(Path(__file__).parent)
        cmd = ["matlab", "-nodesktop", "-r", f"main('{rainfall_inputdata_folder}')"]
        import pdb

        pdb.set_trace()
        subprocess.call(cmd)
    else:
        rfactor_python(rainfall_inputdata_folder)


def rfactor_python(rainfall_inputdata_folder):

    print("TO DO")
