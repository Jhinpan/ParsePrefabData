import os
import re


def extract_prefab_data_chunked(file_path):
    exclude_patterns = ["ObjectHighlighter", "Environment_", "BFW180201_", "solid", "glass_", "Wall", "xWalls",
                        "zWalls", "Rooms", "RoomTypes", "Bedroom1", "Bedroom2", "livingroom",
                        "Window", "Environment", "Floor", "CreatedObjects", "CreatedBoxes", "BoxGroup", "visuals",
                        "link_", "midpoint_",
                        "corner_", "faceCenter_", "shadow", "Black_Right_Arrow", "rigRoot"]

    with open(file_path, 'r') as prefab_file:
        content = prefab_file.read()

    # Splitting the content based on "\nGameObject"
    gameobject_chunks = content.split("\nGameObject")[1:]

    # Patterns for extraction
    gameobject_name_pattern = re.compile(r'm_Name: (\w+)')
    local_position_pattern = re.compile(r'm_LocalPosition: {x: (-?\d+\.?\d*), y: (-?\d+\.?\d*), z: (-?\d+\.?\d*)}')
    local_rotation_pattern = re.compile(
        r'm_LocalRotation: {x: (-?\d+\.?\d*), y: (-?\d+\.?\d*), z: (-?\d+\.?\d*), w: (-?\d+\.?\d*)}')
    local_scale_pattern = re.compile(r'm_LocalScale: {x: (-?\d+\.?\d*), y: (-?\d+\.?\d*), z: (-?\d+\.?\d*)}')

    extracted_data = []
    for chunk in gameobject_chunks:
        name = gameobject_name_pattern.search(chunk)
        position = local_position_pattern.search(chunk)
        rotation = local_rotation_pattern.search(chunk)
        scale = local_scale_pattern.search(chunk)

        if name and position and rotation and scale:
            extracted_data.append((name.group(1), position.groups(), rotation.groups(), scale.groups()))

    filtered_data = [item for item in extracted_data if not any(pattern in item[0] for pattern in exclude_patterns)]

    return filtered_data


def parse_directory_for_prefabs_updated(root_directory):
    all_prefab_data = {}

    # Loop through P1 to P14 folders
    for p_index in range(1, 15):  # P1 to P14
        p_folder = os.path.join(root_directory, f'P{p_index}')
        all_prefab_data[f'P{p_index}'] = {}

        # Ensure P folder exists
        if os.path.exists(p_folder):

            # Loop through C1 to C3 folders inside the P folder
            for c_index in range(1, 4):  # C1 to C3
                c_folder = os.path.join(p_folder, f'C{c_index}')
                all_prefab_data[f'P{p_index}'][f'C{c_index}'] = {}

                # Ensure C folder exists
                if os.path.exists(c_folder):

                    # Get all prefab files in the C folder
                    for file in os.listdir(c_folder):
                        if file.startswith("Environment_") and file.endswith(".prefab"):
                            full_path = os.path.join(c_folder, file)
                            e_number = file.split('_')[-1].split('.')[0]  # Extracting the number after "Environment_"
                            all_prefab_data[f'P{p_index}'][f'C{c_index}'][f'E{e_number}'] = extract_prefab_data_chunked(
                                full_path)

    return all_prefab_data


def save_data_to_files(data, save_directory):
    for p_key, p_data in data.items():
        for c_key, c_data in p_data.items():
            for e_key, e_data in c_data.items():
                filename = f"{p_key}{c_key}{e_key}.txt"
                full_path = os.path.join(save_directory, filename)

                # Saving the data
                with open(full_path, 'w') as file:
                    for item in e_data:
                        file.write(str(item) + "\n")


# Set the root_directory variable to the path of your top-level directory
root_directory = r"D:\Creation Results-20230910T173510Z-001\Creation Results"  # replace with your directory path

# Set the save_directory variable to the path where you want to save the output files
save_directory = r"D:\OutputFiles_excluded"  # replace with your desired directory path

# Ensure directory exists or create it
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Run the script and save results
all_data = parse_directory_for_prefabs_updated(root_directory)
save_data_to_files(all_data, save_directory)
