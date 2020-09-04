# pylint: skip-file
"""CLI for librtl
"""
import argparse
import os
import sys

from librtl.azdo import AzureDevOpsInteractor

from librtl.__version__ import __version__ as VERSION

class CLI():

    @staticmethod
    def process_globals(arguments):
        if not hasattr(arguments, "token") or arguments.token is None:
            try:
                arguments.token = os.environ["AZDO_TOKEN"]
            except:
                print("No AZDO_TOKEN environment variable provided and no --token argument provided")
                sys.exit(1)

    @staticmethod
    def create_pr(arguments):
        client = AzureDevOpsInteractor(arguments.token)
        client.create_pull_request(arguments.project, arguments.repo, arguments.source, arguments.destination)
        print(f"Created PR successfully from {arguments.source} to {arguments.destination} for {arguments.project}/{arguments.repo}")

    @staticmethod
    def create_thread(arguments):
        client = AzureDevOpsInteractor(arguments.token)
        pullrequest = client.load_pull_request(arguments.project, arguments.repo, arguments.source) 
        if pullrequest is None:
            print("No Pull Request Found.")
            sys.exit(1)
        client.create_thread(arguments.repo, arguments.project, arguments.artifact, pullrequest["pull_request_id"])        
        print(f"Created Thread successfully for {pullrequest['title']}")

def main(args=None):
    parser = argparse.ArgumentParser(description=f"rtlctl v{VERSION}")
    parser.add_argument("--token", default=None, type=str, help="Azure Devops Token to use [default: os.environ['AZDO_TOKEN']]")
    subparsers = parser.add_subparsers()

    create_pr = subparsers.add_parser("create-pr", help="Create an Azure Devops Pull Request for the Route to Live")
    create_pr.add_argument("project", help="Name of Azure Devops Project")
    create_pr.add_argument("repo", help="Name of Azure Devops Repo")
    create_pr.add_argument("source", help="Name of the source branch")
    create_pr.add_argument("--destination", default="develop", type=str, help="Name of the destination branch [default: develop]")
    create_pr.set_defaults(func=CLI.create_pr)

    create_thread = subparsers.add_parser("create-thread", help="Create an Azure Devops Thread for the Route to Live")
    create_thread.add_argument("project", help="Name of Azure Devops Project")
    create_thread.add_argument("repo", help="Name of Azure Devops Repo")
    create_thread.add_argument("source", help="Name of the source branch")
    create_thread.add_argument("artifact", help="Name of Artifact")
    create_thread.set_defaults(func=CLI.create_thread)

    if args is None:
        try:
            args = sys.argv[1:]
        except:
            parser.print_help()
            sys.exit(1)

    arguments = parser.parse_args(args)
    if not hasattr(arguments, "func"):
        parser.print_help()
        sys.exit(1)

    CLI.process_globals(arguments)
    arguments.func(arguments)

if __name__ == "__main__":
    main()
