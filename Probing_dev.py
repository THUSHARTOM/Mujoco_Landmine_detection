import mujoco as mj
from mujoco.glfw import glfw
import numpy as np
import os
import pandas as pd
import sys  # Import the sys module
from enum import Enum

# Define states
class State(Enum):
    HORIZONTAL_MOVEMENT = 0
    PROBE_MOVEMENT = 1
    BED_MOVEMENT = 2

# Global variables
count = 0
simend = 300  # Simulation time

# Define the limit for probing
rod_limit = 0.05
positive_force = 1
negative_force = -0.5
force_sensor_limit = 0.24
probe_position_limit = -0.027

Xaxis_position_start = -0.15
probestart = State.HORIZONTAL_MOVEMENT
onetime = True
Xaxis_position = 0

Yaxis_position = 0
Yaxis_position_start = 0.01
Yflag = 0
data_dict = {}
printone = True
onetimeadd = True
flag = 0  # Initialize flag

X_axis_Resolution = 0.01
Y_axis_Resolution = 0.005

# Function to append values to the dictionary
def append_to_dict(data_dict, x_position, y_position, depth, force_value):
    if 'Y_Axis' not in data_dict:
        data_dict['Y_Axis'] = []
    if 'depth_mm' not in data_dict:
        data_dict['depth_mm'] = []
    if 'X_Axis' not in data_dict:
        data_dict['X_Axis'] = []
    if 'pressure_N' not in data_dict:
        data_dict['pressure_N'] = []

    data_dict['Y_Axis'].append(y_position)
    data_dict['depth_mm'].append(depth)
    data_dict['X_Axis'].append(x_position)
    data_dict['pressure_N'].append(force_value)

# Function to initialize the controller
def init_controller(model, data):
    data.ctrl[1] = -0.5
    pass

# Function for controller logic
def controller(model, data):
    state_machine[probestart](model, data)

# Function to find the next incremented filename
def get_next_filename(prefix, directory='.'):
    existing_files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith('.csv')]
    if not existing_files:
        return f"{prefix}_1.csv"
    max_num = max(int(f.split('_')[-1].split('.')[0]) for f in existing_files)
    return f"{prefix}_{max_num + 1}.csv"

