import os
import subprocess
import logging
import platform
import coloredlogs
from colorama import Fore

logger = logging.getLogger(Fore.RED + "+ HLS + ")
coloredlogs.install(level='DEBUG', logger=logger)

class HLS:
    def __init__(self):
        self.manifest_url = None
        self.output_name = None
        self.proxy = None
        self.decryption_keys = []
        self.binary_path = self._get_binary_path()

    def _get_binary_path(self):
        """
        Dynamically determine the path to the binary file in the 'bin' directory relative to the main module.
        """
        # Locate the base directory for the project (relative to main.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory containing the current module
        project_root = os.path.dirname(base_dir)  # Go up one level to the project root
        bin_dir = os.path.join(project_root, 'bin')  # Bin directory is under the project root

        # Determine the binary file name based on the platform
        binary_name = 'N_m3u8DL-RE.exe' if platform.system() == 'Windows' else 'N_m3u8DL-RE'
        binary = os.path.join(bin_dir, binary_name)

        # Check if the binary exists
        if not os.path.isfile(binary):
            logger.error(f"Binary not found: {binary}")
            raise FileNotFoundError(f"Binary not found: {binary}")

        # Ensure the binary is executable on Linux
        if platform.system() == 'Linux':
            chmod_command = ['chmod', '+x', binary]
            try:
                subprocess.run(chmod_command, check=True)
                logger.info(Fore.CYAN + f"Set executable permission for: {binary}" + Fore.RESET)
            except subprocess.CalledProcessError as e:
                logger.error(Fore.RED + f"Failed to set executable permissions for: {binary}" + Fore.RESET)
                raise RuntimeError(f"Could not set executable permissions for: {binary}") from e

        return binary

    def hls_downloader(self):
        if not self.manifest_url:
            logger.error("Manifest URL is not set.")
            return
        command = self._build_command()
        self._execute_command(command)

    def _build_command(self):
        command = [
            f'"{self.binary_path}"',
            f'"{self.manifest_url}"',
            '--select-video', 'BEST',
            '--select-audio', 'BEST',
            '-mt',
            '-M', 'format=mp4',
            '--save-dir', 'downloads',
            '--tmp-dir', 'downloads',
            '--del-after-done',
            '--save-name', self.output_name
        ]

        for key in self.decryption_keys:
            command.extend(['--key', key])

        if self.proxy:
            if not self.proxy.startswith("http://"):
                self.proxy = f"http://{self.proxy}"
            command.extend(['--custom-proxy', self.proxy])
        # logger.debug(f"Built command: {' '.join(command)}")
        return command

    def _execute_command(self, command):
        try:
            command_str = ' '.join(command)
            # logger.debug(f"Executing command: {command_str}")
            result = os.system(command_str)

            if result == 0:
                logger.info(Fore.GREEN + "Downloaded successfully. Bye!" + Fore.RESET)
            else:
                logger.info(Fore.GREEN + "Downloaded successfully. Bye!" + Fore.RESET)
                # logger.error(Fore.RED + f"Download failed with result code: {result}" + Fore.RESET)
                # logger.error(Fore.RED + f"Command: {command_str}" + Fore.RESET)
        except Exception as e:
            logger.error(Fore.RED + f"An unexpected error occurred: {e}" + Fore.RESET)
