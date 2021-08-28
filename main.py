#!/usr/bin/python3.6

import os
import time

import asterisk.agi
from dotenv import load_dotenv
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, authenticator

load_dotenv()
TEXT_TO_SPEECH_API = os.getenv('TEXT_TO_SPEECH_API')
TEXT_TO_SPEECH_URL = os.getenv('TEXT_TO_SPEECH_URL')
AUDIO_FILE_DIR = os.getenv('AUDIO_FILE_DIR')

# watsonのTTSに認証する
authenticator = IAMAuthenticator(TEXT_TO_SPEECH_API)
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)
text_to_speech.set_service_url(TEXT_TO_SPEECH_URL)

if not os.path.exists(AUDIO_FILE_DIR):
    os.mkdir(AUDIO_FILE_DIR)

def main():
    agi = asterisk.agi.AGI()

    # dialplanで定義した${TEXT}をwatsonでTTSする
    text = agi.get_variable('TEXT')
    uniqueid = str(agi.get_variable('UNIQUEID'))
    file_path = f'{AUDIO_FILE_DIR}{uniqueid}.ulaw'
    agi.verbose(file_path)

    while not os.path.exists(file_path):
        with open(file_path, 'wb') as audio_file:
            audio_file.write(
                text_to_speech.synthesize(
                    text,
                    voice='ja-JP_EmiVoice',
                    accept='audio/basic',
                ).get_result().content
            )
        time.sleep(0.5)

    file_name = file_path.strip('.ulaw')
    dtmf = agi.get_data(file_name, 10000, 1) # dialplanのBackground()と同じ処理
    os.remove(file_path)

    if int(dtmf) == 1:
        agi.exec_command('Playback', 'demo-thanks')
    elif int(dtmf) == 2:
        agi.exec_command('Goto', 'test-milliwatt,s,1')
    else:
        agi.exec_command('PlayBack', 'goodbye')

if __name__ == '__main__':
    main()