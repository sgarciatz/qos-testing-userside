#!/usr/bin/env python3
import argparse
import os
import sqlite3
import json
from Experiment import Experiment
from pathlib import Path

from pprint import pprint

def parse_arguments():

    """ Parse the CLI arguments """

    args_parser = argparse.ArgumentParser(
        description= ("Perform HTTP requests to test QoS metrics.\n"
        
                      "The parameters of the experiment should be specified "
                      "in a JSON file with the following format:\n"
                      "\n\n{\n"
                      "    \t\"experiment_name\": \"<name>\",\n"
                      "    \t\"experiment_description\": \"<description>\",\n"
                      "    \t\"server_ip\": \"<ip>\",\n"
                      "    \t\"server_port\": \"<port>\",\n"
                      "    \t\"method\": \"<method>\",\n"
                      "    \t\"payload_size\": <payload_size>,\n"
                      "    \t\"n_requests\": <payload_size>,\n"
                      "}\n"
                       ),
        formatter_class=argparse.RawTextHelpFormatter)
    args_parser.add_argument("input_file",
                             metavar="S",
                             type=str,
                             help="Input file")
    args_parser.add_argument("--results",
                             action=argparse.BooleanOptionalAction,
                             help="Do not execute, only see previous results")
    args = args_parser.parse_args()
    return args

def main(args):

    """ Main entry point of the app """

    input_file = json.load(open(args.input_file))
    should_execute = not args.results
    
    print(should_execute)
    # Create a new Experiment
    if (not Path("../database").is_dir()):
        Path.mkdir(Path("../database"))
        
    db_conn = sqlite3.connect("../database/info_Experiments.db")
    experiment = Experiment(input_file["experiment_name"],
                            input_file["experiment_description"],
                            db_conn)

    # Execute Experiment
    if (should_execute):
        experiment.create_experiment()
        experiment.execute_experiment(input_file["server_ip"],
                                      input_file["server_port"],
                                      input_file["method"],
                                      input_file["payload_size"],
                                      input_file["n_requests"])
    # See Experiment Results
    experiment.show_results()
    

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main(parse_arguments())