# Function to get the current XML file number
def get_current_xml_number(file_path='current_xml_number.txt'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return int(file.read().strip())
    return 1

# Function to update the current XML file number
def update_current_xml_number(current_number, file_path='current_xml_number.txt'):
    with open(file_path, 'w') as file:
        file.write(str(current_number))

# State machine functions
def bed_movement(model, data):
    global count, Yaxis_position_start, probestart, printone, Yflag, onetime, Xaxis_position_start, Yaxis_position

    Yaxis_position = data.qpos[0]

    if count == 50:
        print("Yaxis position", Yaxis_position)
        print("Yaxis position start", Yaxis_position_start)
        count = 0
    count += 1

    if Yaxis_position <= Yaxis_position_start and Yflag == 0:
        Yaxis_position_start += Y_axis_Resolution
        data.ctrl[2] = 0.03
        Yflag = 1
    elif Yaxis_position > Yaxis_position_start and Yflag == 1:
        data.ctrl[2] = 0
        Yaxis_position_start += Y_axis_Resolution
        probestart = State.HORIZONTAL_MOVEMENT
        Yflag = 0
        data.ctrl[1] = -1
        Xaxis_position_start = -0.15

    if Yaxis_position > 0.13 and printone:
        df = pd.DataFrame(data_dict)
        filename_prefix = 'data'
        filepath = get_next_filename(filename_prefix)
        print(f"CSV file saved as {filepath}")
        df.to_csv(filepath, index=False)
        printone = False
        restart_script()

def horizontal_xaxis_movement(model, data):
    global onetimeadd, count, Xaxis_position_start, probestart, flag, onetime, Xaxis_position

    Xaxis_position = data.qpos[1]

    if count == 50:
        count = 0
    count += 1

    if Xaxis_position > Xaxis_position_start and flag == 0:
        flag = 0
    elif Xaxis_position < Xaxis_position_start and flag == 0:
        data.ctrl[1] = 0.5
        flag = 1
        Xaxis_position_start += X_axis_Resolution
    elif Xaxis_position > Xaxis_position_start and flag == 1:
        data.ctrl[1] = 0
        Xaxis_position_start += X_axis_Resolution
        probestart = State.PROBE_MOVEMENT
        flag = 0
        onetime = True
        onetimeadd = True

    if Xaxis_position > 0.15:
        probestart = State.BED_MOVEMENT

def probe_movement(model, data):
    global onetimeadd, count, probe_position_limit, probestart, onetime, Xaxis_position, Yaxis_position

    force_sensor_value = data.sensordata[0]
    probing_position_value = data.qpos[2]

    if count == 50:
        count = 0
    count += 1

    if onetime:
        data.ctrl[0] = positive_force
        onetime = False

    if force_sensor_value > force_sensor_limit:
        data.ctrl[0] = negative_force
        if onetimeadd:
            append_to_dict(data_dict, Xaxis_position, Yaxis_position, probing_position_value, force_sensor_value)
            onetimeadd = False
    elif probing_position_value < probe_position_limit:
        data.ctrl[0] = 0
        probestart = State.HORIZONTAL_MOVEMENT

# Dictionary-based state machine
state_machine = {
    State.HORIZONTAL_MOVEMENT: horizontal_xaxis_movement,
    State.PROBE_MOVEMENT: probe_movement,
    State.BED_MOVEMENT: bed_movement
}

def restart_script():
    print("Restarting script...")
    current_xml_number = get_current_xml_number()
    next_xml_number = current_xml_number + 1
    update_current_xml_number(next_xml_number)
    python = sys.executable
    os.execl(python, python, *sys.argv, str(next_xml_number))

# Get the current XML file number
current_xml_number = get_current_xml_number()
xml_path = f'./XML_files/Probing_{current_xml_number}.xml'

# Get the full path to the XML file
dirname = os.path.dirname(__file__)
abspath = os.path.join(dirname, xml_path)
xml_path = abspath

# MuJoCo data structures
model = mj.MjModel.from_xml_path(xml_path)  # MuJoCo model
data = mj.MjData(model)  # MuJoCo data
cam = mj.MjvCamera()  # Abstract camera
opt = mj.MjvOption()  # Visualization options

# Init GLFW, create window, make OpenGL context current, request v-sync
glfw.init()
window = glfw.create_window(1200, 900, "Demo", None, None)
glfw.make_context_current(window)
glfw.swap_interval(1)

# Initialize visualization data structures
mj.mjv_defaultCamera(cam)
mj.mjv_defaultOption(opt)
scene = mj.MjvScene(model, maxgeom=10000)
context = mj.MjrContext(model, mj.mjtFontScale.mjFONTSCALE_150.value)

# Example on how to set camera configuration
cam.azimuth = 90
cam.elevation = -40
cam.distance = 1.3
cam.lookat = np.array([0.0, 0.0, 0])

# Initialize the controller
init_controller(model, data)

# Set the controller
mj.set_mjcb_control(controller)

while not glfw.window_should_close(window):
    time_prev = data.time

    while (data.time - time_prev < 1.0 / 60.0):
        mj.mj_step(model, data)

    if data.time >= simend:
        break

    # Get framebuffer viewport
    viewport_width, viewport_height = glfw.get_framebuffer_size(window)
    viewport = mj.MjrRect(0, 0, viewport_width, viewport_height)

    # Update scene and render
    mj.mjv_updateScene(model, data, opt, None, cam, mj.mjtCatBit.mjCAT_ALL.value, scene)
    mj.mjr_render(viewport, scene, context)

    # Swap OpenGL buffers (blocking call due to v-sync)
    glfw.swap_buffers(window)

    # Process pending GUI events, call GLFW callbacks
    glfw.poll_events()

# Terminate GLFW
glfw.terminate()
