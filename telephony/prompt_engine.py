from os import path
from rootio.config import *
from rootio.configuration import VoicePrompt


class PromptEngine:

    def __init__(self, station):
        self.__station = station
        self.ON_AIR_PROMPT = {"is_file": False, "prompt": "You are now on air"}
        self.CALL_END_WARNING = {"is_file": False, "prompt": "Your call will be terminated a minute from now"}
        self.CALLER_ON_THE_LINE = {"is_file": False, "prompt": "You have a caller on the line. To connect to the station, press one, to cancel, press two"}
        self.INQUIRE_HOST_READY = {"is_file": False, "prompt": "You are scheduled to host a talk show at this time. If you are ready, press one, if not ready, press two"}
        self.AWAIT_STATION_CONNECTION = {"is_file": False, "prompt": "'Please wait while we connect you to the radio station"}
        self.ENTERING_WAKE_MODE = {"is_file": False, "prompt": "Your call will be terminated and you will be called when someone calls into the station"}
        self.ENTERING_REJECT_MODE = {"is_file": False, "prompt": "All incoming calls will be rejected"}
        self.ENTERING_AUTO_ANSWER_MODE = {"is_file": False, "prompt": "All incoming calls will be automatically answered"}
        self.ENTERING_QUEUING_MODE = {"is_file": False, "prompt": "All incoming calls will be queued for call back"}
        self.ENTERING_5_MIN_BREAK = {"is_file": False, "prompt": "You will be called back in 5 minutes"}
        self.ENTER_NUMBER_TO_CALL = {"is_file": False, "prompt": "Please enter the number to call and press the # key to dial"}
        self.CALLING_OUT = {"is_file": False, "prompt": "You are calling"}
        self.INCOMING_CALL_QUEUED = {"is_file": False, "prompt": "You have a new caller on the line"}
        self.CALL_FAILED = {"is_file": False, "prompt": "The call to {0} failed. Please press the hash key to try again"}
        self.CALL_BACK_NOTIFICATION = {"is_file": False, "prompt": "Thank you for wanting to take part in this program. We will call you back shortly"}
        self.AWAIT_HOST_CONNECTION = {"is_file": False, "prompt": "Please wait while we connect you to the host of this program"}
        try:
            self.__load_prompts()
        except Exception as e:
            print e
        
    def __load_prompts(self):
        voice_prompts = self.__station.db.query(VoicePrompt).filter(VoicePrompt.deleted == False).order_by(VoicePrompt.updated_at.desc()).filter(VoicePrompt.station_id == self.__station.id).first()
        print voice_prompts
        if voice_prompts is not None:
            print "Using tts prompts"
            if not voice_prompts.use_tts:  # Use TTS, but the text files already downloaded as audio, or audio uploaded
                self.ON_AIR_PROMPT = {True: {"is_file": True, "prompt": voice_prompts.on_air}, False: self.ON_AIR_PROMPT}[voice_prompts.on_air is not None]
                self.CALL_END_WARNING = {True: {"is_file": True, "prompt": voice_prompts.call_end}, False: self.CALL_END_WARNING}[voice_prompts.call_end is not None]
                self.CALLER_ON_THE_LINE = {True: {"is_file": True, "prompt": voice_prompts.incoming_call}, False: self.CALLER_ON_THE_LINE}[voice_prompts.incoming_call is not None]
                self.INQUIRE_HOST_READY = {True: {"is_file": True, "prompt": voice_prompts.host_welcome}, False: self.INQUIRE_HOST_READY}[voice_prompts.host_welcome is not None]
                self.AWAIT_STATION_CONNECTION = {True: {"is_file": True, "prompt": voice_prompts.host_wait}, False: self.AWAIT_STATION_CONNECTION}[voice_prompts.host_wait is not None]
                self.ENTERING_WAKE_MODE = {True: {"is_file": True, "prompt": voice_prompts.wake_mode_activation}, False: self.ENTERING_WAKE_MODE}[voice_prompts.wake_mode_activation is not None]
                self.ENTERING_REJECT_MODE = {True: {"is_file": True, "prompt": voice_prompts.incoming_reject_activation}, False: self.ENTERING_REJECT_MODE}[voice_prompts.incoming_reject_activation is not None]
                self.ENTERING_AUTO_ANSWER_MODE = {True: {"is_file": True, "prompt": voice_prompts.incoming_answer_activation}, False: self.ENTERING_AUTO_ANSWER_MODE}[voice_prompts.incoming_answer_activation is not None]
                self.ENTERING_QUEUING_MODE = {True: {"is_file": True, "prompt": voice_prompts.incoming_queue_activation}, False: self.ENTERING_QUEUING_MODE}[voice_prompts.incoming_queue_activation is not None]
                self.ENTERING_5_MIN_BREAK = {True: {"is_file": True, "prompt": voice_prompts.take_break}, False: self.ENTERING_5_MIN_BREAK}[voice_prompts.take_break is not None]
                self.ENTER_NUMBER_TO_CALL = {True: {"is_file": True, "prompt": voice_prompts.input_number}, False: self.ENTER_NUMBER_TO_CALL}[voice_prompts.input_number is not None]
                self.CALLING_OUT = {True: {"is_file": True, "prompt": voice_prompts.calling_number}, False: self.CALLING_OUT}[voice_prompts.calling_number is not None]
                self.INCOMING_CALL_QUEUED = {True: {"is_file": True, "prompt": voice_prompts.call_queued}, False: self.INCOMING_CALL_QUEUED}[voice_prompts.call_queued is not None]
                self.CALL_FAILED = {True: {"is_file": True, "prompt": voice_prompts.call_failed}, False: self.CALL_FAILED}[voice_prompts.call_failed is not None]
                self.CALL_BACK_NOTIFICATION = {True: {"is_file": True, "prompt": voice_prompts.call_back_hangup}, False: self.CALL_BACK_NOTIFICATION}[voice_prompts.call_back_hangup is not None]
                self.AWAIT_HOST_CONNECTION = {True: {"is_file": True, "prompt": voice_prompts.call_back_wait}, False: self.AWAIT_HOST_CONNECTION}[voice_prompts.call_back_wait is not None]
            else:
                print "no tts"
                self.ON_AIR_PROMPT = \
                {True: {"is_file": False, "prompt": voice_prompts.on_air_txt}, False: self.ON_AIR_PROMPT}[
                    voice_prompts.on_air_txt is not None]
                self.CALL_END_WARNING = \
                {True: {"is_file": False, "prompt": voice_prompts.call_end_txt}, False: self.CALL_END_WARNING}[
                    voice_prompts.call_end_txt is not None]
                self.CALLER_ON_THE_LINE = \
                {True: {"is_file": False, "prompt": voice_prompts.incoming_call_txt}, False: self.CALLER_ON_THE_LINE}[
                    voice_prompts.incoming_call_txt is not None]
                self.INQUIRE_HOST_READY = \
                {True: {"is_file": False, "prompt": voice_prompts.host_welcome_txt}, False: self.INQUIRE_HOST_READY}[
                    voice_prompts.host_welcome_txt is not None]
                self.AWAIT_STATION_CONNECTION = \
                {True: {"is_file": False, "prompt": voice_prompts.host_wait_txt}, False: self.AWAIT_STATION_CONNECTION}[
                    voice_prompts.host_wait_txt is not None]
                self.ENTERING_WAKE_MODE = \
                {True: {"is_file": False, "prompt": voice_prompts.wake_mode_activation_txt}, False: self.ENTERING_WAKE_MODE}[
                    voice_prompts.wake_mode_activation_txt is not None]
                self.ENTERING_REJECT_MODE = \
                {True: {"is_file": False, "prompt": voice_prompts.incoming_reject_activation_txt},
                 False: self.ENTERING_REJECT_MODE}[voice_prompts.incoming_reject_activation_txt is not None]
                self.ENTERING_AUTO_ANSWER_MODE = \
                {True: {"is_file": False, "prompt": voice_prompts.incoming_answer_activation_txt},
                 False: self.ENTERING_AUTO_ANSWER_MODE}[voice_prompts.incoming_answer_activation_txt is not None]
                self.ENTERING_QUEUING_MODE = \
                {True: {"is_file": False, "prompt": voice_prompts.incoming_queue_activation_txt},
                 False: self.ENTERING_QUEUING_MODE}[voice_prompts.incoming_queue_activation_txt is not None]
                self.ENTERING_5_MIN_BREAK = \
                {True: {"is_file": False, "prompt": voice_prompts.take_break_txt}, False: self.ENTERING_5_MIN_BREAK}[
                    voice_prompts.take_break_txt is not None]
                self.ENTER_NUMBER_TO_CALL = \
                {True: {"is_file": False, "prompt": voice_prompts.input_number_txt}, False: self.ENTER_NUMBER_TO_CALL}[
                    voice_prompts.input_number_txt is not None]
                self.CALLING_OUT = \
                {True: {"is_file": False, "prompt": voice_prompts.calling_number_txt}, False: self.CALLING_OUT}[
                    voice_prompts.calling_number_txt is not None]
                self.INCOMING_CALL_QUEUED = \
                {True: {"is_file": False, "prompt": voice_prompts.call_queued_txt}, False: self.INCOMING_CALL_QUEUED}[
                    voice_prompts.call_queued_txt is not None]
                self.CALL_FAILED = \
                {True: {"is_file": False, "prompt": voice_prompts.call_failed_txt}, False: self.CALL_FAILED}[
                    voice_prompts.call_failed_txt is not None]
                self.CALL_BACK_NOTIFICATION = \
                {True: {"is_file": False, "prompt": voice_prompts.call_back_hangup_txt}, False: self.CALL_BACK_NOTIFICATION}[
                    voice_prompts.call_back_hangup_txt is not None]
                self.AWAIT_HOST_CONNECTION = \
                {True: {"is_file": False, "prompt": voice_prompts.call_back_wait_txt}, False: self.AWAIT_HOST_CONNECTION}[
                    voice_prompts.call_back_wait_txt is not None]

                
    def play_prompt(self, prompt, call_handler, call_uuid):
        if prompt.get("is_file"):
            return call_handler.play(call_uuid, path.join(DefaultConfig.CONTENT_DIR,prompt.get("prompt")))
        else:
            return call_handler.speak(prompt.get("prompt"), call_uuid)
            

