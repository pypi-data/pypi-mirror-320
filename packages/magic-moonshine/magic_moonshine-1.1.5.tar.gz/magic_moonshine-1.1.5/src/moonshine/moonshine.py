# moonshine.py
import os
import imghdr
import base64
import urllib.parse
import requests
import mimetypes
import dataclasses
from typing import Dict, Optional, Callable, Any, Union
import cv2
import math
import asyncio
import json

# Private configuration
_CONFIG = {
    'api_token': None
}

_MULTIPART_UPLOAD_THRESHOLD = 50 * 1024 * 1024 * 10000000  # 50 MB * 10000000
_PART_SIZE = 15 * 1024 * 1024  # 15 MB
_MAX_CONCURRENT_UPLOADS = 5

@dataclasses.dataclass
class VideoTarget:
    """
    Represents a video target for Moonshine tasks.
    
    Attributes:
        file_id (str): The target video ID.
        timestamp (Optional[float]): The target timestamp. Defaults to None.
    
    Raises:
        ValueError: If file_id is not provided.
    """
    file_id: str
    timestamp: Optional[float] = None

    def __post_init__(self):
        """
        Validate that both timestamp and file_id are provided.
        
        This method is automatically called after object initialization.
        """
        if self.file_id is None:
            raise ValueError("File ID must be provided")

# Private helper functions
def _is_video(filename: str) -> bool:
    """Determine if a file is a video based on its extension."""
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'}
    return os.path.splitext(filename.lower())[1] in video_extensions

def _get_video_info(filename: str) -> tuple[Optional[float], Optional[float]]:
    """Get video duration in seconds and FPS using OpenCV."""
    try:
        video = cv2.VideoCapture(filename)
        if not video.isOpened():
            return None, None
            
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        video.release()
        
        return duration, fps
        
    except Exception as e:
        print(f"Error reading video file: {e}")
        return None, None
    
