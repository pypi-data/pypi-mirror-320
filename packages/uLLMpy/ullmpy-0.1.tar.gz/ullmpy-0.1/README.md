# uLLMpy - MicroPython LLM Access Library

`uLLMpy` is a MicroPython library designed for large language model (LLM) applications on ESP32S3 modules. It supports basic functionality like making HTTP requests, handling JSON, and timing operations for AI-related tasks.

## Requirements

- MicroPython v1.23.0
- ESP32 hardware

## Installation

To install the package, use the following command:

'pip install uLLMpy'


## Example Usage

```python
import uLLMpy


## Example Usage

```python
import uLLMpy


api_key = 'sk-emmmmm'

client = uLLMpy.DeepSeek(api_key=api_key)



client.chat("Who r u?", mode="new")


client.chat("I'm a coder.", mode="continue")


message='Do you support speak in Chinese?'
client.chat(message, mode="continue")

print(client.chat_history)





