import argparse as arg
import os
import subprocess
from .log_usage import get_device_usage_page

def bmcompiler_parser():
    parser = arg.ArgumentParser(description     = "SILK2 Profile Tools",
                                formatter_class = arg.ArgumentDefaultsHelpFormatter,
                                prog            = "python -m SILK2.Tools.profile")
    required_group = parser.add_argument_group("required", "required parameters for compilation")
    required_group.add_argument("--get_info", help="Increase output verbosity", action="store_true")
    required_group.add_argument("--logfile",
                                type    = str,
                                help    = "log file name")
    required_group.add_argument("--looptime",
                            type    = str,
                            help    = "Log collection interval(s)")

    return parser
if __name__ == "__main__":
    parser = bmcompiler_parser()
    a = parser.parse_args()
    if a.get_info:
        current_folder = os.path.dirname(os.path.abspath(__file__))
        get_info_name = os.path.join(current_folder,"get_info.sh")
        with open(get_info_name,"+r") as fp:
            lines=fp.readlines()
            for line in lines:
                if line.find("GET_INFO_VERSION") >= 0:
                    ger_info_version = line.split("\"")[-2]
                    print("get_info VERSION: {}".format(ger_info_version))
                    break
        try:
            if a.looptime is None:
                print("Start run: get_info!")
                result = subprocess.run(['sudo', 'bash', get_info_name ], check=True)
            elif a.logfile is None:
                print("Please set logfile use [--logfile LOGFILE] ")
            else:
                print("Start record: get_info!")
                result = subprocess.run(['sudo', 'bash', get_info_name, 'server',  a.logfile, a.looptime, 'y'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code: {e.returncode}")
    elif a.logfile is not None:
        full_name = os.path.basename(a.logfile)
        # 去掉文件后缀（.log）
        task_name = os.path.splitext(full_name)[0]
        get_device_usage_page(a.logfile, task_name)
    else:
        print("python3 -m SILK2.Tools.profile [-h] [--get_info] [--logfile LOGFILE] [--looptime LOOPTIME]")
