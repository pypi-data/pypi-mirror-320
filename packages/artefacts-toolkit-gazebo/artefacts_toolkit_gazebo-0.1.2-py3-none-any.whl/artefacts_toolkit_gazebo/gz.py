import subprocess
import re
from xml.etree import ElementTree as ET


def get_sim_objects(world_file: str):
    """Get the included objects names and poses in the simulation.
    Returns a list of dict in this format:
    {
        "name": "green_apple"
        "pose": "0.20 0 1.0 0 0 0"
    }
    as well as a dict in this format;
    {
        "green_apple": "0.20 0 1.0 0 0 0",
    }
    """
    objects = []
    try:
        tree = ET.parse(world_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {world_file} not found, check your pathing.")

    root = tree.getroot()
    # Find all model elements
    for model in root.find("world").findall("model"):
        if "name" in model.attrib:
            object = {}
            object["name"] = model.get("name")
            # Check if the model has a 'pose' element and add it to the dictionary
            pose = model.find("pose")
            if pose is not None:
                object["pose"] = pose.text
            objects.append(object)

    objects_positions = {
        obj["name"]: [float(v) for v in obj["pose"].split(" ")[:3]]
        for obj in objects
        if "pose" in obj
    }
    # first one is legacy format for rc0, second one is new convenience format
    return objects, objects_positions


def get_model_location(model_name):
    """
    Function to get the location of a model
    """

    command = ["gz", "model", "-m", model_name, "-p"]

    try:
        result = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result_output = result.stdout.read().decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            "Gazebo not found in the system. Please install / source Gazebo."
        )

    x_variable = 0.0
    y_variable = 0.0
    z_variable = 0.0

    # Extract position data if it exists
    position_pattern = r"\[(.*?)\]"

    # Search for all matching instances of the list pattern in the text
    matches = re.findall(position_pattern, result_output)

    if len(matches) >= 2:
        position = matches[-2]

        # Extract the individual numbers from the matched string
        numbers = re.findall(r"[\d.-]+", position)

        if len(numbers) >= 3:
            x_variable = float(numbers[0])
            y_variable = float(numbers[1])
            z_variable = float(numbers[2])

        else:
            x_variable = 0.0
            y_variable = 0.0
            z_variable = 0.0
    else:
        print("No x, y, or z variables found in the text.")

    return x_variable, y_variable, z_variable


def kill_gazebo():
    """kill the gazebo process. Tested with harmonic"""
    subprocess.run(["pkill", "-f", "gz"])
