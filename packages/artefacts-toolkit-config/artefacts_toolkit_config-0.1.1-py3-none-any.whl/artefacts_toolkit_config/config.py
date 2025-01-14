import yaml
from .constants import ARTEFACTS_PARAMS_FILE
import os


def get_artefacts_param(param_type, param_name, is_ros=True):
    # TODO: requires artefacts-cli to accept non-ROS parameters
    if not is_ros:
        raise NotImplementedError(
            "Error: Non-ROS parameters are not yet supported. Exiting..."
        )

    with open(ARTEFACTS_PARAMS_FILE, "r") as file:
        try:
            params = yaml.safe_load(file)
            param = params[param_type]["ros__parameters"][param_name]
            # Ros Launch arguments need to be of type string, so convert if necessary
            if param_type == "launch" and not type(param) == str:
                param = str(param)
            return param
        except KeyError:
            raise KeyError(
                f"Error: Unable to find parameter {param_name} of type {param_type} in artefacts.yaml. Exiting..."
            )
        except Exception as e:
            raise RuntimeError(f"Error: {e}. Exiting...")
