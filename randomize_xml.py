import xml.etree.ElementTree as ET
import os
import random
import pandas as pd

mine_pos = (0, 0)



# Create new Folder
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print("Folder created")
    else:
        print("Folder already exists")

# Read XML file
def read_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    return tree, root

def randomize_mine_box_number():
    random_number_list = []
    random_number_list.append(random.randint(0,1))
    random_number_list.append(random.randint(0,3))


# Randomize position
def randomize_mine_position():
    x_pos = round(random.uniform(-0.01, -0.1), 3)  # Random X position
    y_pos = round(random.uniform(0.11, -0.11), 3)    # Random Y position
    z_pos = 0.275  # Z position remains the same

    global mine_pos

    mine_pos = (x_pos, y_pos)
    return f"{x_pos} {y_pos} {z_pos}"

def randomize_box1_position():
    global mine_pos

    x_pos = round(random.uniform(-0.3, -0.105), 3)  # Random X position
    while(mine_pos[0] - 0.066 < x_pos < mine_pos[0] + 0.066):
        print(mine_pos)
        print(x_pos)
        x_pos = round(random.uniform(-0.3, -0.105), 3)

    
    y_pos = round(random.uniform(-0.11, 0.11), 3)    # Random Y position
    while(mine_pos[1] - 0.075 < y_pos < mine_pos[1] + 0.075):
        y_pos = round(random.uniform(-0.11, 0.11), 3)
    z_pos = 0.03  # Z position remains the same
    return f"{x_pos} {y_pos} {z_pos}"

def randomize_box2_position():
    global mine_pos

    x_pos = round(random.uniform(-0.3, -0.105), 3)  # Random X position
    while(mine_pos[0] - 0.06 < x_pos < mine_pos[0] + 0.06):
        x_pos = round(random.uniform(-0.3, -0.14), 3)
    y_pos = round(random.uniform(-0.11, 0.11), 3)    # Random Y position
    while(mine_pos[1] - 0.08 < y_pos < mine_pos[1] + 0.08):
        y_pos = round(random.uniform(-0.11, 0.11), 3)
    z_pos = 0.03  # Z position remains the same
    return f"{x_pos} {y_pos} {z_pos}"

# Create the folder for output files
create_folder("Testing")

xml_path = "STL_files/Probing_Physics_copy.xml"

# Generate 5 XML files with random positions
for i in range(0, 1000):
    data_dict = {}

    data_dict['X_Axis'] = []
    data_dict['Y_Axis'] = []
    data_dict['Z_Axis'] = []
    
    tree, root = read_xml(xml_path)

    parent = root.findall(".//body")

    for child in parent:
        if len(child.findall(".//geom[@mesh='Mine']")) > 0:
            child.attrib["pos"] = randomize_mine_position()  # Set randomized position
        elif len(child.findall(".//geom[@size='0.02 0.02 0.02']")) > 0:
            child.attrib["pos"] = randomize_box1_position()
        elif len(child.findall(".//geom[@size='0.013 0.03 0.005']")) > 0:
            child.attrib["pos"] = randomize_box2_position()



    # Write the updated XML to a new file
    output_filename = f"XML_files/Probing_{i}.xml"
    tree.write(output_filename)
    print(f"XML file saved as {output_filename}")
    a = mine_pos[0]
    print("a", a)
    b = a - 0.17
    print("b", b)
    c = 0
    #Write csv file for mine position
    data_dict['Y_Axis'].append(mine_pos[1])
    data_dict['X_Axis'].append(b)
    data_dict['Z_Axis'].append(c)
    
    df = pd.DataFrame(data_dict)
    print(df)
    df.to_csv(f'Mine_location/mine_pos_{i}.csv', index=False)

print("All XML files updated and saved successfully.")
