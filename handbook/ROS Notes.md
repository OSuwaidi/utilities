# Notes on ROS

## Introduction

- ROS is a set of tools, libraries, and a framework that enable modular robotic system design and development.
- ROS contains a bunch of modular programs that run simultaneously and communicate with each other. Every program is called a _node_.
- Typically, every node is designed to address one specific task (e.g., read sensor data, send control commands, dislay viz).
- To run a package's node:
  `$ ros2 run <pkg_name> <node_name>`
- To dislpay a list of avaiable nodes:
  `$ ros2 node list`
- Essentially, **ROS nodes are just executables**.
- ROS nodes communicate via _topics_ and _messages_. Topics are named locations (destinations) that a node can publish a message to.
- Nodes that publish messages to topics are called _publishers_, and nodes that subscribe to topics to receieve messages are called _subscribers_.
- A single node can be both.
- To dislpay a list of avaiable topics:
  `$ ros2 topic list`
- To publish a topic:
  `$ ros2 topic pub /<topic_name> <msg_type> "<payload>"`
- To act as a subscriber and see what's being published on a topic:
  `$ ros2 topic echo /<topic_name>`, adding `--no-arr` flag hides array data
- To send a message that doesn't need to be accessed by everyone (unlike a topic), we use _services_.
- Services are usually used to trigger an event rather than continously monitor/track/control something.
- To dislpay a list of avaiable services:
  `$ ros2 service list`
- To call a service explicitly:
  `$ros2 service call /<service_name> ...`, where `...` refers to the message we want to send the service (sometimes empty)
- ROS provides _parameters_ for its commands that allow us to modify the behavior of a node (as exposed by the node itself).
- ROS also provides _remapping_ which allows us to change the name of a topic or a service to ensure communication compatability.
  - for example, if a node is publishing to topic X while another node is expecting to receive that message from topic Y, we can remap the name of X to Y
  - or if two nodes are publishing to the same topic name when they should be different, we can remap their topics
- To specify ROS parameters `-p` or remapping `-r`:
  `$ ros2 <some_command> --ros-args -p <x_parameter:=X> -r <old_name:=new_name>`
- To isolate topic names and avoid naming conflicts, we can run a node inside a _name space_; a named "folder" that contains all the node's topics/services within it:
  `$ ros2 <some_command> --ros-args -r __ns:=</some_name_space>`
- _Quality of Service (QoS)_ is a communication protocol between publishers and subscribers. They must agree on the QoS to communicate successfuly.
- To view the QoS profile of any topic:
  `$ ros2 topic info /<topic_name> -v`

## Notes on Transform System (TF2)

- TF2 is a coordinate frame transformation library that enables nodes to _broadcast_ a transform from one frame to another.
- Given a series of nodes with every node broadcasting a transform to another, we form a _transform tree_.
- Nodes can also _listen_ to transforms to convert between frames (analogous to: publisher -> broadcaster, subscriber -> listener).
- A node can broadcast two types of transform topics, static and dynamic:
  - `/tf_static`: transformation is constant w.r.t to time (absolute frame)
  - `/tf`: transformation changes over time
- If a transformation is dynamic, the broadcaster needs to _update it regularly_ to keep listener nodes up to date on its pose.
- To broadcast a static transform from a `parent_frame` to a `child_frame`:
  `$ ros2 run tf2_ros static_transform_publisher x y z yaw pitch roll parent_frame child_frame` # translation occurs first, then rotations (in rads)
- To visualize the transformation data by `tf`, we use `rviz2`:
  `$ rviz2`

## Robot state publisher (rsp)

- The ROS node `robot_state_publisher` (_rsp_) takes in a URDF file and broadcasts all the transforms from it along with a `/robot_description` topic:
  - URDF file -> `robot_state_publisher` -> [`/tf_static`, `/tf`, `/robot_description`]
  - `$ ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(xacro path/to/my/xacro/file.urdf.xacro)"`
  - A better way to publish the robot's URDF is via a _launch file_, which includes the `robot_state_publisher` node and other nodes with their respective commands (args).
