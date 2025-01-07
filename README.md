# Audio Library Exporter

Generates a sortable table of music from a folder with audio files.
![Audio Library Exporter](./audio_library_exporter.png?raw=true "Audio Library Exporter")

## Prerequisites
1. Install Python

2. Install Mutagen:
   - Run `pip install mutagen`

## Use
1. cd to the directory you want the output file to be in
2. Run `python path/to/generate_library_html_export.py`
3. Input the path to the folder with the audio files

- The script generates an HTML file that you can open in your web browser in the directory you ran the script in named `output.html`

## Features
- Scans the input folder (and subfolders) for audio files
- Supports file types that Mutagen supports
- Metadata (album artist, track name, album name, etc.) will be extracted
- Any missing metadata will default to "Unknown" values
- If a `cover.jpg`, `cover.png`, `folder.jpg`, or `folder.png` (case insensitive) exists in the same folder as an audio file, it will be displayed as the album cover
- Click on a column header to sort the table by that column
- Intended for people who download music locally (MusicBee, Foobar2000, etc.) to share their playlists