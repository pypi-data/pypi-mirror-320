import pytest
from functools import reduce
import importlib

from hestia_earth.config import load_config


def _flatten(values: list): return list(reduce(lambda x, y: x + (y if isinstance(y, list) else [y]), values, []))


# included in orchestrator
_ignore_models = ['emissions.deleted', 'transformations']
_ignore_values = [None, '', 'all']


def _model_path(model: dict):
    name = model.get('model')
    value = model.get('value')
    suffix = f"hestia_earth.models.{name}"
    return f"{suffix}.{value}" if value not in _ignore_values else suffix


def _get_models_paths(node_type: str):
    models = _flatten(load_config(node_type).get('models', []))
    return [
        _model_path(m)
        for m in models
        if m.get('model') not in _ignore_models
    ]


@pytest.mark.parametrize(
    'node_type',
    ['Cycle', 'Site', 'ImpactAssessment']
)
def test_load_config_cycle(node_type):
    paths = _get_models_paths(node_type)

    for path in paths:
        run = importlib.import_module(path).run
        assert run is not None, path
