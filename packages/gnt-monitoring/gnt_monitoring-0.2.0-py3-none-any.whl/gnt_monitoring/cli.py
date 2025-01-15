import asyncio
import json
import sys
import time
from argparse import Namespace
from logging import getLogger

from tabulate import tabulate

from gnt_monitoring._decorators import argument, command
from gnt_monitoring.arguments import base_args
from gnt_monitoring.constants import NAGIOS_STATUS_CODES
from gnt_monitoring.helpers import check_for_status, convert_to_human
from gnt_monitoring.logger import init_logger
from gnt_monitoring.rapi import GntMonitoring, GntRapiAuth
from gnt_monitoring.sentry import Sentry

args = base_args()

subparser = args.add_subparsers(dest="subcommand")
_logger = getLogger(__name__)


async def memory_check(cluster: GntMonitoring, **params) -> None:
    """
    Memory monitoring function
    :param float warning: percentage at which return warning
    :param float critical: percentage at which return critical
    """
    warning = params.pop("warning")
    critical = params.pop("critical")
    monitoring_data = {}
    start = time.perf_counter()
    hosts = await cluster.hosts()
    hosts = [h["id"] for h in hosts]
    for host in hosts:
        host_memory = await cluster.host_memory(host=host)
        host_memory["status"] = check_for_status(
            warning=warning, critical=critical, value=host_memory["allocated_perc"]
        )
        _logger.debug(f"Memory data:\n{json.dumps(host_memory, indent=2)}")
        monitoring_data[host] = host_memory
    end = time.perf_counter()
    exec_time = round(end - start, 2)
    _logger.debug(f"Collecting data took: {exec_time}")
    process_results(monitoring_data)


def init_gnt_monitoring(**kwargs) -> GntMonitoring:
    """
    Function to initialyze ganeti monitoring class
    """
    # warning = kwargs.pop("warning")
    # critical = kwargs.pop("critical")
    rapi_host = kwargs.pop("rapi_host")
    rapi_port = kwargs.pop("rapi_port")
    rapi_scheme = kwargs.pop("rapi_scheme")
    rapi_auth = GntRapiAuth(
        user=kwargs.pop("rapi_user"),
        password=kwargs.pop("rapi_password"),
        netrc=kwargs.pop("netrc_file"),
    )
    return GntMonitoring(
        host=rapi_host, port=rapi_port, scheme=rapi_scheme, auth=rapi_auth
    )


def process_results(data: dict) -> None:
    """
    Process gathered results
    :param dict data: data collected from rapi
    :return: None
    """
    overal_status = max([s["status"] for _, s in data.items()])
    output = [["Host", "Status", "Usage %", "Total", "Allocated", "Used", "Available"]]
    for host, info in data.items():
        host_line = []
        host_line.append(host)
        status_converted = NAGIOS_STATUS_CODES.get(info["status"])
        host_line.append(status_converted)
        host_line.append(info["allocated_perc"])
        total = convert_to_human(info["total"])
        host_line.append(f"{total[0]} {total[1]}")
        allocated = convert_to_human(info["allocated"])
        host_line.append(f"{allocated[0]} {allocated[1]}")
        used = convert_to_human(info["used"])
        host_line.append(f"{used[0]} {used[1]}")
        free = convert_to_human(info["free"])
        host_line.append(f"{free[0]} {free[1]}")
        output.append(host_line)
    print(tabulate(output, tablefmt="simple", headers="firstrow", numalign="center"))
    sys.exit(overal_status)


@command(
    [
        argument(
            "-w",
            "--warning",
            help="Percent value for warning, default: %(default)s",
            default=75,
            type=float,
        ),
        argument(
            "-c",
            "--critical",
            help="Percent value for critical, default: %(default)s",
            default=90,
            type=float,
        ),
    ],
    parent=subparser,  # type: ignore
)
def check(cluster: GntMonitoring, pargs: dict) -> None:
    """
    Main check command
    """
    if pargs["warning"] >= pargs["critical"]:
        _logger.error("Warning value can't be equal or higher then critical")
        sys.exit(5)
    asyncio.run(memory_check(cluster, **pargs))


async def calculate_cluster_memory(cluster: GntMonitoring) -> None:
    """
    Function to calculate total cluster memory
    """


@command(
    [
        argument(
            "-w",
            "--warning",
            help="Warning value for nodes available, default: %(default)s",
            default=1.10,
            type=float,
        ),
        argument(
            "-c",
            "--critical",
            help="Critical value for nodes available, defailt: %(default)s",
            default=1.05,
            type=float,
        ),
    ],
    parent=subparser,  # type: ignore
)
def cluster_memory(cluster: GntMonitoring, pargs: dict) -> None:
    """
    Cli command to calculate total cluster memory
    """
    hosts = asyncio.run(cluster.hosts())
    _logger.debug(json.dumps(hosts, indent=2, default=str))
    results = {
        "total": 0,
        "allocated": 0,
        "used": 0,
        "biggest node": 0,
        "nodes available": 0.0,
        "available": 0,
    }
    results = dict(sorted(results.items()))
    key_length = 0
    for k in results.keys():
        key_length = max(key_length, len(k))
    for h in hosts:
        host = asyncio.run(cluster.host_memory(h["id"]))
        results["biggest node"] = max(results["biggest node"], host["total"])
        results["total"] += host["total"]
        results["allocated"] += host["allocated"]
        results["used"] += host["used"]
    results["available"] = results["total"] - results["allocated"]
    results["nodes available"] = round(
        results["available"] / results["biggest node"], 2
    )
    for k, v in results.items():
        if isinstance(v, int):
            value, unit = convert_to_human(v)
            print(f"{k.capitalize():<{key_length}} : {value} {unit}")
        else:
            print(f"{k.capitalize():<{key_length}} : {v}")
    status = check_for_status(
        warning=-abs(pargs["warning"]),
        critical=-abs(pargs["critical"]),
        value=-abs(results["nodes available"]),
    )
    sys.exit(status)


def main() -> None:
    """
    Tool entry point
    :returns: None
    """
    parsed = args.parse_args()
    init_logger(level=parsed.log_level)

    if parsed.sentry_dsn:
        Sentry(dsn=parsed.sentry_dsn, env=parsed.sentry_env)
    cluster = init_gnt_monitoring(**parsed.__dict__)
    if parsed.subcommand is None:
        asyncio.run(memory_check(cluster=cluster, **parsed.__dict__))
        # args.print_help()
        return
    try:
        parsed.func(cluster, parsed.__dict__)
    except KeyboardInterrupt:
        _logger.debug("Keyboard interrupt")
        sys.exit(4)
