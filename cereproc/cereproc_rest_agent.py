import requests
from lxml import etree


class CereprocRestAgent:

    def __init__(self, cereproc_url, cereproc_username, cereproc_password, gender='male', language='english',
                 sample_rate='16000', audio_format='wav'):
        self._cereproc_url = cereproc_url
        self._cereproc_username = cereproc_username
        self._cereproc_password = cereproc_password
        self._gender = gender
        self._language = language
        self._sample_rate = sample_rate
        self._audio_format = audio_format

        # To save time in TTS operations, it makes sense to load the voices when
        # this class is instantiated rather than for individual TTS requests
        self._voices = self.cprc_list_voices()

    def __do_cprc_request(self, data):  # raise error if http error, if network failure
        headers = {'Content-type': 'text/xml'}
        response = requests.post(self._cereproc_url, headers=headers, data=data)
        return etree.fromstring(response.text)

    def __generate_request_xml(self, root, data):
        rt = etree.Element(root)
        for key in data:
            itm = etree.Element(str(key))
            itm.text = str(data[key])
            rt.append(itm)
        return etree.tostring(rt, xml_declaration=True)

    def cprc_list_voices(self):
        requestxml = self.__generate_request_xml("listVoices", {'accountID': self._cereproc_username,
                                                               'password': self._cereproc_password})
        return self.__do_cprc_request(requestxml)

    def get_cprc_tts(self, text, voice=None, sample_rate=None, audio_format=None, metadata=True):
        if voice is None:
            voice = self._choose_voice()

        if sample_rate is None:  # use default
            sample_rate = self._sample_rate
        elif sample_rate not in [8000, 16000, 48000]:  # a sample rate was supplied but is not among those supported
            raise ValueError("Audio sample rate not supported")

        if audio_format is None:  # use the default
            audio_format = self._audio_format
        elif audio_format not in ['wav', 'mp3',
                                  'ogg']:  # a format was specified but is not among those that are supported
            raise ValueError("Audio format not supported")
        metadata = bool(metadata)

        requestxml = self.__generate_request_xml("speakExtended", {'accountID': self._cereproc_username,
                                                                  'password': self._cereproc_password, 'voice': voice,
                                                                  'audioFormat': audio_format,
                                                                  'sampleRate': sample_rate, 'audio3D': '',
                                                                  'metadata': metadata, 'text': text})
        responsexml = self.__do_cprc_request(requestxml)

        if responsexml.findtext('resultCode') != '1':
            raise RuntimeError('Failed to synthesize voice with Cereproc Cloud server')

        audiofile_url = responsexml.findtext('fileUrl')
        metadata_url = responsexml.findtext('metadataUrl')
        transcription = None
        if metadata_url is not None:
            transcription = {'trans': []}
            metadata_response = requests.get(metadata_url)
            trans = etree.fromstring(metadata_response.text)
            if trans.tag != 'trans':
                raise RuntimeError('Meta data not a valid transcription')
            for event in trans:
                e = {
                    'name': event.attrib.get('name'),
                    'start': float(event.attrib.get('start')),
                    'end': float(event.attrib.get('end')),
                }
                transcription['trans'].append({event.tag: e})

        return audiofile_url, transcription

    def _choose_voice(self, language=None, gender=None, accent=None, strict_gender=False, strict_accent=False):
        voicelist = self._voices.find('voicesList')
        if language is None:
            language = self._language
        if gender is not None:
            gender = gender.lower()
            if gender not in ['male', 'female']:
                raise ValueError('Gender must be "Male", "Female"')
        if accent is not None:
            accent = accent.lower()
        language = language.lower()

        if not len(voicelist):
            raise RuntimeError('No suitable voices found in supplied listing')

        voice_match_gender = False
        voice_match_accent = False
        for voice in voicelist:
            voice_name = voice.findtext('voiceName')
            voice_language = voice.findtext('language').lower()
            voice_gender = voice.findtext('gender').lower()
            voice_accent = voice.findtext('accent').lower()

            if voice_language == language:
                gender_matches = (not gender or voice_gender == gender)
                accent_matches = (not accent or voice_accent == accent)

                if gender_matches and accent_matches:
                    return voice_name
                if gender_matches and not strict_gender:
                    voice_match_gender = voice_name
                if accent_matches and not strict_accent:
                    voice_match_accent = voice_name

        if voice_match_gender:
            return voice_match_gender
        elif voice_match_accent:
            voice_match_accent
        else:
            raise ValueError('Cannot find voice')
