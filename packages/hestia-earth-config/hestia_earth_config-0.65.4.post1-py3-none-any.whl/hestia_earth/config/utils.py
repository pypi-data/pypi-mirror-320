from .version import VERSION, engine_version
from .log import logger


def _parse_version(version: str):
    versions = version.split('-')[0].split('.')
    return '.'.join([versions[0], versions[1]])


def engine_version_match():
    try:
        version = _parse_version(engine_version())
        config_version = _parse_version(VERSION)
        match = version == config_version
        if not match:
            logger.warning(f"Models version does not match configuration version. Please install version {version}.")
        return match
    except ModuleNotFoundError:
        logger.warning('No "hestia_earth_models" module found, please install.')
        pass

    return False
