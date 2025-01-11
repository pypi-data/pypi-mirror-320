import os
import re
import logging
import coloredlogs
import time
from pathlib import Path
from colorama import Fore, Style
from DDownloader.modules.helper import download_binaries, detect_platform
from DDownloader.modules.args_parser import parse_arguments
from DDownloader.modules.banners import clear_and_print
from DDownloader.modules.dash_downloader import DASH
from DDownloader.modules.hls_downloader import HLS

# Setup logger
logger = logging.getLogger("+ DDOWNLOADER + ")
coloredlogs.install(level='DEBUG', logger=logger)

def validate_directories():
    """Ensure necessary directories exist."""
    downloads_dir = 'downloads'
    try:
        os.makedirs(downloads_dir, exist_ok=True)
        # logger.debug(f"Validated existence of directory: '{downloads_dir}'.")
    except Exception as e:
        logger.error(f"Failed to create or validate downloads directory: {e}")
        exit(1)

def display_help():
    """Display custom help message with emoji."""
    print(
        f"{Fore.WHITE}+" + "=" * 100 + f"+{Style.RESET_ALL}\n"
        f"{Fore.CYAN}{'Option':<40}{'Description':<90}{Style.RESET_ALL}\n"
        f"{Fore.WHITE}+" + "=" * 100 + f"+{Style.RESET_ALL}\n"
        f"  {Fore.GREEN}-u, --url{' ' * 22}{Style.RESET_ALL}URL of the manifest (mpd/m3u8) 🌐\n"
        f"  {Fore.GREEN}-p, --proxy{' ' * 20}{Style.RESET_ALL}A proxy with protocol (http://ip:port) 🌍\n"
        f"  {Fore.GREEN}-o, --output{' ' * 19}{Style.RESET_ALL}Name of the output file 💾\n"
        f"  {Fore.GREEN}-k, --key{' ' * 22}{Style.RESET_ALL}Decryption key in KID:KEY format 🔑\n"
        f"  {Fore.GREEN}-h, --header{' ' * 19}{Style.RESET_ALL}Custom HTTP headers (e.g., User-Agent: value) 📋\n"
        f"  {Fore.GREEN}-?, --help{' ' * 21}{Style.RESET_ALL}Show this help message and exit ❓\n"
        f"{Fore.WHITE}+" + "=" * 100 + f"+{Style.RESET_ALL}\n"
    )

def main():
    """Main entry point for the downloader."""
    clear_and_print()
    platform_name = detect_platform()
    if platform_name == 'Unknown':
        logger.error(f"Unsupported platform: {platform_name}")
        exit(1)
        
    logger.info(f"Running on platform: {platform_name}")
    time.sleep(1)
    
    logger.info(f"Downloading binaries... Please wait!\n")
    bin_dir = Path(__file__).resolve().parent / "bin"
    download_binaries(bin_dir, platform_name)
    
    time.sleep(1)
    logger.info(f"{Fore.GREEN}Downloading completed! Bye!{Fore.RESET}")
    clear_and_print()

    validate_directories()

    # Parse arguments
    try:
        args = parse_arguments()
    except SystemExit:
        display_help()
        exit(1)

    # Detect and initialize appropriate downloader
    downloader = None
    if re.search(r"\.mpd\b", args.url, re.IGNORECASE):
        logger.info("DASH stream detected. Initializing DASH downloader...")
        downloader = DASH()
    elif re.search(r"\.m3u8\b", args.url, re.IGNORECASE):
        logger.info("HLS stream detected. Initializing HLS downloader...")
        downloader = HLS()
    else:
        logger.error("Unsupported URL format. Please provide a valid DASH (.mpd) or HLS (.m3u8) URL.")
        exit(1)

    # Configure downloader
    downloader.manifest_url = args.url
    downloader.output_name = args.output
    downloader.decryption_keys = args.key or []
    downloader.proxy = args.proxy  # Add proxy if provided

    # Add headers if specified
    if hasattr(args, 'header') and args.header:
        downloader.headers = args.header  # Pass headers to downloader
        logger.info("Custom HTTP headers provided:")
        for header in args.header:
            logger.info(f"  --header {header}")
        print(Fore.MAGENTA + "=" * 100 + Fore.RESET)

    # Log provided decryption keys
    if downloader.decryption_keys:
        logger.info("Decryption keys provided:")
        for key in downloader.decryption_keys:
            logger.info(f"  --key {key}")
        print(Fore.MAGENTA + "=" * 100 + Fore.RESET)

    # Execute downloader
    try:
        if isinstance(downloader, DASH):
            downloader.dash_downloader()
        elif isinstance(downloader, HLS):
            downloader.hls_downloader()
    except Exception as e:
        logger.error(f"An error occurred during the download process: {e}")
        exit(1)

if __name__ == "__main__":
    main()
