import mujoco as mj
from mujoco.glfw import glfw
import numpy as np
import os

flag =0
count=0
xml_path = 'Probing_Physics.xml' #xml file (assumes this is in the same folder as this file)
simend = 200 #simulation time
print_camera_config = 0 #set to 1 to print camera config
                        #this is useful for initializing view of the model)

# For callback functions
button_left = False
button_middle = False
button_right = False
lastx = 0
lasty = 0

# Define the limit for rod position
rod_limit = 0.05
positive_force = 1
negative_force = -0.5
# initial_force = 0
force_sensor_limit = 0.24
probe_position_limit = -0.027

Xaxis_position_start=-0.15
probestart=0
onetime=True

Yaxis_position_count = 0
Yaxis_position_start = 0.01
OneSweepComplete = False


def init_controller(model,data):
    #initialize the controller here. This function is called once, in the beginning
    # global initial_force, force_sensor_limit, positive_force, negative_force
    # initial_force = data.sensordata[0]
    # print ( "initial_force", initial_force)
    # force_sensor_limit = initial_force + 0.24
    #initialize the controller here. This function is called once, in the beginning
    # data.ctrl[0]= positive_force
    data.ctrl[1]=-0.5
    pass

def controller(model, data):
    global probestart
    # put the controller here. This function is called inside the simulation.
    # Check if the position of the rod exceeds the limit
    if probestart==0:
        probe_movement()
    elif probestart==1:
        Horizondal_Xaxis_movement()
    elif probestart==2:
        # print("Test bed move")
        Test_bed_movement()
    # probe_movement()
    
def Test_bed_movement():
    global count, Xaxis_position, Xaxis_position_start, Yaxis_position_count, Yaxis_position_start, probestart,flag,onetime, OneSweepComplete
    
    data.ctrl[1]=-1
    Yaxis_position=data.qpos[0]
    Xaxis_position=data.qpos[1]
    
    if count ==50:
        print("Yaxis position",Yaxis_position)
        # print("Yaxis position start",Yaxis_position_start)
        count=0
    count+=1
    if OneSweepComplete:
        if Yaxis_position < Yaxis_position_start :
            print("Yaxis_position", Yaxis_position)
            print("Yaxis_position_start", Yaxis_position_start)
            print("Xaxis_position", Xaxis_position)
            data.ctrl[2]=0.04
            # OneSweepComplete = False
        elif Xaxis_position<-0.15:
            Yaxis_position_start += 0.01
            data.ctrl[2]=0
            flag=0
            Xaxis_position_start = -0.15
            probestart=1
    


def Horizondal_Xaxis_movement():
    global count,Xaxis_position_start,probestart,flag,onetime, OneSweepComplete
    
    Xaxis_position=data.qpos[1]

    if count ==50:
        print("Xaxis position",Xaxis_position)
        print("Xaxis position start",Xaxis_position_start)
        count=0
    count+=1

    # while flag:
    #     if Xaxis_position>-0.15:
    #         data.ctrl[1]=-0.3
    #     else:
    #         flag =False
    if Xaxis_position>Xaxis_position_start and flag==0:
        flag=0

    elif Xaxis_position<Xaxis_position_start and flag==0:
        data.ctrl[1]=0.5
        flag=1
        Xaxis_position_start+=0.01
        print("working  1")
        
    elif Xaxis_position>Xaxis_position_start and flag==1:
        print("working  2")
        data.ctrl[1]=0
        Xaxis_position_start+=0.01
        probestart=0
        flag=0
        onetime=True
    
    elif Xaxis_position>0.15:
        OneSweepComplete = True
        print("*"*20)
        probestart = 2
    
           
         

def probe_movement():
    force_sensor_value = data.sensordata[0]
    probing_position_value=data.qpos[2]
# position_sensor_value = data.qpos[0]
    global count,probe_position_limit,probestart,onetime

    if count ==50:
        print("Force",force_sensor_value)
        print("Horizondal Position",probing_position_value)
        count=0
    count+=1
    
    if onetime:
       data.ctrl[0]= positive_force
       onetime=False 

    if force_sensor_value > force_sensor_limit  :
        # force_sensor_value=0
        # print("Force sensor value exceeded the limit!")
        # print("Rod position exceeded the limit!")
        # print("===================================================")
        data.ctrl[0]= negative_force

    elif probing_position_value<probe_position_limit:
        data.ctrl[0]= 0
        probestart=1
        
        print("velocity0",data.ctrl[0])

    

          




   

