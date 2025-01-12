import time
import asyncio
import micropip

def pip_install(package, deps=True):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(micropip.install(package, deps=deps, verbose=True))

def install_pyvista_no_deps():
    pip_install("pyvista", deps=False)
    pip_install("numpy")

def install():
    # TODO: Dynamically lookup the version to mock
    micropip.add_mock_package("vtk", "9.3.1")
    micropip.add_mock_package("vtkmodules", "9.3.1")
    # install_pyvista_no_deps()  # Install PyVista without vtk
    pip_install("pyvista")
    # TODO: Wait until pyvista is importable

if __name__ == "__main__":
    install()
