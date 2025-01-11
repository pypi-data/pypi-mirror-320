# audiomatic-python

The official Python library for the Audiomatic API

## Installation

```bash
pip install -U audiomatic
```

## Quick Start

```python
from audiomatic import Audiomatic

# Initialize the client
client = Audiomatic(api_key="your_api_key")

# Translate a local video file
project_id = client.translate(
    source="path/to/video.mp4",
    target_lang="es",
    project_name="Spanish Translation"
)

# Check translation status
status, result_url = client.get_status(project_id)
```

## Usage Examples

### Translating a YouTube Video

```python
# Translate a YouTube video to French
project_id = client.translate(
    source="https://youtube.com/watch?v=example",
    target_lang="fr",
    project_name="French Translation"
)
```

### Advanced Options

```python
# Translate with custom options
project_id = client.translate(
    source="path/to/video.mp4",
    target_lang="de",
    project_name="German Translation",
    opt_params={
        "accent_level": 0.75,
        "num_speakers": 2,
        "remove_background_audio": True,
        "start_time": 30000,  # Start at 30 seconds
        "end_time": 120000,   # End at 2 minutes
        "captions_path": "path/to/captions.vtt"
    }
)
```

## API Reference

### Client Initialization

#### `Audiomatic(api_key: str)`

Initialize the Audiomatic client.

**Parameters:**
- `api_key` (str): Your Audiomatic API key

### Methods

#### `translate(source: str, target_lang: str, project_name: Optional[str] = None, opt_params: Optional[Dict] = None) -> str`

Translate a video file or YouTube URL.

**Parameters:**
- `source` (str): Path to local video file or YouTube URL
- `target_lang` (str): Target language code (e.g., "es", "fr", "de")
- `project_name` (str, optional): Custom project name (defaults to filename)
- `opt_params` (Dict, optional): Additional parameters:
  - `accent_level` (float): Voice accent level (0, 0.25, 0.5, 0.75, or 1)
  - `num_speakers` (int): Number of speakers in video (defaults to auto-detect)
  - `remove_background_audio` (bool): Whether to remove background audio
  - `start_time` (int): Start time of video clip in milliseconds
  - `end_time` (int): End time of video clip in milliseconds
  - `captions_path` (str): Path to custom captions file

**Returns:** Project ID string

#### `get_status(project_id: str) -> Tuple[str, Optional[str]]`

Check the status of a translation project.

**Parameters:**
- `project_id` (str): Project ID returned from translate()

**Returns:** Tuple of (status, result_url)

## Limitations

- Maximum file size: 500MB
- Maximum video duration: 15 minutes
- Supported languages: ['en', 'fr', 'es', 'de', 'pt', 'zh', 'ja', 'hi', 'it', 'ko', 'nl', 'pl', 'ru', 'sv', 'tr']
- Supported accent levels:[0, 0.25, 0.5, 0.75, 1]

## Error Handling

The client includes a custom `AudiomaticError` exception class that provides detailed error information:

```python
try:
    project_id = client.translate(...)
except AudiomaticError as e:
    print(f"Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Error Code: {e.error_code}")
```