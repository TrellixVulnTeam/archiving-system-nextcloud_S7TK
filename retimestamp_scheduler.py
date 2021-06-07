
from pathlib import Path, PurePath
import sys
from apscheduler.schedulers.blocking import BlockingScheduler


from common.yaml_parser import parse_yaml_config
from task_makers.retimestamping.retimestamping_checker import checker_controller

def raise_system_exit():
    raise SystemExit(
        f"Usage: {sys.argv[0]} (-ho | --hours) <number of hours between checks> (-c | --config) <path to yaml config for Rabbitmq connection>"
        )

    
def parse_arguments(args):
    if not (len(args) == 4):
        raise_system_exit()
    config_path = None
    if args[0] == '-ho' or args[0] == '--hours':
        hours = int(args[1])
    
    if args[2] == '-c' or args[2] == '--config':
        config_path = Path(args[3])

    else: 
        raise_system_exit() 
    return hours, config_path


def run_retimestamping_checker(config, hours):
    scheduler = BlockingScheduler()
    scheduler.add_job(
        func = checker_controller,
        trigger= 'interval',
        args = [config],
        hours = hours
    )
    scheduler.start()

def main():
    """
    Parse args
    -ho  | --hours           how othen will run checking scripts for retimestamping
    -c   | --config          path yaml config for rabbitmq and database -> see common_config_template.yaml
    required options:
    reimestamping_scheduler.py [-ho | --hours ] [-c | --config] 
    """

    hours, config_path = parse_arguments(sys.argv[1:])
    parsed_config = parse_yaml_config(config_path)
    run_retimestamping_checker(parsed_config, hours)

    

if __name__ == '__main__':
    main()




