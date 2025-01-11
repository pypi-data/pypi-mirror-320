import os
import requests
from tqdm import tqdm
from colorama import Fore, Style, init
import logging
import coloredlogs
import platform

# Initialize Colorama for Windows compatibility
init(autoreset=True)

# Logger setup
logger = logging.getLogger(Fore.GREEN + "+ HELPER + ")
coloredlogs.install(level='DEBUG', logger=logger)

# Binaries with platform-specific handling
binaries = {
    "Windows": [
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/N_m3u8DL-RE.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/ffmpeg.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/aria2c.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/mp4decrypt.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/shaka-packager.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/yt-dlp.exe",
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/mkvmerge.exe"
    ],
    "Linux": [
        "https://github.com/ThatNotEasy/DDownloader/raw/refs/heads/main/DDownloader/bin/N_m3u8DL-RE"
    ]
}

def download_binaries(bin_dir, platform_name):
    """
    Downloads platform-specific binaries to the specified directory.
    """
    os.makedirs(bin_dir, exist_ok=True)
    logger.info(f"Platform detected: {platform_name}")
    logger.info(f"Using binary directory: {bin_dir}")
    
    platform_binaries = binaries.get(platform_name, [])
    
    if not platform_binaries:
        logger.error(f"No binaries available for platform: {platform_name}")
        return

    for binary_url in platform_binaries:
        try:
            filename = binary_url.split("/")[-1]
            filepath = os.path.join(bin_dir, filename)

            if os.path.exists(filepath):
                logger.info(f"{Style.BRIGHT}{Fore.YELLOW}Skipping {filename} (already exists).")
                continue

            logger.info(f"{Fore.GREEN}Downloading {Fore.WHITE}{filename}...{Fore.RESET}")
            response = requests.get(binary_url, stream=True, timeout=30)
            response.raise_for_status()

            # Total size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            with open(filepath, "wb") as file, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=f"{Fore.CYAN}{filename}{Fore.RESET}",
                dynamic_ncols=True,
                bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{rate_fmt}]"
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    progress_bar.update(len(chunk))

            # logger.info(f"{Fore.GREEN}Downloaded and saved: {filepath}{Fore.RESET}")
            # Make binary executable on Linux
            if platform_name == "Linux":
                os.chmod(filepath, 0o755)
        except requests.exceptions.RequestException as e:
            logger.error(f"{Fore.RED}Failed to download {binary_url}: {e}{Fore.RESET}")
        except Exception as e:
            logger.error(f"{Fore.RED}Unexpected error for {binary_url}: {e}{Fore.RESET}")

def detect_platform():
    """
    Detects the current operating system platform.
    """
    system_platform = platform.system().lower()
    if system_platform == 'windows':
        return 'Windows'
    elif system_platform == 'linux':
        return 'Linux'
    elif system_platform == 'darwin':
        return 'MacOS'
    else:
        return 'Unknown'