- However, for `robot_state_publisher` to publish dynamic transforms, it needs external values to calculate the transform at each point in time.
- It does so by subscribing to the `/joint_states` topic, which sends `JointSate` messages.
- But where does `/joint_states` get its `JointSate` messages from to inform `robot_state_publisher`? They come from physical or simulated actuator feedback sensors.
- To generate manual (fake) joint values (`JointSate` messages) from our robot for rsp to broadcast its corresponding transforms:
  `$ ros2 run joint_state_publisher_gui joint_state_publisher_gui` -> which can then be visualized via `rviz2`
- It's a good practice to write a bunch of modular URDF files describing specific parts of the robot rather than writing a single big one. This allows for efficient re-use, ease of change, and logic sepraration.
- `xacro` is a _macro_ language that helps manipulate URDF files. It allows to combine multiple modular URDF files into a single complete one to be published.
- To enable `xacro`: `<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="my_robot">`
- `xacro` is basically like Jinja2; a template engine.

## Create ROS packages

- To run a bunch of nodes, each with its specific args (params and remappings), we write a _launch file_; a `.py` script that specifies the command for each node.
- The core ROS _workspace_ is called the _underlay_ (system installation dir). Subsequent local workspaces are called _overlays_.
- To create a ROS package, create a workspace/src dir `~/<name_ws>`, then in its `src`: `$ cd ~/<name_ws>/src/` dir run:
  `$ ros2 pkg create --build-type <ament_python, ament_cmake> <pkg_name>`
- Then, create `launch/` and `urdf/` folders in the package root `$ cd ~/<name_ws>/src/<pkg_name>`. The dir strucutre should look like:

```text
~/<name_ws>/src/<pkg_name>
  launch/
  <pkg_name>/          # Python module
  resource/
  test/
  urdf/
  package.xml
  setup.py
  setup.cfg
```

- Now move all your `.urdf.xacro` and `.xacro` files into `urdf/`, and move your `launch.py` file into `launch/` (modify `setup.py` file accordingly).
- The ROS _build tool_ is called `colcon`; it takes all the source files from `src` dir, builds them into `build` dir, then install them in `install` dir
- To build your package (from the root of the workspace `$ cd ~/<name_ws>`):
  `$ colcon build --symlink-install`
- Then, for your package to be discoverable by `ros2`, you need to _source_ it from the workspace root `cd ~/<name_ws>`:
  `$ source install/setup.bash`
- Finally, for `ros2` to run your `<launch_file>` that contains the commands for all your nodes (e.g., `robot_state_publisher` node):
  `$ ros2 launch <pkg_name> <launch_file>`
  `$ rm -rf build/<pkg_name> install/<pkg_name>` to reset your package

## Notes on Robotic Description

- A _URDF_ (Unified Robot Description Format) is a ROS (config) file format that describes a single robot's physical characteristics _in isolation_ (e.g., size, shape, color).
- A URDF file is written in XML (a data storage and exchange language).
- In a URDF, a robot is composed of a tree of rigid _links_, where different links are connected/related by _joints_.
- This is analogous to: frames -> links, transforms -> joints
- Links describe the overall strucutre of the robot's components/parts (frontend). Whereas joints describe the relationship between them and the motions permitted (backend).
- Specifically, **joints define the relationship between the origins (coordinate frames) of the links (defines their poses)**.
- Every link except the first one (base) has a joint connecting it to its parent link. Each link can _only have one parent_, but can have multiple children.
  - If we have N links, we must have N-1 joints.
- Every joint is associated with a _type of motion_ that describes how it moves in space:
  1. revolute: rotational motion about a point with a fixed limit (hinge)
  2. continuous: rotational motion about a point with no fixed limits (wheel)
  3. prismatic: sliding (linear) motion along an axis without roation (pump)
  4. fixed: child link is fixed (no motion) relative to the parent link

```xml
<!-- The top of a URDF file -->
<robot name="my_robot">
    ...
    all the rest of the tags
    ...
</robot>
```

```xml
<!-- Link example -->
<link name="arm_link">
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.1 0.1 0.1"/>
    </geometry>
    <material name="grey">
      <color rgba="0.5 0.5 0.5 1.0"/>
    </material>
  </visual>

  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.1 0.1 0.1"/>
    </geometry>
  </collision>

  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="1.0"/>
    <inertia ixx="0.1" ixy="0.0" ixz="0.0"
             iyy="0.1" iyz="0.0" izz="0.1"/>
  </inertial>
</link>
```