def keyboard(window, key, scancode, act, mods):
    if act == glfw.PRESS and key == glfw.KEY_BACKSPACE:
        mj.mj_resetData(model, data)
        mj.mj_forward(model, data)

def mouse_button(window, button, act, mods):
    # update button state
    global button_left
    global button_middle
    global button_right

    button_left = (glfw.get_mouse_button(
        window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS)
    button_middle = (glfw.get_mouse_button(
        window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS)
    button_right = (glfw.get_mouse_button(
        window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS)

    # update mouse position
    glfw.get_cursor_pos(window)

def mouse_move(window, xpos, ypos):
    # compute mouse displacement, save
    global lastx
    global lasty
    global button_left
    global button_middle
    global button_right

    dx = xpos - lastx
    dy = ypos - lasty
    lastx = xpos
    lasty = ypos

    # no buttons down: nothing to do
    if (not button_left) and (not button_middle) and (not button_right):
        return

    # get current window size
    width, height = glfw.get_window_size(window)

    # get shift key state
    PRESS_LEFT_SHIFT = glfw.get_key(
        window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
    PRESS_RIGHT_SHIFT = glfw.get_key(
        window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    mod_shift = (PRESS_LEFT_SHIFT or PRESS_RIGHT_SHIFT)

    # determine action based on mouse button
    if button_right:
        if mod_shift:
            action = mj.mjtMouse.mjMOUSE_MOVE_H
        else:
            action = mj.mjtMouse.mjMOUSE_MOVE_V
    elif button_left:
        if mod_shift:
            action = mj.mjtMouse.mjMOUSE_ROTATE_H
        else:
            action = mj.mjtMouse.mjMOUSE_ROTATE_V
    else:
        action = mj.mjtMouse.mjMOUSE_ZOOM

    mj.mjv_moveCamera(model, action, dx/height,
                      dy/height, scene, cam)

def scroll(window, xoffset, yoffset):
    action = mj.mjtMouse.mjMOUSE_ZOOM
    mj.mjv_moveCamera(model, action, 0.0, -0.05 *
                      yoffset, scene, cam)

#get the full path
dirname = os.path.dirname(__file__)
abspath = os.path.join(dirname + "/" + xml_path)
xml_path = abspath

# MuJoCo data structures
model = mj.MjModel.from_xml_path(xml_path)  # MuJoCo model
data = mj.MjData(model)                # MuJoCo data
cam = mj.MjvCamera()                        # Abstract camera
opt = mj.MjvOption()                        # visualization options

# Init GLFW, create window, make OpenGL context current, request v-sync
glfw.init()
window = glfw.create_window(1200, 900, "Demo", None, None)
glfw.make_context_current(window)
glfw.swap_interval(1)

# initialize visualization data structures
mj.mjv_defaultCamera(cam)
mj.mjv_defaultOption(opt)
scene = mj.MjvScene(model, maxgeom=10000)
context = mj.MjrContext(model, mj.mjtFontScale.mjFONTSCALE_150.value)

# install GLFW mouse and keyboard callbacks
glfw.set_key_callback(window, keyboard)
glfw.set_cursor_pos_callback(window, mouse_move)
glfw.set_mouse_button_callback(window, mouse_button)
glfw.set_scroll_callback(window, scroll)

# Example on how to set camera configuration
cam.azimuth = 90
cam.elevation = -40
cam.distance = 1
cam.lookat = np.array([0.0, 0.0, 0])

#initialize the controller
init_controller(model,data)

#set the controller
mj.set_mjcb_control(controller)

while not glfw.window_should_close(window):
    time_prev = data.time

    while (data.time - time_prev < 1.0/60.0):
        mj.mj_step(model, data)

    if (data.time>=simend):
        break;

    # get framebuffer viewport
    viewport_width, viewport_height = glfw.get_framebuffer_size(
        window)
    viewport = mj.MjrRect(0, 0, viewport_width, viewport_height)

    #print camera configuration (help to initialize the view)
    if (print_camera_config==1):
        print('cam.azimuth =',cam.azimuth,';','cam.elevation =',cam.elevation,';','cam.distance = ',cam.distance)
        print('cam.lookat =np.array([',cam.lookat[0],',',cam.lookat[1],',',cam.lookat[2],'])')

    # Update scene and render
    mj.mjv_updateScene(model, data, opt, None, cam,
                       mj.mjtCatBit.mjCAT_ALL.value, scene)
    mj.mjr_render(viewport, scene, context)

    # swap OpenGL buffers (blocking call due to v-sync)
    glfw.swap_buffers(window)

    # process pending GUI events, call GLFW callbacks
    glfw.poll_events()

glfw.terminate()
