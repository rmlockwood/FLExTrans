#
#   fttranslator/dotnet
#
#   Ron Lockwood
#   SIL International
#   11/6/26
#
#   Version 3.17 - 11/6/26 - Ron Lockwood
#    Initial version. Starts .NET 8 in this process for the assemblies FTtranslator loads with pythonnet (HCSynthByGloss.dll, FTtranslator.Apertium.dll).
#
#   OVERVIEW (AI generated, then edited)
#
#   Two parts of the offline translator are .NET 8 assemblies loaded into Python with pythonnet rather than run as programs, so their data is read once instead of for every text:
#   HermitCrab synthesis (synthesis.py, HCSynthByGloss.dll) and the Apertium transfer step (transfer.py, FTtranslator.Apertium.dll). A process can start only one .NET runtime, and it has
#   to be CoreCLR, so whichever assembly comes first starts it with its own runtime config (the .runtimeconfig.json beside it) and the other uses it. startDotNet() does that part, and makes the
#   assembly's folder one pythonnet searches for its dependencies; the caller then adds its assembly with clr.AddReference() and imports its classes.
#
#   TRAPS
#
#    - Both assemblies target .NET 8, so either one's runtime config serves both. One built for a newer .NET would need its own runtime started first.
#    - The error messages name the assembly with the description the caller gives, so synthesis.py's read as they did before this file existed.
#
#   CODE STRUCTURE
#
#   startDotNet() is the whole file.
#

import sys
from pathlib import Path

def startDotNet(dllPath, description):
    '''Make sure .NET 8 (CoreCLR) runs in this process, starting it with dllPath's runtime config if nothing has started a runtime yet, and let pythonnet find dllPath's dependencies.
       description names the assembly in the error messages ("the HermitCrab synthesis DLL"). Returns dllPath resolved. Raises RuntimeError saying what went wrong.'''

    dllPath = Path(dllPath).resolve()

    if not dllPath.is_file():

        raise RuntimeError(f"Could not find {description}: {dllPath}")

    try:
        import pythonnet

    except ImportError:

        raise RuntimeError(f"Loading {description} needs pythonnet (pip install pythonnet).")

    # Start .NET 8 with the dll's own runtime config, unless this process already has a runtime; only one can be loaded, and it has to be CoreCLR
    runtimeInfo = pythonnet.get_runtime_info()

    if runtimeInfo is None:

        try:
            pythonnet.load("coreclr", runtime_config=str(dllPath.with_suffix(".runtimeconfig.json")))

        except Exception as e:

            raise RuntimeError(f"Could not start .NET 8 for {description}. Error: {e}")

    elif runtimeInfo.kind != "CoreCLR":

        raise RuntimeError(f"{description[0].upper()}{description[1:]} needs .NET 8, but this process already runs {runtimeInfo.kind}.")

    # pythonnet looks for the assemblies the dll depends on in sys.path's folders
    if str(dllPath.parent) not in sys.path:

        sys.path.append(str(dllPath.parent))

    return dllPath
