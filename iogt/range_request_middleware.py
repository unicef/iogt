import os
import re
import mimetypes

from django.conf import settings
from django.http import StreamingHttpResponse, FileResponse


class RangeRequestMiddleware:
    """
    Middleware that adds HTTP Range request support for media file responses.

    When iOS Safari requests a video, it sends:
        GET /media/video.mp4
        Range: bytes=0-1

    It expects a 206 Partial Content response. If it gets a 200 with the
    full file, it will refuse to play the video.

    This middleware intercepts FileResponse objects for media files and
    converts them to proper 206 Partial Content responses when a Range
    header is present.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only process Range requests for media file paths
        if not self._is_media_request(request):
            return response

        # Add Accept-Ranges header to all media responses
        response['Accept-Ranges'] = 'bytes'

        range_header = request.META.get('HTTP_RANGE', '')
        if not range_header:
            return response

        print(f"RangeRequestMiddleware: Intercepting range header {range_header} for path {request.path}")

        # Only handle successful FileResponse (actual file serving)
        if not isinstance(response, FileResponse) or response.status_code != 200:
            print(f"RangeRequestMiddleware: Response is not a 200 FileResponse, type is {type(response)}, status is {getattr(response, 'status_code', 'unknown')}")
            return response

        # Parse the Range header
        range_match = re.match(r'bytes=(\d*)-(\d*)', range_header)
        if not range_match:
            print("RangeRequestMiddleware: Invalid range header format")
            return response

        try:
            file_path = self._get_file_path(request, response)
            if not file_path or not os.path.isfile(file_path):
                return response

            file_size = os.path.getsize(file_path)

            range_start_str, range_end_str = range_match.groups()
            range_start = int(range_start_str) if range_start_str else 0
            range_end = int(range_end_str) if range_end_str else file_size - 1

            # Validate range
            if range_start >= file_size:
                response.status_code = 416  # Range Not Satisfiable
                response['Content-Range'] = f'bytes */{file_size}'
                return response

            range_end = min(range_end, file_size - 1)
            content_length = range_end - range_start + 1

            # Read the requested byte range
            with open(file_path, 'rb') as f:
                f.seek(range_start)
                data = f.read(content_length)

            # Determine content type
            content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

            # Build the 206 Partial Content response
            range_response = StreamingHttpResponse(
                iter([data]),
                status=206,
                content_type=content_type,
            )
            range_response['Content-Length'] = content_length
            range_response['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'
            range_response['Accept-Ranges'] = 'bytes'

            # Preserve cache and other headers from the original response
            for header in ('Cache-Control', 'Last-Modified', 'ETag'):
                if header in response:
                    range_response[header] = response[header]

            return range_response

        except (ValueError, IOError, OSError):
            # If anything goes wrong, fall back to the normal response
            return response

    def _is_media_request(self, request):
        """Check if the request is for a media file."""
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        return request.path.startswith(media_url)

    def _get_file_path(self, request, response):
        """
        Extract the file path from a FileResponse.

        FileResponse stores the file object, which may have a .name attribute
        pointing to the file on disk.
        """
        # FileResponse wraps a file-like object
        if hasattr(response, 'file_to_stream_with_sendfile'):
            file_obj = response.file_to_stream_with_sendfile
            if hasattr(file_obj, 'name'):
                return file_obj.name

        # Try to resolve from the request path
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        media_url = getattr(settings, 'MEDIA_URL', '/media/')

        if hasattr(request, 'path'):
            relative_path = request.path.replace(media_url, '', 1)
            return os.path.join(media_root, relative_path)

        # Fallback: try to get path from the streaming content
        streaming_content = getattr(response, 'streaming_content', None)
        if streaming_content:
            file_obj = getattr(response, 'file_to_stream_with_sendfile', None)
            if file_obj and hasattr(file_obj, 'name'):
                return file_obj.name

        return None
