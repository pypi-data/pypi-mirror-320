import argparse
import pkg_resources
import logging
import sys
import os.path

from ..model.ea.instance import EAInstance

def main():
    version = pkg_resources.require("ea_model")[0].version

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", required = False, help = "Print debug information", action = "store_true")
    #ap.add_argument("--cfg", required = False, help = "The TOML configuration file.")
    #ap.add_argument("INPUT", help = "The path of Excel.")
    #ap.add_argument("OUTPUT", help = "The path of .")

    args = ap.parse_args()

    logger = logging.getLogger()
    
    formatter = logging.Formatter('[%(levelname)s] : %(message)s')

    stdout_handler = logging.StreamHandler(sys.stderr)
    stdout_handler.setFormatter(formatter)

    #base_path = os.path.dirname(args.OUTPUT)
    base_path = os.path.dirname(".")
    log_file = os.path.join(base_path, 'ea-test.log')

    if os.path.exists(log_file):
        os.remove(log_file)

    if args.verbose:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

    logger.setLevel(logging.DEBUG)

    if args.verbose:
        stdout_handler.setLevel(logging.DEBUG)
    else:
        stdout_handler.setLevel(logging.INFO)

    if args.verbose:
        logger.addHandler(file_handler)
        
    logger.addHandler(stdout_handler)    

    try:
        instance = EAInstance()
        print("Access %s successfully" % instance.getRepository().ConnectionString)
        
    except Exception as e:
        #print(e)
        raise e
