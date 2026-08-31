"""Convert the brand logo to a trimmed PNG with a transparent background."""

import struct
import sys
import zlib
from collections import deque

SOURCE = sys.argv[1]
TARGET = sys.argv[2]
WHITE = 232


def read_png(path: str) -> tuple[int, int, bytearray]:
    raw = open(path, 'rb').read()
    assert raw[:8] == b'\x89PNG\r\n\x1a\n', 'not a png'
    offset = 8
    header = None
    data = b''
    while offset < len(raw):
        length, kind = struct.unpack('>I4s', raw[offset:offset + 8])
        payload = raw[offset + 8:offset + 8 + length]
        if kind == b'IHDR':
            header = struct.unpack('>IIBBBBB', payload)
        elif kind == b'IDAT':
            data += payload
        offset += 12 + length
    width, height, depth, color, compression, filtering, interlace = header
    assert depth == 8 and color in (2, 6) and interlace == 0, header
    channels = 3 if color == 2 else 4
    stream = zlib.decompress(data)
    stride = width * channels
    pixels = bytearray(width * height * 4)
    previous = bytearray(stride)
    position = 0
    for row in range(height):
        filter_type = stream[position]
        position += 1
        line = bytearray(stream[position:position + stride])
        position += stride
        for index in range(stride):
            left = line[index - channels] if index >= channels else 0
            up = previous[index]
            up_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                line[index] = (line[index] + left) & 0xFF
            elif filter_type == 2:
                line[index] = (line[index] + up) & 0xFF
            elif filter_type == 3:
                line[index] = (line[index] + ((left + up) >> 1)) & 0xFF
            elif filter_type == 4:
                estimate = left + up - up_left
                distance_left = abs(estimate - left)
                distance_up = abs(estimate - up)
                distance_up_left = abs(estimate - up_left)
                if distance_left <= distance_up and distance_left <= distance_up_left:
                    predictor = left
                elif distance_up <= distance_up_left:
                    predictor = up
                else:
                    predictor = up_left
                line[index] = (line[index] + predictor) & 0xFF
        for column in range(width):
            source = column * channels
            target = (row * width + column) * 4
            pixels[target] = line[source]
            pixels[target + 1] = line[source + 1]
            pixels[target + 2] = line[source + 2]
            pixels[target + 3] = line[source + 3] if channels == 4 else 255
        previous = line
    return width, height, pixels


def clear_background(width: int, height: int, pixels: bytearray) -> None:
    def is_white(index: int) -> bool:
        return pixels[index] >= WHITE and pixels[index + 1] >= WHITE and pixels[index + 2] >= WHITE

    seen = bytearray(width * height)
    queue = deque()
    for column in range(width):
        for row in (0, height - 1):
            queue.append(row * width + column)
    for row in range(height):
        for column in (0, width - 1):
            queue.append(row * width + column)
    while queue:
        cell = queue.popleft()
        if seen[cell] or not is_white(cell * 4):
            continue
        seen[cell] = 1
        pixels[cell * 4 + 3] = 0
        column, row = cell % width, cell // width
        if column > 0:
            queue.append(cell - 1)
        if column < width - 1:
            queue.append(cell + 1)
        if row > 0:
            queue.append(cell - width)
        if row < height - 1:
            queue.append(cell + width)


def bounding_box(width: int, height: int, pixels: bytearray) -> tuple[int, int, int, int]:
    left, top, right, bottom = width, height, -1, -1
    for row in range(height):
        for column in range(width):
            if pixels[(row * width + column) * 4 + 3]:
                left = min(left, column)
                right = max(right, column)
                top = min(top, row)
                bottom = max(bottom, row)
    return left, top, right, bottom


def write_png(path: str, width: int, height: int, pixels: bytes) -> None:
    raw = bytearray()
    stride = width * 4
    for row in range(height):
        raw.append(0)
        raw += pixels[row * stride:(row + 1) * stride]

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))

    header = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    body = zlib.compress(bytes(raw), 9)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', body) + chunk(b'IEND', b''))


width, height, pixels = read_png(SOURCE)
clear_background(width, height, pixels)
left, top, right, bottom = bounding_box(width, height, pixels)
cropped_width, cropped_height = right - left + 1, bottom - top + 1
cropped = bytearray()
for row in range(top, bottom + 1):
    start = (row * width + left) * 4
    cropped += pixels[start:start + cropped_width * 4]
write_png(TARGET, cropped_width, cropped_height, bytes(cropped))
print('wrote', TARGET, cropped_width, 'x', cropped_height)
