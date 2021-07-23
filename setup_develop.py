from setuptools import setup, find_packages
from configparser import ConfigParser
from pathlib import Path

setup_cfg_path = Path(__file__).parent/'setup.cfg'
setup_cfg = ConfigParser()
setup_cfg.read(setup_cfg_path)
setup_cfg_metadata = setup_cfg['metadata']
setup_cfg_version = setup_cfg_metadata['version']
dev_version = f'{setup_cfg_version}.dev'
setup_cfg_options = setup_cfg['options']

setup(
    name=setup_cfg_metadata['name'],
    version=dev_version,
    url=setup_cfg_metadata['url'],
    author=setup_cfg_metadata['author'],
    author_email=setup_cfg_metadata['author_email'],
    description=setup_cfg_metadata['description'],
    packages=find_packages(),    
    install_requires=setup_cfg_options['install_requires'],
)
