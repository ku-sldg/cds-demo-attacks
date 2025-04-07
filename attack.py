"""
This is a python script that will either corrupt or repair specific components on the system based upon the command line arguments.
"""

import argparse
import os
import shutil

type component_T = str
type component_path_T = str
type good_path_T = str
type bad_path_T = str
type cds_manifest_T = dict[
    component_T, tuple[component_path_T, good_path_T, bad_path_T]
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
good_file_path = os.path.join(script_dir, "good_files")
bad_file_path = os.path.join(script_dir, "bad_files")

manifest: cds_manifest_T = {
    "CDS.Config": (
        f"/path/to/componentA",
        f"{good_file_path}/rewrite_one_config.json",
        f"{bad_file_path}/rewrite_one_config.json",
    ),
    "CDS.Behavior": (
        "/path/to/componentB",
        "/path/to/good/componentB",
        "/path/to/bad/componentB",
    ),
}

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
    (path, good_path, bad_path) = manifest[component]
    match args.mode:
        case "corrupt":
            corrupt_component(component, path, bad_path)
        case "repair":
            repair_component(component, path, good_path)
