import os
import json
from pkgutil import extend_path

from .utils import engine_version_match

__path__ = extend_path(__path__, __name__)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def _is_aggregated_model(model: dict):
    return isinstance(model, dict) and 'aggregated' in model.get('value', '').lower()


def _remove_aggregated(models: list):
    values = [
        _remove_aggregated(m) if isinstance(m, list) else m if not _is_aggregated_model(m) else None
        for m in models
    ]
    return list(filter(lambda v: v is not None, values))


def load_config(node_type: str, skip_aggregated_models: bool = False) -> dict:
    """
    Load the configuration associated with the Node Type.

    Parameters
    ----------
    node_type : str
        The Node Type to load configuration. Can be: `Cycle`, `Site`, `ImpactAssessment`.
    skip_aggregated_models : bool
        Include models using aggregated data. Included by default.
    """
    # log warning if version does not match but allow running models
    engine_version_match()

    try:
        with open(os.path.join(CURRENT_DIR, f"{node_type}.json"), 'r') as f:
            config = json.load(f)
        models = config.get('models')
        return config | {'models': _remove_aggregated(models) if skip_aggregated_models else models}
    except FileNotFoundError:
        raise Exception(f"Invalid type {node_type}.")