def _does_bucket_exist(index: str) -> bool:
    """
    Check if a bucket exists in the Moonshine API.
    
    Args:
        index (str): The index to check
    
    Returns:
        bool: True if the bucket exists, False otherwise
        
    Raises:
        ValueError: If API token is not configured
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    base_url = "https://www.moonshine-edge-compute.com/does-group-exist"
    
    payload = {
        'token': _CONFIG['api_token'], 
        'index': index
    }
    
    try:
        # Use a POST request with JSON payload
        response = requests.post(base_url, json=payload)
        response.raise_for_status()
        return response.json().get('exists', False)
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")

def _get_file_info(filepath: str) -> tuple[int, str]:
    """Determine which bucket to use based on file size and type."""
    file_size = os.path.getsize(filepath)
    content_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
    
    return file_size, content_type

def _upload_part(s3_client: Any, bucket: str, key: str, upload_id: str, 
                part_number: int, data: bytes) -> Dict:
    """Upload a single part of a multipart upload."""
    response = s3_client.upload_part(
        Bucket=bucket,
        Key=key,
        UploadId=upload_id,
        PartNumber=part_number,
        Body=data
    )
    return {
        'PartNumber': part_number,
        'ETag': response['ETag']
    }
    
async def _upload_remote_file(
    src: str, 
    index: str, 
    progress_callback: Optional[Callable[[dict], None]] = None
) -> Optional[str]:
    """Upload a remote file using a signed URL."""
    
    if not _CONFIG.get('api_token'):
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")

    url = "https://moonshine-edge-compute.com/remote-upload"
    event_payload = {
        "url": src,
        "index": index,
        "token": _CONFIG.get('api_token')
    }
    
    file_id = None
    file_size = None

    # Define a function to process the server-sent events (SSE)
    def process_sse(response):
        for line in response.iter_lines():
            if line: 
                try:
                    data_str = line.decode('utf-8').strip()
                    if data_str.startswith("data: "):
                        data_str = data_str[6:]
                        update = json.loads(data_str)
                        if update.get('type') == 'error':
                            return print(f"Error: {update}")
                        
                        if update.get('type') == 'metadata':
                            nonlocal file_size
                            file_size = update.get('fileSize')
                            print(f"Video duration: {update.get('duration')} seconds")
                            print(f"Video FPS: {update.get('fps')}")
                        
                        if update.get('type') == 'file_authorized':
                            nonlocal file_id
                            file_id = update.get('key')
                        
                        if progress_callback and update.get('type') == 'progress':
                            progress_callback({
                                'status': 'uploading',
                                'progress': update.get('percentage', 0),
                                'src': src,
                                'file_id': file_id
                            })
                            
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    continue

    # Make the POST request and stream the response
    response = requests.post(url, json=event_payload, stream=True)

    if response.status_code == 200:
        process_sse(response)
        return file_id, float(file_size[:-3]) > 650
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
    
async def _get_signed_upload(
    filename: str, index: str, duration: Optional[float] = None,
    fps: Optional[int] = None, file_size: Optional[int] = None,
    content_type: Optional[str] = None
) -> Optional[str]:
    """Call the pre-upload API to get a file ID."""
    base_url = 'https://moonshine-edge-compute.com/api-pre-upload'
    payload = {
        "filename": filename,
        "index": index,
        "duration": math.ceil(duration) if duration else None,
        "fps": round(fps) if fps else None,
        "filesize": file_size,
        "content": content_type or "application/octet-stream"
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(base_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('key'), data.get('url')
    except requests.RequestException as e:
        raise requests.RequestException(f"Error in API call: {str(e)}")

# Public functions
def moo() -> None:
    """Print a cow saying hello."""
    print("  __________________")
    print(" < MOO, its Harold! >")
    print("  ------------------")
    print("         \\   ^__^")
    print("          \\  (oo)\\_______")
    print("             (__)\\       )\\/\\")
    print("                 ||----w |")
    print("                 ||     ||")

def config(API: str) -> None:
    """
    Configure the Moonshine client with your API token.
    
    Args:
        API (str): Your Moonshine API token
    """
    base_url = "https://www.moonshine-edge-compute.com/check-token"
    
    params = {
        'token': API,
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        if (response.json()["valid"]):
            _CONFIG['api_token'] = API
        else:
            raise ValueError("Invalid API token")
    except requests.RequestException as e:
        raise requests.RequestException(f"Could not validate your token: {str(e)}")

def create(bucket: str) -> Dict:
    """
    Create a new Moonshine index.
    
    Args:
        bucket (str): The project/bucket to create
    
    Returns:
        Dict: The API response
        
    Raises:
        ValueError: If API token is not configured
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    if _does_bucket_exist(bucket):
        raise ValueError(f"Index {bucket} already exists.")
    
    base_url = "https://www.moonshine-edge-compute.com/create-media-group"
    
    params = {
        'userid': _CONFIG['api_token'],
        'projectname': _CONFIG['api_token'] + bucket,
        'projectdescription': "api",
        'from': "api",
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")
    
    
def inquire(index: str, prompt: str, guidance: Optional[str] = None, 
            target: Optional[VideoTarget] = None) -> str:
    """
    Generate responses to a prompt using a Moonshine index.
    
    Args:
        index (str): The project/bucket ID to search in
        prompt (str): The prompt query
        guidance (str): Optional guidance to match your expected output
        target (VideoTarget): Optional grounding target timestamp 
    
    Returns:
        str: The API response
        
    Raises:
        ValueError: If API token is not configured
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    base_url = "https://www.moonshine-edge-compute.com/search-and-generate"
    
    # Build request payload
    payload = {
        'project_id': _CONFIG['api_token'] + index,
        'prompt': prompt,
    }
    
    if guidance:
        payload['guidance'] = guidance
    
    if target:
        if isinstance(target, VideoTarget):
            if target.timestamp is not None:
                payload['target'] = target.timestamp
            if target.file_id is not None:
                payload['target_video'] = target.file_id
        else:
            raise ValueError("Target must be a VideoTarget object. Hint: moonshine.VideoTarget(timestamp, file_id)")
    
    try:
        response = requests.post(
            base_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=3000
        )
        response.raise_for_status()
        return response.json()['output']
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")

def search(index: str, query: str = None, image: str = None) -> Dict:
    """
    Search media using the Moonshine API. Supports both text and image-based searches.
    
    Args:
        index (str): The project/bucket ID to search in
        query (str, optional): The text search query
        image (str, optional): Path to the image file for visual search
    
    Returns:
        Dict: The API response
        
    Raises:
        ValueError: If API token is not configured or if neither query nor image is provided
        FileNotFoundError: If the image file doesn't exist
        TypeError: If the provided file is not a valid image
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    if query is None and image is None:
        raise ValueError("Either 'query' or 'image' parameter must be provided")
        
    # Text-based search
    if query is not None:
        base_url = "https://www.moonshine-edge-compute.com/media-query"
        
        params = {
            'projectid': _CONFIG['api_token'] + index,
            'api': _CONFIG['api_token'],
            'query': query,
            'numargs': 5,
            'threshold': 1000
        }
        
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"API request failed: {str(e)}")
    
    # Image-based search
    else:
        # Validate image file exists
        if not os.path.exists(image):
            raise FileNotFoundError(f"Image file not found: {image}")
        
        # Validate file is actually an image
        image_type = imghdr.what(image)
        if image_type is None:
            raise TypeError(f"File is not a valid image: {image}")
            
        # Read and encode image
        try:
            with open(image, 'rb') as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to read or encode image: {str(e)}")
        
        base_url = "https://www.moonshine-edge-compute.com/search-with-image"
        
        payload = {
            'project_id': _CONFIG['api_token'] + index,
            'image': base64_image
        }
        
        try:
            response = requests.post(base_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"API request failed: {str(e)}")

