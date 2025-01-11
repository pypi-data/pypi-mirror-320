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
logger = logging.getLogger("+ MAIN + ")
coloredlogs.install(level='DEBUG', logger=logger)

def validate_directories():
    downloads_dir = 'downloads'
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
        # logger.debug(f"Created '{downloads_dir}' directory.")

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
        f"  {Fore.GREEN}-H, --header{' ' * 19}{Style.RESET_ALL}Custom HTTP headers (e.g., User-Agent: value) 📋\n"
        f"  {Fore.GREEN}-h, --help{' ' * 21}{Style.RESET_ALL}Show this help message and exit ❓\n"
        f"{Fore.WHITE}+" + "=" * 100 + f"+{Style.RESET_ALL}\n"
    )

def main():
    clear_and_print()
    platform_name = detect_platform()
    logger.info(f"Downloading binaries... Please wait!")
    print(Fore.MAGENTA + "=" * 100 + Fore.RESET)
    time.sleep(1)
    bin_dir = Path(__file__).resolve().parent / "bin"
    download_binaries(bin_dir, platform_name)
    clear_and_print()

    validate_directories()
    try:
        args = parse_arguments()
    except SystemExit:
        display_help()
        exit(1)

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
    downloader.headers = args.header or []
    downloader.proxy = args.proxy  # Add proxy if provided
    
    if downloader.proxy:
        print(Fore.MAGENTA + "=" * 100 + Fore.RESET)
        if not downloader.proxy.startswith("http://"):
            downloader.proxy = f"http://{downloader.proxy}"
            logger.info(f"Proxy: {downloader.proxy}")
            print(Fore.MAGENTA + "=" * 100 + Fore.RESET)
            
    # Log provided headers
    if downloader.headers:
        print(Fore.MAGENTA + "=" * 100 + Fore.RESET)
        logger.info("Headers provided:")
        for header in downloader.headers:
            logger.info(f"  -H {header}")
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