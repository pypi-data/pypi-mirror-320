import os
import sys
import argparse
from .check import CHECKER
from .report import report
from .utils import parse_arg

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(
        prog="musa-develop",
        formatter_class=argparse.RawTextHelpFormatter,
        description="A tool for deploying and checking the musa environment.",
    )
    parser.add_argument(
        "-c",
        "--check",
        nargs="?",
        const="driver",
        default="",
        choices=[
            "host",
            "driver",
            "mtlink",
            "ib",
            "smartio",
            "container_toolkit",
            "torch_musa",
            "musa",
            "vllm",
            None,
        ],
        dest="check",
        help="""check musa develop environment. Default value is 'driver' if only '-c' or '--check' is set.
optional list: host
               driver
               mtlink
               ib
               smartio
               container_toolkit
               musa
               torch_musa
               vllm""",
    )
    parser.add_argument(
        "--container",
        dest="container",
        type=str,
        default=None,
        help="Check the musa environment in the container.",
    )
    parser.add_argument(
        "-r",
        "--report",
        dest="report",
        action="store_true",
        default=False,
        help="Display the software stack and hardware information of the current environment.",
    )
    parser.add_argument(
        "-d",
        "--download",
        nargs="?",
        type=parse_arg,
        help="""
            choices=[
                "kuae",
                "sdk",
                "mudnn",
                "mccl",
                "driver",
                "smartio",
                "container_toolkit",
                "torch_musa",
            ],
        """,
    )
    parser.add_argument(
        "--dir",
        nargs="?",
        type=str,
        help="""
            download dir
        """,
    )
    parser.add_argument(
        "-i",
        "--install",
        dest="install",
        type=str,
        default="",
        help="Deploy the musa base software stack.",
    )
    parser.add_argument(
        "--force_upgrade_musa",
        dest="force_upgrade_musa",
        action="store_true",
        default=False,
        help="Force update the musa software stack.",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Print verbose",
    )

    # demo
    demo_parser = parser.add_argument_group("Demo Mode")

    demo_parser.add_argument(
        "--demo",
        dest="demo",
        action="store_true",
        default=False,
        help="Enable demo mode and run prebuilt AI project.",
    )

    demo_parser.add_argument(
        "-t",
        "--task",
        dest="task",
        type=str,
        default="",
        help="Specify the task to run (must be used with --demo).",
    )

    demo_parser.add_argument(
        "--ctnr-name",
        dest="ctnr_name",
        type=str,
        default=False,
        help="Specify a contaner name (Optionally, must be used with --demo).",
    )

    demo_parser.add_argument(
        "--host-dir",
        dest="host_dir",
        type=str,
        default=False,
        help="Specify a directory mapping to the container (Optionally, must be used with --demo).",
    )

    # default with no args will print help
    if len(sys.argv) == 1:
        parser.print_help()
        exit()

    args = parser.parse_args()

    if args.container and not args.check:
        parser.error("--container can only be used with -c/--check")

    if args.check:
        checker = CHECKER[args.check](container_name=args.container)
        checker.check()
        checker.report()
        exit()

    if args.report:
        report()
        exit()

    if not args.demo:
        if args.task or args.ctnr_name or args.host_dir:
            parser.error(
                "Error: The --demo option is required to use --task, --ctnr-name, or --host-dir."
            )
            exit()

    if args.demo:
        print("Enter Demo Mode")
        if args.task == "vllm":
            print(f"Task: {args.task}")
        else:
            print(
                f"Without specifying a specific task, start a container runs on MT-GPU. "
            )
        if args.ctnr_name:
            print(f"Container name: {args.ctnr_name}")
        if args.host_dir:
            print(f"Directory on host: {args.host_dir},")
            print("The Directory will mapping to the container: /workspace .")


if __name__ == "__main__":
    main()
