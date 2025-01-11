# SONNET - Sound Network Negotiated Encoding Transmitter

SONNET is a Python library for encoding and decoding data through audio signals. It uses frequency-shift keying (FSK) to transmit digital data through sound waves, making it suitable for air-gapped data transfer or creative audio applications.

## Features

- Encode text data into audio signals
- Real-time audio signal decoding
- Multiple encoding modes (1, 2, or 3 bits per beep)
- Signal quality monitoring
- CRC32 checksum verification
- Automatic mode detection
- Transmission rate monitoring

## Installation

```bash
pip install sonnet-audio
```
# Quick Start
### Encoding Text to Audio
```python
from sonnet import text_to_sound

# Encode text file to audio
text_to_sound("input.txt", "output.wav", mode="3bpb")
```
### Decoding Realtime Audio
```python
from sonnet import SonnetDecoder
import pyaudio
import numpy as np

# Initialize decoder
decoder = SonnetDecoder()

# Set up PyAudio for input
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=512)

try:
    while True:
        # Read audio chunk
        data = stream.read(512)
        audio_data = np.frombuffer(data, dtype=np.float32)
        
        # Process the chunk
        result = decoder.process_chunk(audio_data)
        
        if result:
            if result['type'] == 'bits':
                print(f"Bits: {result['value']} ({result['quality']:.2f})")
            elif result['type'] == 'marker':
                print(f"Marker: {result['value']}")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
```   
## Advanced Usage
See the examples directory for more detailed usage examples.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request. 

## License
This project is licensed under the MIT License - see the LICENSE file for details.