import re
import subprocess
import sys
import time

import requests


def get_repo_package(branch='master', build='lastSuccessfulBuild') -> str:
    """Returns the auto_etp repo module package from our Jenkins given the requested branch and build"""
    source_job = '/job/utils-sources/job/'
    base_url = f'http://autoetp2.jenkins.akamai.com{source_job}{branch}/{build}/'
    url = f'{base_url}api/json?tree=artifacts[*]'
    response = requests.get(url, verify=False)
    response.raise_for_status()
    res_dict = response.json()
    artifacts = res_dict.get('artifacts')
    for i in artifacts:
        match = re.match(r'auto_etp.*tar\.gz', i.get('fileName'))
        if match:
            return f'{base_url}artifact/{i["relativePath"]}'


def install_pip_package_using_pip(package_path):
    """Install pip package """
    print(f'Installing {package_path = }')
    cmd = [sys.executable, "-m", "pip", "install", package_path, "-U"]
    complete_proc = subprocess.run(cmd, check=False)
    if complete_proc.returncode:
        print(f"{' '.join(cmd)} failed with exit code {complete_proc.returncode}.")


def auto_etp_install():
    """Download and install auto_etp repo package to python site packages"""
    install_pip_package_using_pip('requests')
    install_pip_package_using_pip('pybenutils')
    time.sleep(1)
    from pybenutils.network.download_manager import download_url
    repo_package_url = get_repo_package()
    if repo_package_url:
        install_pip_package_using_pip(download_url(repo_package_url))

try:
    from auto_etp.jarvis import main_new_window
except ModuleNotFoundError as ex:
    print(ex)
    auto_etp_install()
finally:
    from auto_etp.jarvis import main_new_window

main_new_window()
