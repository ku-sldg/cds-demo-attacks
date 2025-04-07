"""
This is a python script that will either corrupt or repair specific components on the system based upon the command line arguments.
"""

import argparse
import os
import shutil
from typing import Any, Callable

type component_T = str
type component_path_T = str
type good_path_T = str
type bad_path_T = str
type cds_manifest_T = dict[
    component_T,
    tuple[Callable[[], Any], Callable[[], Any]],
]

all_components = [
    "Hardware.Config",
    "Hardware.Behavior",
    "TPM.Config",
    "TPM.Behavior",
    "BootLoader.Config",
    "BootLoader.Behavior",
    "LKIM.Config",
    "LKIM.Behavior",
    "Kernel.Config",
    "Kernel.Behavior",
    "IMA.Config",
    "IMA.Behavior",
    "SELinux.Config",
    "SELinux.Behavior",
    "AM.Conifg",
    "AM.Behavior",
    "ASP.Config",
    "ASP.Behavior",
    "CDS.Config",
    "CDS.Behavior",
]

corruptible_components = [
    "TPM.Config",
    "BootLoader.Config",
    "LKIM.Config",
    "Kernel.Config",
    "Kernel.Behavior",
    "IMA.Config",
    "IMA.Behavior",
    "SELinux.Config",
    "SELinux.Behavior",
    "AM.Conifg",
    "AM.Behavior",
    "ASP.Config",
    "ASP.Behavior",
    "CDS.Config",
    "CDS.Behavior",
]


def corrupt_component(
    component: component_T, path: component_path_T, bad_path: bad_path_T
) -> None:
    """
    Corrupt a component by copying a bad path to the component path.
    """
    print(f"Corrupting {component} at {path} with {bad_path}")
    # first check that the bad_path exists
    if not os.path.exists(bad_path):
        raise Exception(f"Bad path {bad_path} does not exist")
    # then check that the component path exists
    if not os.path.exists(path):
        raise Exception(f"Component path {path} does not exist")
    # replace the component at component path with the bad path
    os.remove(path)
    shutil.copy2(bad_path, path)
    print(f"Successfully Corrupted {component} at {path} with {bad_path}")


def repair_component(
    component: component_T, path: component_path_T, good_path: good_path_T
) -> None:
    """
    Repair a component by copying a good path to the component path.
    """
    print(f"Repairing {component} at {path} with {good_path}")
    # first check that the good_path exists
    if not os.path.exists(good_path):
        raise Exception(f"Good path {good_path} does not exist")
    # then check that the component path exists
    if not os.path.exists(path):
        raise Exception(f"Component path {path} does not exist")
    # replace the component at component path with the good path
    os.remove(path)
    shutil.copy2(good_path, path)
    print(f"Successfully Repaired {component} at {path} with {good_path}")


script_dir = os.path.dirname(os.path.abspath(__file__))
GOOD_FILE_DIR = os.path.join(script_dir, "good_files")
BAD_FILE_DIR = os.path.join(script_dir, "bad_files")
# Get some environment variables
DEMO_ROOT = os.environ.get("DEMO_ROOT")
if DEMO_ROOT is None:
    raise Exception("DEMO_ROOT environment variable not set")
ASP_BIN = os.environ.get("ASP_BIN")
if ASP_BIN is None:
    raise Exception("ASP_BIN environment variable not set")
AM_ROOT = os.environ.get("AM_ROOT")
if AM_ROOT is None:
    raise Exception("AM_ROOT environment variable not set")

manifest: cds_manifest_T = {
    "CDS.Config": (
        (
            lambda: corrupt_component(
                "CDS.Config",
                f"{DEMO_ROOT}/cds_config/rewrite_one_config.json",
                f"{BAD_FILE_DIR}/rewrite_one_config.json",
            )
        ),
        (
            lambda: repair_component(
                "CDS.Config",
                f"{DEMO_ROOT}/cds_config/rewrite_one_config.json",
                f"{GOOD_FILE_DIR}/rewrite_one_config.json",
            )
        ),
    ),
    "CDS.Behavior": (
        (
            lambda: corrupt_component(
                "CDS.Behavior",
                f"{DEMO_ROOT}/installed_dir/bin/rewrite_one",
                f"{BAD_FILE_DIR}/rewrite_one",
            )
        ),
        (
            lambda: repair_component(
                "CDS.Behavior",
                f"{DEMO_ROOT}/installed_dir/bin/rewrite_one",
                f"{GOOD_FILE_DIR}/rewrite_one",
            )
        ),
    ),
    "ASP.Behavior": (
        (
            lambda: corrupt_component(
                "ASP.Behavior",
                f"{ASP_BIN}/readfile",
                f"{BAD_FILE_DIR}/readfile",
            )
        ),
        (
            lambda: (
                # navigate the the asp-libs directory "~/asp-libs"
                os.chdir(
                    os.path.join(
                        os.path.expanduser("~"),
                        "asp-libs",
                    )
                ),
                # run the `make all` command
                print("Running make all"),
                os.system("make all"),
                # sign it with IMA
                print("Resigning the ASP"),
                os.system(
                    f"sudo evmctl ima_sign {ASP_BIN}/readfile -k ~/custom_ima.priv"
                ),
            )
        ),
    ),
    "AM.Behavior": (
        (
            lambda: corrupt_component(
                "AM.Behavior",
                f"{AM_ROOT}/bin/attestation_manager",
                f"{BAD_FILE_DIR}/attestation_manager",
            )
        ),
        (
            lambda: (
                # navigate the the am-root directory
                os.chdir(AM_ROOT + "/tests"),  # type: ignore
                # run the `make all` command
                print("Running make ci_build"),
                os.system("make ci_build"),
                # sign it with IMA
                print("Resigning the Attestation Manager"),
                os.system(
                    f"sudo evmctl ima_sign {AM_ROOT}/bin/attestation_manager -k ~/custom_ima.priv"
                ),
            )
        ),
    ),
    "SELinux.Config": (
        (
            lambda: (
                # first we remove the selinux "demo_pipeline" module
                os.system(f"sudo semodule --remove=demo_pipeline"),
            )
        ),
        (
            lambda: (
                # first navigate to the folder where the policy was
                os.chdir(DEMO_ROOT + "/selinux_policy"),  # type: ignore
                # then we load the module
                os.system(f"sudo semodule --install demo_pipeline.pp"),
            )
        ),
    ),
}

for component in corruptible_components:
    if component not in manifest:
        # Here is a component that we do not manage, but also should be manageable!
        print(
            f"Warning: {component} is not in the manifest and is corruptible. Please add an attack for it to the manifest."
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Corrupt or repair specific components on the system."
    )
    parser.add_argument(
        "--mode",
        choices=["corrupt", "repair"],
        help="Specify the mode of operation: corrupt or repair.",
    )
    parser.add_argument(
        "component",
        type=str,
        help="Specific component to corrupt or repair. Options: CDS.Config, CDS.Behavior, etc.",
    )
    args = parser.parse_args()
    component = args.component
    if args.component not in manifest:
        print(f"Component {args.component} not found in manifest.")
        print("Available components are:")
        for comp in manifest.keys():
            print(f"  {comp}")
        exit(1)
    (corrupt_fn, repair_fn) = manifest[component]
    match args.mode:
        case "corrupt":
            corrupt_fn()
        case "repair":
            repair_fn()
