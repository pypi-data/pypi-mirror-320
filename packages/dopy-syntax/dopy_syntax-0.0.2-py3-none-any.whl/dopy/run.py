from pathlib import Path
import tempfile
import importlib.util
import sys
import shutil
from typing import Union

from dopy.transpiler import process_with_imports
from dopy.transpiler.collector import DopyImportCollector
from dopy.transpiler.processor import DopyProcessor


def run_module(module_path: str):
    """Run a Python module dynamically from a file path."""
    # Convert module path to module name (e.g., './foo.py' -> 'foo')
    module_name = Path(module_path).stem

    # Create and load the module spec
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)

    # Add module to sys.modules
    sys.modules[module_name] = module

    # Execute the module
    spec.loader.exec_module(module)


def run_with_files(main_module: Union[str, Path], project_root: Path = None) -> None:
    """
    Run Dopy code while preserving the transpiled Python files in their original directory structure.

    Args:
        dopy: Instance of Dopy class for code preprocessing (not used, kept for API compatibility)
        main_module: Path to the main .dopy file to execute
        project_root: Optional root directory for resolving imports
    """
    main_module = Path(main_module)
    if project_root is None:
        project_root = main_module.parent

    # Use existing transpiler functionality
    success = process_with_imports(str(main_module), project_root)
    if not success:
        raise ValueError(f"Failed to process {main_module} and its dependencies")

    # Run the processed module
    main_module_py = main_module.with_suffix(".py")
    if main_module_py.exists():
        run_module(str(main_module_py))
    else:
        raise ValueError(f"Main module {main_module} was not successfully processed")


def run_without_files(main_module: Union[str, Path], project_root: Path = None) -> None:
    """
    Run Dopy code without creating permanent files by using a temporary directory.

    Args:
        dopy: Instance of Dopy class for code preprocessing (not used, kept for API compatibility)
        main_module: Path to the main .dopy file to execute
        project_root: Optional root directory for resolving imports
    """
    main_module = Path(main_module)
    if project_root is None:
        project_root = main_module.parent

    # Create temporary directory
    temp_dir = None
    try:
        temp_dir = Path(tempfile.mkdtemp())

        # Collect all dependencies using existing collector
        collector = DopyImportCollector(project_root)
        all_files = collector.collect_all_imports(main_module)

        # Copy files to temp directory preserving structure
        temp_files = set()
        for file_path in all_files:
            rel_path = file_path.relative_to(project_root)
            temp_path = temp_dir / rel_path
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, temp_path)
            temp_files.add(temp_path)

        # Get temp main module path
        temp_main = temp_dir / main_module.relative_to(project_root)

        # Process all files using existing processor
        processor = DopyProcessor()
        if not processor.process_all(temp_files):
            raise ValueError("Failed to process one or more files")

        # Run the processed module
        temp_main_py = temp_main.with_suffix(".py")
        if temp_main_py.exists():
            run_module(str(temp_main_py))
        else:
            raise ValueError(f"Main module {temp_main} was not successfully processed")

    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)
