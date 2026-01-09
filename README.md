# Photo-pipeline

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)


<img src="banner.png" alt="Logo" width="300">

## Usage

**Install uv:** 
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Run Photo-pipeline:**
```
uv run process.py
```
or
```
photo-pipeline.bat
```


## Supported tools for photos

### FastRawViewer

- https://www.fastrawviewer.com/

### DXO PureRAW

- https://www.dxo.com/dxo-pureraw/

### Darktable

- https://www.darktable.org/

### exiftool

- https://exiftool.org/

## Supported tools for video

### DaVinci Resolve

- https://www.blackmagicdesign.com/fi/products/davinciresolve

### Shutter Encoder

- https://www.shutterencoder.com/

## Other resources

- Sony LUTs 
    - https://pro.sony/ue_US/technology/professional-video-lut-look-up-table#TEME170401LutsFromSony-professional-video-lut-look-up-table
- Flicker free video
    - https://www.red.com/tools#flicker-free-video

- Remember to add sqlite3 to PATH on Windows systems!