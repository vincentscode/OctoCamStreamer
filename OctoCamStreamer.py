import requests
import io

import numpy as np
import cv2

import threading


class MjpegReader:
    def __init__(self, url: str):
        self._url = url

    def iter_content(self):
        r = requests.get(self._url, stream=True)

        # parse boundary
        content_type = r.headers['content-type']
        index = content_type.rfind("boundary=")
        assert index != 1
        boundary = content_type[index+len("boundary="):] + "\r\n"
        boundary = boundary.encode('utf-8')

        rd = io.BufferedReader(r.raw)
        while True:
            self._skip_to_boundary(rd, boundary)
            length = self._parse_length(rd)
            yield rd.read(length)

    def _parse_length(self, rd) -> int:
        length = 0
        while True:
            line = rd.readline()
            if line == b'\r\n':
                return length
            if line.startswith(b"Content-Length"):
                length = int(line.decode('utf-8').split(": ")[1])
                assert length > 0


    def _skip_to_boundary(self, rd, boundary: bytes):
        for _ in range(10):
            if boundary in rd.readline():
                break
        else:
            raise RuntimeError("Boundary not detected:", boundary)


def display_reader(reader, title, scale):
    iter_object = reader.iter_content()

    cv2.namedWindow(title, cv2.WINDOW_KEEPRATIO)

    for content in iter_object:
        image = cv2.resize(cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR), None, fx=scale, fy=scale, interpolation = cv2.INTER_LINEAR)

        if not cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) >= 1:
        	break

        cv2.imshow(title, image)
        
        if cv2.waitKey(1) == 27:
            break


def start_mjpeg_display_thread(url, title, scale):
    threading.Thread(target=display_reader, args=(MjpegReader(url), title, scale)).start()


start_mjpeg_display_thread("http://192.168.0.205:4747/video", "Main", 1 / 3)
# start_mjpeg_display_thread("http://192.168.0.149:8080/video", "Spool", 1 / 4)
print("Running.")