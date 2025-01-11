# SoyleApp

SoyleApp is a Python library for interacting with the Soyle Translation API, available at [soyle.nu.edu.kz](https://soyle.nu.edu.kz/). Before using this library, you must register on the website and obtain an API token. The resources consumed by the library will be tied to your account.

## Features
- Translate text between multiple languages.
- Convert text into audio with options for male or female voice.

## Installation
Once the library is published, install it via pip:

```bash
pip install SoyleApp
```

## Usage
Here's how to use the library:

```python
from SoyleApp import SoyleApp

# Create a client with your API token
translator = SoyleApp("your-api-token")

# Translate text to text
translated_text = translator.text_translate(
    source_language="eng", target_language="kaz", text="Hello, world!"
)
print("Translated text:", translated_text)

# Translate text to audio
audio_base16 = translator.audio_translate(
    source_language="eng", target_language="kaz", text="Hello, world!", voice="female"
)

# Save the audio to a file
with open("output_audio.wav", "wb") as audio_file:
    audio_file.write(bytes.fromhex(audio_base16))
print("Audio saved as output_audio.wav")

```

## Note
- You need to register at [soyle.nu.edu.kz](https://soyle.nu.edu.kz/) to get an API token.
- All resource usage is tied to your account, so use your token responsibly.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

