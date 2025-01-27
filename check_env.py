import subprocess
from pyflink.common import Configuration
from pyflink.datastream import StreamExecutionEnvironment

import os
import subprocess

def check_env():
    result = subprocess.check_output(["pip", "install", "/flink/usrlib"])
    return result.decode("utf-8")

config = Configuration()
env = StreamExecutionEnvironment.get_execution_environment(config)
env.from_collection(["Check"]).map(lambda _: check_env()).print()
env.execute("Check Environment")