# pngpadder

A tool for adding extra data to PNG files to pad them out for tests.

### Installation

    pip install pngpadder

### Examples:

    import pngpadder

    # Pad file size to 100,000 bytes
    pngpadder.pad_to('/path/to/file.png', '/path/to/output/file.png', 100000)

    # Pad file size by 20 bytes
    pngpadder.pad_by('/path/to/file.png', '/path/to/output/file.png', 20)

Alternatively, from the command line:

    # Pad file to 100,000 bytes
    pngpadder --to 100000 -i /path/to/file.png -o /path/to/output/file.png

    # Pad file size by 20 bytes
    pngpadder --to 100000 -i /path/to/file.png -o /path/to/output/file.png
