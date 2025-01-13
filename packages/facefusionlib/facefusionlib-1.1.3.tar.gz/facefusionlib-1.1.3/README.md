# FaceFuison Python Lib

[FaceFusion](https://github.com/facefusion/facefusion) is a very nice face swapper and enhancer.

## Requirements
```
python: >=3.9
```

## Installation

CPU support:
```
pip install facefusionlib
```

GPU support:

First of all, you need to check if your system supports the `onnxruntime-gpu`.

Go to [https://onnxruntime.ai](https://onnxruntime.ai) and check the installation matrix.

![Preview](https://raw.githubusercontent.com/IAn2018cs/sd-webui-facefusion/dev/.github/onnxruntime-installation-matrix.png)

If yes, just run:

```
pip install facefusionlib[gpu]
```

## Usage

```python
from facefusionlib import swapper
from facefusionlib.swapper import DeviceProvider

input_path = 'input.png'
target_path = 'target.png'

result = swapper.swap_face(
		source_paths=[input_path],
		target_path=target_path,
		provider=DeviceProvider.CPU,
		detector_score=0.65,
		mask_blur=0.7,
		skip_nsfw=True,
        landmarker_score=0.5
	)
print(result)
```
