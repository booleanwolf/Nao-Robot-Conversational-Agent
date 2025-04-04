# NAO Robot Planner with qiBullet & OpenAI

A PyBullet-based simulator for the NAO robot with AI-driven action planning.

## Features

- **OpenAI-Powered Action Planning**: Generates robot action sequences from natural language instructions.
- **Full NAO Robot Simulation**: Control speech, movement, and gestures in a PyBullet environment.
- **Multiple Action Types**: Movement, gestures, speech, and vision capabilities.

## Environment Setup

- A virtual Conda environment with Python 3.9 is used since the latest version of qiBullet supports up to Python 3.9.
- For the ChatGPT-empowered robot planning paper, the OpenAI version used was `openai==0.28.0`. This is included in the requirements.

## Installation (Ubuntu)

1. In your terminal, activate your Conda environment with Python 3.9:
   ```bash
   conda activate base
   conda activate <your_python_env>
   ```
   > **Note:** The latest supported Python version for qiBullet is 3.9. Newer versions of Python3 will throw errors in the code.

2. Clone this repository and navigate to the cloned directory:
   ```bash
   cd ~/
   git clone https://github.com/alfattah129/nao_planner_qibullet.git
   cd ./nao_planner_qibullet
   ```

3. Install the dependencies from `requirements.txt`:
   ```bash
   python3 -m pip install -r ./requirements.txt
   ```
   > **Note:** For installing the qiBullet library alone, follow the README section of the qiBullet repository: [qiBullet GitHub](https://github.com/softbankrobotics-research/qibullet)

## Driver Issue for Conda-Based Virtual Environment Users

(From Sabik's repository. I did not face any issues, but this might help others.)

I encountered a driver issue while running the simulator because I was using an Anaconda environment. According to online sources, there is a problem with the `libstdc++.so` file in Anaconda. It cannot be associated with the system driver, so we remove it and use the `libstdc++` that comes with Linux by creating a soft link.

```bash
cd /home/$USER/anaconda3/envs/$ENV/lib
mkdir backup  # Create a new folder to keep the original libstdc++
mv libstd* backup  # Move all libstdc++ files into the backup folder, including soft links
cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6 ./  # Copy the system's C++ dynamic link library here
ln -s libstdc++.so.6 libstdc++.so
ln -s libstdc++.so.6 libstdc++.so.6.0.19
```

Here, `$ENV` is the name of the Conda environment.

Reference: [Stack Overflow](https://stackoverflow.com/questions/72110384/libgl-error-mesa-loader-failed-to-open-iris)

---

## About This Repository

### `nao_agent.py`
Contains the class for controlling the NAO robot in simulation. The methods in this class represent all available actions for the robot. Feel free to modify or extend these methods.

**Available Actions:**
- `speak(speech=text)`: Make the robot say the specified text.
- `stand()`: Set the joint angles for a standing posture.
- `sit()`: Set the joint angles for a sitting posture *(UNDER DEVELOPMENT).*
- `wave(hand=right/left)`: Wave the specified hand twice (default: `right`).
- `nod_head(direction=up_down/right_left)`: Nod head in "yes" or "no" gesture (default: `up_down`).
- `turn_head(direction=right/left)`: Turn head left or right (default: `right`).
- `gaze_head(direction=up/down)`: Gaze up or down (default: `up`).
- `raise_arms(hand=left/right/both)`: Raise specified arm(s) (default: `both`).
- `walk(x=x, y=y)`: Walk to specified coordinates *(UNDER DEVELOPMENT).*
- `handshake(hand=right/left)`: Perform handshake (default: `right`).
- `reset_nao_pose()`: Reset to default standing pose.
- `capture_image(camera=top/bottom)`: Capture image from camera (default: `top`).
- `stream_video(camera=top/bottom/both)`: Start video stream (default: `top`). Press **Space** to stop.

### `robot_planner.py`
Contains the AI-powered action planner that uses OpenAI's API to convert natural language instructions into executable action sequences for the NAO robot.

**Key Features:**
- Uses GPT-3.5-turbo model for action planning.
- Converts natural language to structured JSON action plans.
- Validates actions against available NAO capabilities.
- Handles parameter generation for complex actions.

**Example Workflow:**
1. **User Input:** "Wave with your left hand, then say hello."
2. **Planner Generates:**
   ```json
   {
     "actions": [
       {
         "action": "wave",
         "parameters": {"hand": "left"}
       },
       {
         "action": "speak",
         "parameters": {"speech": "hello"}
       }
     ]
   }
   ```

### `main.py`
`main.py` serves as the central controller that connects the NAO robot simulation with AI-powered planning. It takes natural language instructions from users, generates corresponding action plans via `robot_planner.py`, and executes them step-by-step on the virtual NAO robot through `nao_agent.py`, while handling errors and maintaining proper timing between actions.

The script runs in a continuous loop until the user enters "stop," providing an interactive way to test all of the robot's capabilities.

> **Note:** Ensure qiBullet installation is complete before running `main.py` or any custom scripts. Keep `nao_agent.py` and `robot_planner.py` in the same directory as the script you're executing, so the NAO class can be accessed correctly.

---

## Useful References

- Example code files: [qiBullet Examples](https://github.com/softbankrobotics-research/qibullet/tree/master/examples)
- Posture control examples: [qiBullet Wiki - Virtual Robot](https://github.com/softbankrobotics-research/qibullet/wiki/Tutorials:-Virtual-Robot)
- qiBullet NAO robot class and available methods: [qiBullet NAO Virtual Class](https://github.com/softbankrobotics-research/qibullet/blob/master/qibullet/nao_virtual.py)

