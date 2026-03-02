import requests

class WhisperClient:
    """
    A client for communicating with the Whisper Speech-to-Text (STT) microservice.
    """
    def __init__(self, url="http://whisper:9000/asr", timeout=60):
        """
        Initializes the WhisperClient.
        
        Args:
            url (str): The endpoint URL of the Whisper API.
            timeout (int): The maximum time (in seconds) to wait for a response.
        """
        self.url = url
        self.timeout = timeout # Даем Whisper до минуты на обработку

    def transcribe(self, file_path: str) -> str:
        """
        Sends an audio file to the Whisper API for transcription.
        
        Args:
            file_path (str): The local path to the audio file to be transcribed.
            
        Returns:
            str: The transcribed text. Returns an empty string if transcription fails or times out.
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'audio_file': f}
                # Ставим таймаут, чтобы воркер не завис навсегда
                response = requests.post(
                    self.url, 
                    files=files, 
                    params={'task': 'transcribe', 'output': 'json'},
                    timeout=self.timeout 
                )
                response.raise_for_status()
                return response.json().get("text", "").strip()
        except requests.exceptions.Timeout:
            # Логируем, что сервис слишком долго думает
            return ""
        except requests.exceptions.RequestException:
            # Ошибки сети
            return ""
