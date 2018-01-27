#!/usr/bin/env python2

"""A utility for padding PNG images"""

import binascii
import os
import struct
import sys
import zlib

from argparse import ArgumentParser

class FileReader(object):
    """Create a new object which can read from a file, tracking offset."""

    def __init__(self, path):
        """Create a new file reader object."""
        self.path = path
        self.file_size = os.path.getsize(path)
        self.offset = 0
        self.file_handle = None

    def __enter__(self):
        self.file_handle = open(self.path, 'rb')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file_handle.close()

    def read_bytes(self, count):
        """Read bytes from the file."""
        self.offset += count
        return self.file_handle.read(count)

    def read_hex(self, count):
        """Read bytes from the file and convert to a hex string."""
        return self.read_bytes(count).encode('hex')

    def read_ascii(self, count):
        """Read bytes from the file and convert to an ASCII string."""
        return self.read_bytes(count).encode('ascii')

    def read_int(self):
        """Read a 4 byte int from the file."""
        return int(self.read_hex(4), 16)

    def has_bytes_remaining(self):
        """Return True if there are bytes remaining in the file."""
        return self.offset < self.file_size


class PNGFile(object):
    """Represents a PNG file."""

    HEADER = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]

    def __init__(self, path):
        """Create a new PNG file."""
        self.path = path
        self.file_size = os.path.getsize(path)
        self.chunks = None
        self.header = None

        if not os.path.exists(path):
            raise IOError("Input image does not exist.")

        self._load_image()

    def _load_image(self):
        """Load the image from the path."""
        try:
            with FileReader(self.path) as reader:
                chunks = self._parse_file(reader)
                return chunks
        except IOError:
            print "Failed to read input file"
        self.chunks = chunks

    def _parse_file(self, file_reader):
        """Parse a PNG file into chunks."""

        chunks = []

        # Read the header
        self.header = file_reader.read_bytes(len(PNGFile.HEADER))
        header_bytes = map(ord, self.header)
        if header_bytes != PNGFile.HEADER:
            raise ValueError("Image is not a PNG file")

        # Read the chunks
        while file_reader.has_bytes_remaining():
            chunk_length = file_reader.read_int()
            chunk_name = file_reader.read_ascii(4)
            content = file_reader.read_bytes(chunk_length)
            crc_value = file_reader.read_int()
            chunks.append((chunk_name, content, crc_value))

        self.chunks = chunks

    def pad_by(self, count):
        """Pad the image by the size specified."""

        if count < 12:
            raise ValueError("Files can only be expanded by a minimum of 12 bytes")

        padding_size = count - 12
        padding_data = "a" * padding_size

        expansion_chunk = (
            "tEXt",
            padding_data,
            zlib.crc32("tEXt" + padding_data) & 0xFFFFFFFFL
        )

        # Add the chunk just before IEND
        self.chunks.insert(-1, expansion_chunk)

    def write(self, output_path):
        """Write the PNG file out to the output path."""

        with open(output_path, 'wb') as output_file:
            output_file.write(self.header)
            for chunk_name, content, crc_value in self.chunks:
                output_file.write(struct.pack("!I", len(content)))
                output_file.write(chunk_name)
                output_file.write(content)
                output_file.write(struct.pack("!I", crc_value))


def pad_to(input_path, output_path, size):
    """Pad the input file to the supplied size and write out to the output location."""

    png_file = PNGFile(input_path)

    if png_file.file_size > size:
        raise ValueError("File is already bigger than the supplied size")

    delta = size - png_file.file_size
    png_file.pad_by(delta)
    png_file.write(output_path)


def pad_by(input_path, output_path, size):
    """Pad the input file by the number of bytes specified and write to the output location."""

    png_file = PNGFile(input_path)
    png_file.pad_by(size)
    png_file.write(output_path)


def _handle_arguments():
    """Handle command line arguments and call the correct method."""

    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--to",
        dest="to",
        action="store",
        default=None,
        help="Pad the image to this size (in bytes)."
    )

    group.add_argument(
        "--by",
        dest="by",
        action="store",
        default=None,
        help="Pad the image by this size (in bytes)."
    )

    parser.add_argument(
        "-i",
        "--image",
        dest="input",
        action="store",
        default=None,
        help="The path to the original image",
        required=True
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        action="store",
        default=None,
        help="The path to write the new image to",
        required=True
    )

    args = parser.parse_args()

    if args.to is not None:
        size = args.to
    else:
        size = args.by

    try:
        size = int(size)
    except ValueError:
        print "Size value was not an integer"
        sys.exit(1)

    try:
        if args.to is not None:
            pad_to(args.input, args.output, size)
        else:
            pad_by(args.input, args.output, size)
    except Exception as ex:
        print ex.message
        sys.exit(1)


if __name__ == "__main__":
    _handle_arguments()
