
import queue
import re
import sys
import os
from google.cloud import speech
import pyaudio

RATE = 16000
CHUNK = int(RATE / 10)

class MicrophoneStream:

    def __init__(self: object, channel:int = 1, in_device_index:int = None, rate: int = RATE, chunk: int = CHUNK) -> None:
        self._rate = rate
        self._chunk = chunk
        self._device_index = in_device_index
        self._channel = channel
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self: object) -> object:
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            input_device_index=self._device_index,
            format=pyaudio.paInt16,
            channels=self._channel,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False
        return self

    def __exit__(
        self: object,
        type: object,
        value: object,
        traceback: object,
    ) -> None:
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(
        self: object,
        in_data: object,
        frame_count: int,
        time_info: object,
        status_flags: object,
    ) -> object:
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self: object) -> object:
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def __listen_print_loop(responses: object, preview:bool=True) -> str:
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            if preview:
                sys.stdout.write(transcript + overwrite_chars + "\r")
                sys.stdout.flush()
            num_chars_printed = len(transcript)

        else:
            break
    return transcript


def listen(credentials_path:str, model:str="latest_short", language_code:str="en-IN", rate:int = RATE, device_index:int = None, channel:int = 1, preview:bool=True) -> str:
    """
    Opens mic stream using pyaudio and sends the audio stream to speed-to-text using google-cloud-speech client API and gets transcription in realtime. 
    ### Arguments:
    - ``credentials_path:`` /path/to/credentials.json file downloaded from gcloud project.
    - ``model:`` Select a model for your use case https://cloud.google.com/speech-to-text/docs/transcription-model. 
    - ``language_code:`` Select a language for your speech transcription https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages.
    - ``rate:`` Define the rate (in Hz) your audio input device use to capture audio. 
    - ``device_index:`` Select device by index, you want to use for capturing audio. 
    - ``channel:`` Specify number of channels used by your microphone. 
    - ``preview:`` Choose whether you want to preview the realtime response as you speak in microphone.
    ### Returns text transcribed by google-cloud-speech API.
    """
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=credentials_path
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=rate,
        language_code=language_code,
        model=model
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )
    with MicrophoneStream(channel, device_index, rate, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = client.streaming_recognize(streaming_config, requests)
        query = __listen_print_loop(responses, preview)
        return query
