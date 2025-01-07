import os
import mutagen
from html import escape

def extract_metadata(file_path):
    try:
        audio = mutagen.File(file_path, easy=True)
        if audio is None:
            return None

        metadata = {
            "album_artist": audio.get("albumartist", [audio.get("artist", ["Unknown Album Artist"])[0]])[0],
            "artist": audio.get("artist", ["Unknown Artist"])[0],
            "track_name": audio.get("title", [os.path.splitext(os.path.basename(file_path))[0]])[0],
            "album_name": audio.get("album", ["Unknown Album"])[0],
            "year": audio.get("date", ["Unknown Year"])[0],
            "length": audio.info.length if hasattr(audio, 'info') else 0,
            "cover": find_cover_image(file_path)
        }
        return metadata
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {
            "album_artist": "Unknown Album Artist",
            "artist": "Unknown Artist",
            "track_name": os.path.splitext(os.path.basename(file_path))[0],
            "album_name": "Unknown Album",
            "year": "Unknown Year",
            "length": 0,
            "cover": find_cover_image(file_path)
        }

def format_length(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"

def find_cover_image(file_path):
    folder = os.path.dirname(file_path)

    for ext in [".jpg", ".png"]:
        for name in ["cover", "folder"]:
            cover_path = os.path.join(folder, f"{name}{ext}")

            if os.path.isfile(cover_path):
                return cover_path

    return None

def collect_metadata(folder_path):
    metadata_list = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            metadata = extract_metadata(file_path)
            if metadata:
                metadata_list.append(metadata)
    return metadata_list

def generate_html(metadata_list):
    html_template = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Audio Library</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #121212; 
            color: #ffffff; 
        }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
        }}
        th, td {{ 
            border: 1px solid #444; 
            padding: 8px; 
            text-align: left; 
        }}
        th {{ 
            background-color: #333; 
            cursor: pointer; 
        }}
        tr:nth-child(even) {{ 
            background-color: #1e1e1e; 
        }}
        tr:hover {{ 
            background-color: #333; 
        }}
        img {{ 
            max-width: 50px; 
            max-height: 50px; 
        }}
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const table = document.querySelector('table');
            const headers = table.querySelectorAll('th');
            headers.forEach((header, index) => {{
                header.addEventListener('click', () => {{
                    const rows = Array.from(table.querySelectorAll('tbody tr'));
                    const ascending = header.dataset.order !== 'asc';
                    rows.sort((rowA, rowB) => {{
                        const cellA = rowA.children[index].textContent.trim();
                        const cellB = rowB.children[index].textContent.trim();
                        if (!isNaN(cellA) && !isNaN(cellB)) {{
                            return ascending ? cellA - cellB : cellB - cellA;
                        }}
                        return ascending 
                            ? cellA.localeCompare(cellB)
                            : cellB.localeCompare(cellA);
                    }});
                    header.dataset.order = ascending ? 'asc' : 'desc';
                    const tbody = table.querySelector('tbody');
                    tbody.innerHTML = '';
                    rows.forEach(row => tbody.appendChild(row));
                }});
            }});
        }});
    </script>
</head>
<body>
    <h1>Audio Library</h1>
    <table>
        <thead>
            <tr>
                <th>Cover</th>
                <th>Album Artist</th>
                <th>Artist</th>
                <th>Track Name</th>
                <th>Album Name</th>
                <th>Year</th>
                <th>Length</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>"""

    rows = ""
    for metadata in metadata_list:
        cover_html = f"<img src='{escape(metadata['cover'])}' alt='Cover'>" if metadata['cover'] else ""
        rows += "<tr>"
        rows += f"<td>{cover_html}</td>"
        rows += f"<td>{escape(metadata['album_artist'])}</td>"
        rows += f"<td>{escape(metadata['artist'])}</td>"
        rows += f"<td>{escape(metadata['track_name'])}</td>"
        rows += f"<td>{escape(metadata['album_name'])}</td>"
        rows += f"<td>{escape(metadata['year'])}</td>"
        rows += f"<td>{format_length(metadata['length'])}</td>"
        rows += "</tr>"

    return html_template.format(rows=rows)

def main():
    folder_path = input("Enter the path to the folder to scan: ").strip()

    if folder_path.startswith('"') and folder_path.endswith('"'):
        folder_path = folder_path[1:-1]

    folder_path = os.path.normpath(folder_path)

    if not os.path.isdir(folder_path):
        print("Invalid folder path.")
        return

    print(f"Scanning folder: {folder_path}")

    print("Scanning for audio files...")
    metadata_list = collect_metadata(folder_path)
    print(f"Found {len(metadata_list)} audio files.")

    html_output = generate_html(metadata_list)

    output_file = "output.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"Metadata table written to {output_file}")

if __name__ == "__main__":
    main()