async def upload(src: str, index: str, 
                progress_callback: Optional[Callable[[dict], None]] = None) -> Union[str, bool]:
    """
    Upload a file from either a local path or remote URL with progress tracking.
    
    Args:
        src: Local file path or remote URL of the file to upload
        index: Project name/ID
        progress_callback: Optional callback function to report upload progress with detailed status
        
    Returns:
        str: File ID if upload successful
        bool: False if upload failed
        
    Raises:
        ValueError: If API token is not configured or project doesn't exist
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    if not _does_bucket_exist(index):
        raise ValueError(f"Index {index} doesn't exist. Create it first. Hint: moonshine.create('{index}')")
    
    index = _CONFIG['api_token'] + index
    file_id = None  # Initialize file_id to be accessible throughout the function
    
    try:
        # Handle remote URL vs local file path
        if src.startswith(('http://', 'https://')):
            file_id, is_large = await _upload_remote_file(src, index[60:], progress_callback)
            if not file_id:
                raise ValueError("Remote file upload failed")
            
            if progress_callback:
                progress_callback({
                    'status': 'uploading',
                    'progress': 100,
                    'src': src,
                    'file_id': file_id
                })
                
            large_file = is_large
                
        else:
            # Original local file upload logic
            filename = os.path.basename(src)
            file_size = os.path.getsize(src)
            # Get file metadata
            duration = None
            fps = None
            file_size, content_type = _get_file_info(src)
            large_file = file_size > 1e9
            
            if _is_video(src) and content_type.startswith('video/'):
                duration, fps = _get_video_info(src)
                print(f"Video duration: {duration:.2f} seconds")
                print(f"Video FPS: {fps:.2f}")
                
                if large_file:
                    print("WARNING: This is a large format video file that will be transcoded before indexing. Indexing times may take longer.")
                
            else:
                raise ValueError("Only video files are supported.")
            
            # Get signed upload URL
            file_upload = await _get_signed_upload(filename, index, duration, fps, file_size, content_type)
            
            if not file_upload:
                raise ValueError("Unable to index media, insufficient account balance.")
            
            file_id, signed_upload_url = file_upload
            
            # Configure the requests session for uploads
            session = requests.Session()
            
            if file_size < _MULTIPART_UPLOAD_THRESHOLD:
                # Single-part upload
                with open(src, 'rb') as file:
                    response = session.put(
                        signed_upload_url,
                        data=_ProgressFileReader(file, file_size, 
                            lambda progress: progress_callback({
                                'status': 'uploading',
                                'progress': progress,
                                'src': src,
                                'file_id': file_id
                            }) if progress_callback else None),
                        headers={'Content-Type': content_type}
                    )
                    response.raise_for_status()
            
            if progress_callback:
                progress_callback({
                    'status': 'uploading',
                    'progress': 100,
                    'src': src,
                    'file_id': file_id
                })
        
        # Common post-upload processing for both local and remote files
        # Check transcoding status every 4 seconds
        while True and large_file:
            response = requests.get(
                'https://moonshine-edge-compute.com/compress-status',
                params={'video': file_id.split('.')[0]}
            )
            
            try:
                processing_status = int(response.json()['status'])
            except:
                processing_status = 0
            
            if progress_callback:
                progress_callback({
                    'status': 'transcoding',
                    'progress': min(math.floor(processing_status * (fps/30)), 100) if 'fps' in locals() else processing_status,
                    'src': src,
                    'file_id': file_id
                })
            
            # Check if indexing is complete
            if processing_status >= 100:
                break
                
            # Wait 4 seconds before next check
            await asyncio.sleep(4)
            
        # Check indexing status every 4 seconds
        while True:
            response = requests.get(
                'https://moonshine-edge-compute.com/status',
                params={'file_id': file_id}
            )
            processing_status = response.json()['status']
            processing_status = [int(status) for status in processing_status]
            
            # Calculate average progress (rounded down)
            avg_progress = math.floor(sum(processing_status) / len(processing_status))
            
            if progress_callback:
                progress_callback({
                    'status': 'indexing',
                    'progress': avg_progress,
                    'src': src,
                    'file_id': file_id
                })
            
            # Check if indexing is complete
            if avg_progress >= 100:
                break
                
            # Wait 4 seconds before next check
            await asyncio.sleep(4)
        
        return file_id
        
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return False
    
def remove(index: str, video_id: str) -> Dict:
    """
    Remove a video from the Moonshine index permanently.
    
    Args:
        index (str): The project/bucket ID where the video resides
        video_id (str): The ID of the video to be removed
    
    Returns:
        Dict: The API response indicating success or failure
        
    Raises:
        ValueError: If API token is not configured
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    base_url = "https://www.moonshine-edge-compute.com/remove-from-index"
    
    payload = {
        'token': _CONFIG['api_token'],
        'project_id': index,
        'video_id': video_id
    }
    
    try:
        response = requests.post(
            base_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        # Parse and return the JSON response
        return response.json()
    
    except requests.HTTPError as e:
        # Handle specific HTTP errors based on status code
        if e.response.status_code == 400:
            raise ValueError("Invalid token provided.")
        elif e.response.status_code == 404:
            error_details = e.response.json().get('error', 'Unknown error')
            raise ValueError(f"Error: {error_details}")
        else:
            raise requests.RequestException(f"Unexpected HTTP error: {e.response.text}")
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")

class _ProgressFileReader:
    """Wrapper for file object that reports read progress only when whole number percentage changes."""
    def __init__(self, file, total_size, callback=None):
        self.file = file
        self.total_size = total_size
        self.callback = callback
        self.bytes_read = 0
        self.last_reported_progress = -1  # Initialize to -1 to ensure first progress is reported
        
    def __iter__(self):
        return self
    
    def __next__(self):
        data = self.read(8192)  # Read in 8KB chunks
        if not data:
            raise StopIteration
        return data
    
    def read(self, size=-1):
        data = self.file.read(size)
        self.bytes_read += len(data)
        
        if self.callback:
            # Calculate current progress rounded down to nearest whole number
            current_progress = int(self.bytes_read / self.total_size * 100)
            
            # Only call callback if the whole number progress has changed
            if current_progress > self.last_reported_progress:
                self.last_reported_progress = current_progress
                self.callback(current_progress)
        
        return data
    
    def __len__(self):
        return self.total_size

async def _upload_part_with_signed_url(
    session: requests.Session,
    signed_url: str,
    part_number: int,
    data: bytes,
    content_type: str
) -> str:
    """Upload a single part using a signed URL."""
    response = session.put(
        signed_url,
        data=data,
        headers={'Content-Type': content_type}
    )
    response.raise_for_status()
    return response.headers['ETag']