```xml
<!-- Joint example -->
<joint name="arm_joint" type="revolute">
    <parent link="slider_link"/>
    <child link="arm_link"/>
    <origin xyz="0.25 0 0.15" rpy="0 0 0"/>
    <axis xyz="0 -1 0"/>  <!-- axis of movement (permitted motion axes) -->
    <limit lower="0" upper="${pi/2}" velocity="100" effort="100"/>
</joint>
```

## Notes on Gazebo

- Gazebo uses _SDF_ (Simulation Description Format) files, which are more comprehensive formats that describe a whole world: including robots, their poses, complex joint loops.
- Everytime Gazeo needs to interact with programs external to it (e.g., interact w/ ROS, access sensor data), it needs to use _plugins_ (code libraries).
- Now, Gazebo has Spawner Script that subscribes to `/robot_description` to simulate the robot in the world.
- It then uses a plugin to publish `JointState` message to `/join_states` based on how the joints are moving in simulation.
- It also has a plugin that enables ROS to control the joints of the robot in simulation.
- Any sensors used in Gazebo will have their own plugins that publish to their respective topics.
- To list out all the topics published by Gazebo over Ignition Transport topics:
  `$ ign topic -l`
- To find out of Ignition Gazebo is still running in the background:
  `$ ps aux | grep "ign gazebo"`
- To found out message type being published on a topic from within Ignition:
  `$ ign topic -i --topic /ptz/camera/image_raw`
- For extra Gazebo docs, refer to: <https://articulatedrobotics.xyz/tutorials/ready-for-ros/gazebo>
- To launch Gazebo with ROS support (context):

```bash
# GUI + server:
ros2 launch ros_gz_sim gz_sim.launch.py

# Or specify a world/SDF:
ros2 launch ros_gz_sim gz_sim.launch.py gz_args:=empty.sdf
```

- To spawn a robot model in a an active Gazebo world, we use the `rsp` node publishing its URDF file(s):
  `$ ros2 run ros_gz_sim create -world empty -name <robot_name> -topic /robot_description`, or instead of `-topic`: `-file /path/to/robot.sdf`
- ROS 2 - Gazebo bridges:
  1. `$ ros2 run ros_gz_image image_bridge /ptz/camera/image_raw`
  2. `$ ros2 run ros_gz_bridge parameter_bridge /ptz/camera/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo`
  3. `$ ros2 run ros_gz_bridge parameter_bridge /model/my_robot/joint/zoom_joint/cmd_vel@std_msgs/msg/Float64@ignition.msgs.Double`
- ROS 2 Command:
  `$ ros2 topic pub /model/my_robot/joint/zoom_joint/cmd_vel std_msgs/msg/Float64 "data: 0.5" -1`

---

1. After you create a camera link/joint for your robot's model, it will publish its message on a particular topic (in Gazebo, internally).
2. _For it to publish correctly in Gazebo, the Gazbo world needs to have Sensors system plugin!!!_
   2.5 to make sure that your camera is publishing in Gazebo correctly: `$ ign topic -l | grep <name>` where name comes from model .urdf: `<topic>/name/camera/image_raw</topic>`
3. You need to establish a ROS2-Gazebo bridge for that topic to be exposed to ROS2.
4. The YOLO package launch file will start a node that subscribes to your camera’s image topic on ROS2 (by default, it looks for /image_raw – you might need to remap it to your camera topic).
5. It will run the YOLO model against the camera iamge and publish results. By default, it publishes bounding boxes on a specific topic.
   According to the README, it publishes on topics like /yolov5/bounding_boxes containing an array of detected boxes.

Q.) Do we need the following nodes: Controller manager spawner + joint state broadcaster + pan-tilt-zoom trajectory controller?

Use Ignition Gazebo’s joint controller plugins to accept commands on ROS topics. For example, add a JointPositionController plugin for each joint in your URDF/SDF. This plugin creates a topic (by default) at /model/<model_name>/joint/<joint_name>/<index>/cmd_pos that accepts a target position
gazebosim.org
. For instance, for a pan_joint of your robot (index 0 if single-axis), the topic might be /model/cam_robot/joint/pan_joint/0/cmd_pos. You can then bridge this to a ROS topic using ros_gz_bridge so that a ROS node can publish a std_msgs/Float64 message (which the bridge converts to Ignition’s Double message) to command the joint angle


[ptz_controller]: Target '('balloon', 'sphere')' detected with prob. 74.00%. Stopping scan & starting zoom.
