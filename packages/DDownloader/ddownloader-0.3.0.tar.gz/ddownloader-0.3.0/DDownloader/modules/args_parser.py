import argparse
from colorama import Fore, Style

def parse_arguments():
    """Parse and return command-line arguments."""
    # Create the ArgumentParser with a custom usage and help message
    parser = argparse.ArgumentParser(
        add_help=False,  # Disable default help
        usage=f"""{Fore.CYAN}Usage:{Style.RESET_ALL}
  script.py {Fore.YELLOW}-u{Style.RESET_ALL} <manifest_url> {Fore.YELLOW}-o{Style.RESET_ALL} <output_name> [{Fore.YELLOW}-p{Style.RESET_ALL} <proxy>] [{Fore.YELLOW}-k{Style.RESET_ALL} <key>] [{Fore.YELLOW}-h{Style.RESET_ALL} <header>]"""
    )

    # Add arguments (no default descriptions, suppress help visibility)
    parser.add_argument(
        "-u", "--url",
        required=True,
        help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-p", "--proxy",
        help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-k", "--key",
        action="append",  # Allow multiple keys
        help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-h", "--header",
        action="append",  # Allow multiple headers
        help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-?", "--help",
        action="help",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate mandatory arguments
    if not args.url:
        print(f"{Fore.RED}Error: The URL (-u) is required.{Style.RESET_ALL}")
        parser.print_usage()
        exit(1)
    if not args.output:
        print(f"{Fore.RED}Error: The output (-o) is required.{Style.RESET_ALL}")
        parser.print_usage()
        exit(1)

    return args