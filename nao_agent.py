from qibullet import SimulationManager
import pyttsx3
import string
import time
import cv2

class Nao(SimulationManager):
    def __init__(self, gui: bool = True, auto_step: bool = True):
        super().__init__()
        self.client_id = self.launchSimulation(gui=gui, auto_step=auto_step)
        self.robot = self.spawnNao(self.client_id, spawn_ground_plane=True)
        self.voice_engine = pyttsx3.init()
    
    #####################################################################################
    ##################################     ACTIONS     ##################################
    #####################################################################################
    
    # capture image
    def capture_image(self, camera: str = 'top'):
        if camera == 'top':
            handle = self.robot.subscribeCamera(self.robot.ID_CAMERA_TOP, fps=15.0)
            img = self.robot.getCameraFrame(handle)
            self.robot.unsubscribeCamera(handle)
            return img
        elif camera == 'bottom':
            handle = self.robot.subscribeCamera(self.robot.ID_CAMERA_BOTTOM, fps=15.0)
            img = self.robot.getCameraFrame(handle)
            self.robot.unsubscribeCamera(handle)
            return img
        
    # stream video
    def stream_video(self, camera: str = 'top'):
        if camera == 'top':
            handle = self.robot.subscribeCamera(self.robot.ID_CAMERA_TOP, fps=15.0)
            while True:
                img = self.robot.getCameraFrame(handle)
                cv2.imshow("top camera", img)
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    break
            self.robot.unsubscribeCamera(handle)
            cv2.destroyAllWindows()
        elif camera == 'bottom':
            handle = self.robot.subscribeCamera(self.robot.ID_CAMERA_BOTTOM, fps=15.0)
            while True:
                img = self.robot.getCameraFrame(handle)
                cv2.imshow("bottom camera", img)
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    break
            self.robot.unsubscribeCamera(handle)
            cv2.destroyAllWindows()

    # speak
    def speak(self, speech: str):
        speech = speech.translate(str.maketrans('', '', string.punctuation)) # remove punctuation
        self.voice_engine.say(speech)
        self.voice_engine.runAndWait()
        self.voice_engine.stop()

    # stand
    def stand(self):
        self.robot.goToPosture("Stand", 1.0)

    # sit
    def sit(self):
        # self.robot.setAngles(['LHipPitch', 'RHipPitch', 'LKneePitch', 'RKneePitch', 'LAnklePitch', 'RAnklePitch'], [-1.0, -1.0, 2.1, 2.1, -0.13, -0.13], 0.2)
        # self.robot.setAngles(['LHipPitch', 'RHipPitch', 'LKneePitch', 'RKneePitch'], [-1.0, -1.0, 2.1, 2.1], 0.2)
        self.robot.goToPosture("Crouch", 0.4)
        time.sleep(0.2)
        self.robot.goToPosture("Sit", 0.65)

    # crouch
    def crouch(self):
        self.robot.goToPosture("Crouch", 0.1)

    # rest
    def rest(self):
        self.robot.goToPosture("Rest", 1.0)

    # move
    def move(self, x: float, y: float, theta: float):
        self.robot.moveTo(x, y, theta)

    # wave hand
    def wave(self, hand: str = 'right'):
        if hand == 'left':
            # save the current position of the left shoulder
            prev_pitch = self.robot.getAnglesPosition(['LShoulderPitch'])
            prev_roll = self.robot.getAnglesPosition(['LShoulderRoll'])
            
            # wave the left hand two times
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll'], [-1.2, 0.8], 0.5)
            time.sleep(0.5)
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll'], [-1.2, -0.1], 0.5)
            time.sleep(0.5)
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll'], [-1.2, 0.8], 0.5)
            time.sleep(0.5)
            # get back to the previous position
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll'], [prev_pitch, prev_roll], 0.5)

        elif hand == 'right':
            # save the current position of the right shoulder
            prev_pitch = self.robot.getAnglesPosition(['RShoulderPitch'])
            prev_roll = self.robot.getAnglesPosition(['RShoulderRoll'])
            
            # wave the left hand two times
            self.robot.setAngles(['RShoulderPitch', 'RShoulderRoll'], [-1.2, 0.8], 0.5)
            time.sleep(0.5)
            self.robot.setAngles(['RShoulderPitch', 'RShoulderRoll'], [-1.2, -1.0], 0.5)
            time.sleep(0.5)
            self.robot.setAngles(['RShoulderPitch', 'RShoulderRoll'], [-1.2, 0.8], 0.5)
            time.sleep(0.5)
            # get back to the previous position
            self.robot.setAngles(['RShoulderPitch', 'RShoulderRoll'], [prev_pitch, prev_roll], 0.5)


    # nod head
    def nod_head(self, direction: str = 'up_down'):
        if direction == 'up_down':
            # save the current position of the head
            prev_pitch = self.robot.getAnglesPosition(['HeadPitch'])
            
            # nod the head two times
            self.robot.setAngles(['HeadPitch'], [-0.5], 0.5)
            time.sleep(0.5)
            self.robot.setAngles(['HeadPitch'], [0.5], 0.5)
            time.sleep(0.5)
            self.robot.setAngles(['HeadPitch'], [prev_pitch], 0.5)

        elif direction == 'right_left':
            # save the current position of the head
            prev_yaw = self.robot.getAnglesPosition(['HeadYaw'])
            
            # nod the head two times
            self.robot.setAngles(['HeadYaw'], [-0.5], 0.5)
            time.sleep(0.5)
            self.robot.setAngles(['HeadYaw'], [0.5], 0.5)
            time.sleep(0.5)
            self.robot.setAngles(['HeadYaw'], [prev_yaw], 0.5)


    # turn head
    def turn_head(self, direction: str = 'right'):
        if direction == 'right':
            self.robot.setAngles(['HeadYaw'], [-0.5], 0.5)
        elif direction == 'left':
            self.robot.setAngles(['HeadYaw'], [0.5], 0.5)

    # gaze head
    def gaze_head(self, direction: str = 'up'):
        if direction == 'up':
            self.robot.setAngles(['HeadPitch'], [-0.5], 0.5)
        elif direction == 'down':
            self.robot.setAngles(['HeadPitch'], [0.5], 0.5)

    # raise arms
    def raise_arms(self, hand: str = 'both'):
        if hand == 'left':
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll'], [-1.2, 0.1, -0.4, -0.3], 0.5)
        elif hand == 'right':
            self.robot.setAngles(['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll'], [-1.2, -0.2, -0.1, 0.2], 0.5)
        elif hand == 'both':
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll'], [-1.2, 0.1, -0.4, -0.3, -1.2, -0.2, -0.1, 0.2], 0.5)

    # walk
    def walk(self, x: float, y: float, theta: float):
        pass

    # handshake
    def handshake(self, hand: str = 'right'):
        if hand == 'left':
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll'], [0.5, -0.1, -1.5, -0.2], 0.5)
            time.sleep(0.7)
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll'], [0.5, -0.1, -1.5, -0.7], 0.5)
            time.sleep(0.7)
            self.robot.setAngles(['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll'], [0.5, -0.1, -1.5, -0.2], 0.5)
        elif hand == 'right':
            self.robot.setAngles(['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll'], [0.5, -0.1, 1.3, 0.8], 0.5)
            time.sleep(0.7)
            self.robot.setAngles(['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll'], [0.5, -0.1, 1.3, 0.1], 0.5)
            time.sleep(0.7)
            self.robot.setAngles(['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll'], [0.5, -0.1, 1.3, 0.8], 0.5)

    # reset nao pose
    def reset_nao_pose(self):
        self.robot.goToPosture("Stand", 0.2)


    # shutdown
    def shutdown(self):
        self.stopSimulation(self.client_id)