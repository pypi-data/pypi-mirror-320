from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path

import os
import requests
import filetype
import imageio_ffmpeg


class AudiomaticError(Exception):
    """Custom exception for Audiomatic API errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        response_body: Optional[Dict[str, Any]] = None,
        request_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.response_body = response_body
        self.request_body = request_body

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status code: {self.status_code}")
        if self.error_code:
            parts.append(f"Error code: {self.error_code}")
        return " | ".join(parts)


class Audiomatic:
    """Client for interacting with the Audiomatic API.

    Args:
        api_key (str): The API key used for authentication.

    Attributes:
        base_url (str): Base URL for API endpoints.
        MAX_FILE_SIZE (int): Maximum allowed file size in bytes.
        MAX_DURATION (int): Maximum allowed duration in milliseconds.
        VALID_ACCENT_LEVELS (set): Valid accent level values.
    """

    API_VERSIONS = {"v1"}

    def __init__(self, api_key: str, api_version: str = "v1"):
        """Initialize the Audiomatic client."""

        if api_version not in self.API_VERSIONS:
            raise ValueError(f"API version must be one of: {self.API_VERSIONS}")

        self.api_version = api_version
        self.base_url = f"https://audiomatic.app/api/{api_version}"

        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

        # Constants
        self.MAX_FILE_SIZE = 500 * 1024 * 1024      # 500 MB
        self.MAX_DURATION = 0.25 * 3600 * 1000      # 15 minutes in milliseconds
        self.MAX_CAPTIONS_SIZE = 20 * 1024 * 1024   # 20 MB
        self.VALID_ACCENT_LEVELS = {0, 0.25, 0.5, 0.75, 1}

    def _make_request(
        self, method: str, endpoint: str, json_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make an API request and handle errors consistently."""

        try:
            response = self.session.request(
                method=method, url=f"{self.base_url}/{endpoint}", json=json_data
            )

            try:
                response_data = response.json() if response.content else {}
            except ValueError:
                response_data = {"raw_response": response.text}

            if not response.ok:
                error_message = response_data.get("error", "Unknown API error")
                raise AudiomaticError(
                    message=error_message,
                    status_code=response.status_code,
                    error_code=response_data.get("code"),
                    response_body=response_data,
                    request_body=json_data,
                )

            return response_data

        except requests.exceptions.RequestException as e:
            raise AudiomaticError(
                message=f"API request failed: {str(e)}", request_body=json_data
            )

    def _get_video_duration(self, file_path: str) -> int:
        """Get video duration in milliseconds."""
        try:
            # Get video info using ffprobe
            info = imageio_ffmpeg.count_frames_and_secs(file_path)
            duration_seconds = info[1]  # Second element is duration in seconds
            duration_ms = int(duration_seconds * 1000)

            if duration_ms <= 0:
                raise AudiomaticError("Could not determine video duration")

            if duration_ms > self.MAX_DURATION:
                raise AudiomaticError(
                    f"Video duration ({duration_ms/1000/60:.1f} minutes) exceeds "
                    f"maximum allowed duration of {self.MAX_DURATION/1000/60:.1f} minutes"
                )

            return duration_ms

        except Exception as e:
            raise AudiomaticError(f"Failed to get video duration: {str(e)}")

    def _validate_video_file(self, file_path: str) -> Tuple[int, str]:
        """Validate video file size and get mime type."""
        path = Path(file_path)
        if not path.exists():
            raise AudiomaticError(f"File not found: {file_path}")

        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise AudiomaticError(
                f"Video file size exceeds maximum allowed size of {self.MAX_FILE_SIZE/1024/1024}MB"
            )

        kind = filetype.guess(file_path)
        if kind is None:
            raise AudiomaticError("Unable to determine file type")

        mime_type = kind.mime
        if not (mime_type.startswith("audio/") or mime_type.startswith("video/")):
            raise AudiomaticError(
                f"Invalid file type: {mime_type}. Only audio and video files are accepted"
            )

        return file_size, mime_type
    
    def _validate_captions_file(self, file_path: str) -> Tuple[int, str]:
        """Validate video file size and get mime type."""
        path = Path(file_path)
        if not path.exists():
            raise AudiomaticError(f"File not found: {file_path}")

        file_size = path.stat().st_size
        if file_size > self.MAX_CAPTIONS_SIZE:
            raise AudiomaticError(
                f"Captions file size exceeds maximum allowed size of {self.MAX_CAPTIONS_SIZE/1024/1024}MB"
            )
        file_ext = path.suffix.lstrip('.')
        
        return file_size, file_ext

    def _validate_time_range(
        self, start_time: int, end_time: int, total_duration: int
    ) -> None:
        """Validate start and end times are within valid range."""
        if start_time < 0:
            raise AudiomaticError("Start time cannot be negative")
        if end_time > total_duration:
            raise AudiomaticError(
                f"End time ({end_time/1000:.1f}s) cannot exceed video duration ({total_duration/1000:.1f}s)"
            )
        if start_time >= end_time:
            raise AudiomaticError(
                f"Start time ({start_time/1000:.1f}s) must be less than end time ({end_time/1000:.1f}s)"
            )

    def _validate_accent_level(self, accent_level: float) -> None:
        """Validate accent level is one of the allowed values."""
        if accent_level not in self.VALID_ACCENT_LEVELS:
            raise AudiomaticError(
                f"Invalid accent level: {accent_level}. "
                f"Must be one of: {sorted(self.VALID_ACCENT_LEVELS)}"
            )

    def _upload_file(
        self, file_path: str, presigned_url: str
    ) -> None:
        """Upload a file to the provided pre-signed URL."""
        try:
            with open(file_path, "rb") as f:
                response = requests.put(
                    presigned_url, data=f
                )
                response.raise_for_status()
        except (IOError, requests.exceptions.RequestException) as e:
            raise AudiomaticError(f"Failed to upload file: {str(e)}")

    def translate(
        self,
        source: str,
        target_lang: str,
        project_name: Optional[str] = None,
        opt_params: Optional[Dict] = None,
    ) -> str:
        """Translate a video from a file path or YouTube URL.

        Args:
            source (str): Local file path or YouTube URL of the video to translate.
            target_lang (str): Target language code for translation.
            project_name (str, optional): Custom name for the translation project.
                If not provided, uses the source filename.
            opt_params (Dict, optional): Additional parameters for translation:
                - start_time (int): Start time in milliseconds
                - end_time (int): End time in milliseconds
                - accent_level (float): Voice accent level (0, 0.25, 0.5, 0.75, or 1)
                - num_speakers (int): Number of speakers in the video
                - remove_background_audio (bool): Whether to remove background audio
                - captions_path (str): Path to captions file

        Returns:
            str: Project ID for the translation job.

        Raises:
            AudiomaticError: If validation fails or API request fails.
        """

        opt_params = opt_params or {}
        is_youtube = source.startswith(("http://", "https://"))

        # Initialize variables
        video_file_size = None
        video_mime_type = None
        captions_file_size = None
        captions_file_ext = None
        video_duration = None

        if not is_youtube:
            # Validate video file and get duration
            video_file_size, video_mime_type = self._validate_video_file(source)
            video_duration = self._get_video_duration(source)

            # Validate time range
            start_time = opt_params.get("start_time", 0)
            end_time = opt_params.get("end_time", video_duration)
            self._validate_time_range(start_time, end_time, video_duration)

        # Validate accent level if provided
        if "accent_level" in opt_params:
            self._validate_accent_level(opt_params["accent_level"])

        # Handle captions if provided
        captions_path = opt_params.get("captions_path")
        if captions_path:
            captions_file_size, captions_file_ext = self._validate_captions_file(captions_path)
        
        # Start and end times if provided
        start_time = opt_params.get("start_time", 0)
        end_time = opt_params.get("end_time", video_duration)

        # Step 1: Call /create-project
        create_project_payload = {
            "APIKey": self.api_key,
            "videoLink": source if is_youtube else None,
            "fileName": os.path.basename(source) if not is_youtube else None,
            "sourceLang": "auto",  # Could be made configurable
            "targetLang": target_lang,
            "projectName": project_name or os.path.basename(source),
            "totalDuration": video_duration,
            "startTime": start_time,
            "endTime": end_time,
            "videoFileSize": video_file_size,
            "fileMimeType": video_mime_type,
            "captionsFileSize": captions_file_size,
            "captionsMimeType": captions_file_ext,
        }

        projects_response = self._make_request(
            "POST", "create-project", create_project_payload
        )

        # Upload video if local file
        if not is_youtube:
            if "videoURL" not in projects_response:
                raise AudiomaticError("No pre-signed URL received for video upload")
            self._upload_file(source, projects_response["videoURL"])

        # Upload captions if provided
        if captions_path:
            self._upload_file(
                captions_path, projects_response["captionsURL"]
            )

        if is_youtube:
            video_duration = projects_response["totalDuration"]

        # Step 2: Call /translate
        translate_payload = {
            "APIKey": self.api_key,
            "projectID": projects_response["projectID"],
            "videoLink": source if is_youtube else None,
            "cfVideoPath": projects_response.get("cfVideoPath"),
            "cfCaptionsPath": projects_response.get("cfCaptionsPath"),
            "targetLang": target_lang,
            "thumbnailURL": projects_response["thumbnailURL"] if is_youtube else "",
            "totalDuration": video_duration,
            "numSpeakers": opt_params.get("num_speakers", 1),
            "accentLevel": opt_params.get("accent_level", 0),
            "removeBackgroundAudio": opt_params.get("remove_background_audio", False),
            "addWatermark": projects_response.get("addWatermark", True),
            "startTime": start_time,
            "endTime": end_time if end_time else video_duration,
        }

        self._make_request("POST", "translate", translate_payload)
        return projects_response["projectID"]

    def get_status(self, project_id: str) -> Tuple[str, Optional[str]]:
        """Get the status and result URL of a translation request.

        Args:
            project_id (str): The project ID returned from translate().

        Returns:
            Tuple[str, Optional[str]]: A tuple containing:
                - Status string ('PENDING', 'PROCESSING', 'SUCCEEDED', 'FAILED')
                - Result URL if status is 'SUCCEEDED', 'n/a' otherwise

        Raises:
            AudiomaticError: If the API request fails.
        """

        status_data = self._make_request(
            "POST", "check-status", {"APIKey": self.api_key, "projectID": project_id}
        )
        status = status_data.get("status", "not found")
        result_url = (
            status_data.get("export_url", "n/a") if status == "SUCCEEDED" else "n/a"
        )

        return status, result_url
    
    def get_all_projects(self) -> List[Dict[str, str]]:
        """Gets all projects associated with the current API key.
        
        Makes a POST request to the 'get-all-projects' endpoint to retrieve all projects
        associated with the provided API key.
        
        Args:
            None
            
        Returns:
            List[Dict[str, str]]: A list of project dictionaries, where each dictionary contains:
                - projectID (str): Unique identifier for the project
                - projectName (str): Name of the project
                - createdAt (str): ISO format timestamp of project creation (UTC)
                
        Raises:
            AudiomaticError: If the API request fails or returns an invalid response.
       """

        projects_data = self._make_request(
            "POST", "get-all-projects", {"APIKey": self.api_key}
        )
        projects = projects_data.get("projects", "not found")

        return projects

    def delete_project(self, project_id: str) -> None:
        """Deletes a project.
        
        Args:
            project_id (str): The project ID returned from translate().
            
        Returns:
            None
                
        Raises:
            AudiomaticError: If the API request fails.
        """
        self._make_request(
            "POST", "delete-project", {"APIKey": self.api_key, "projectID": project_id}
        )
        return