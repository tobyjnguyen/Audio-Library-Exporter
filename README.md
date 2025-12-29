# Audio Library Exporter

Generates a sortable table of music from a folder with audio files. Intended for people who have music locally (MusicBee, Foobar2000, etc.) to view/share their music library.

![Audio Library Exporter](./audio_library_exporter.png?raw=true "Audio Library Exporter")

## Prerequisites
1. Install Python
2. Install Mutagen:
   - Run `pip install mutagen`

## Use
1. cd to the directory you want the output file to be in
2. Run `python path/to/generate_library_html_export.py`
3. Input the path to the folder with the audio files
- The script generates a standalone HTML file that you can open in your web browser in the directory you ran the script in named `output.html`

## Features
- Scans the input folder (and subfolders) for audio files
- Supports file types that Mutagen supports (mp3, opus, flac, etc.)
- Metadata (album artist, track name, album name, etc.) will be extracted
- Customize view (reorder, show, hide columns, etc.)
- Filter columns (contains, greater than, less than, etc.)
- Import/export as .csv, .txt, or clipboard with customizable delimiter
- Click on a column header to sort the table by that column
- If a `cover.jpg`, `cover.png`, `folder.jpg`, or `folder.png` (case insensitive) exists in the same folder as an audio file or the audio file has an embedded image, it will be displayed as the album cover