from hestia_earth.config.utils import engine_version_match


def test_engine_version_match():
    assert engine_version_match() is True
