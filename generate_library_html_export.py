import os
import mutagen
import json
from html import escape

# Extracts metadata from an audio file using Mutagen
# @param {str} file_path - Path to the audio file
# @returns {dict|None} - Dictionary of metadata or None if failed
def extract_metadata(file_path):
    try:
        # Easy=True attempts to map generic keys (artist, title, etc.) across formats
        audio = mutagen.File(file_path, easy=True)
        if audio is None:
            return None

        # Helper to safely get the first item of a list tag
        def get_tag(key, default=""):
            val = audio.get(key, [default])
            return str(val[0]) if val else default

        # Helper to get numeric values safely
        def get_num(key, default=0):
            val = audio.get(key, [default])
            try:
                v = str(val[0])
                if "/" in v:
                    v = v.split("/")[0]
                return int(v)
            except:
                return default

        # Metadata extraction
        metadata = {
            "file_path": file_path,
            "cover": find_cover_image(file_path),
            "album_artist": get_tag("albumartist", get_tag("artist", "Unknown Album Artist")),
            "artist": get_tag("artist", "Unknown Artist"),
            "track_name": get_tag("title", os.path.splitext(os.path.basename(file_path))[0]),
            "album_name": get_tag("album", "Unknown Album"),
            "year": get_num("date", 0),
            "track_number": get_num("tracknumber", 0),
            "disc_number": get_num("discnumber", 1),
            "genre": get_tag("genre", ""),
            "composer": get_tag("composer", ""),
            "lyricist": get_tag("lyricist", ""),
            "language": get_tag("language", ""),
            "comment": get_tag("comment", ""),
            "copyright": get_tag("copyright", ""),
            "publisher": get_tag("organization", ""), 
            "bpm": get_num("bpm", 0),
            "isrc": get_tag("isrc", ""),
            "length": audio.info.length if hasattr(audio, 'info') else 0,
            "bitrate": int(audio.info.bitrate / 1000) if hasattr(audio, 'info') and hasattr(audio.info, 'bitrate') else 0,
            "sample_rate": audio.info.sample_rate if hasattr(audio, 'info') and hasattr(audio.info, 'sample_rate') else 0,
            "rating": get_num("rating", 0)
        }
        
        return metadata
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {
            "file_path": file_path,
            "cover": find_cover_image(file_path),
            "album_artist": "Error",
            "artist": "Error",
            "track_name": os.path.splitext(os.path.basename(file_path))[0],
            "album_name": "Error",
            "year": 0,
            "track_number": 0,
            "disc_number": 0,
            "genre": "",
            "composer": "",
            "lyricist": "",
            "language": "",
            "comment": "",
            "copyright": "",
            "publisher": "",
            "bpm": 0,
            "isrc": "",
            "rating": 0,
            "length": 0,
            "bitrate": 0,
            "sample_rate": 0
        }

# Formats seconds into MM:SS or HH:MM:SS
# @param {float} seconds 
# @returns {str}
def format_length(seconds):
    if not seconds: return "0:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = int(seconds % 60)
    if hours > 0:
        return f"{hours}:{minutes:02}:{sec:02}"
    else:
        return f"{minutes}:{sec:02}"

# Looks for cover art in the file's folder
# @param {str} file_path 
# @returns {str|None}
def find_cover_image(file_path):
    folder = os.path.dirname(file_path)

    for ext in [".jpg", ".png", ".jpeg"]:
        for name in ["cover", "folder", "front", "album"]:
            cover_path = os.path.join(folder, f"{name}{ext}")
            if os.path.isfile(cover_path):
                return os.path.abspath(cover_path)
    return None

# Scans folder recursively for audio files
# @param {str} folder_path 
# @returns {list}
def collect_metadata(folder_path):
    metadata_list = []
    audio_exts = {'.mp3', '.flac', '.m4a', '.ogg', '.wav', '.wma', '.aac', '.alac', '.aiff'}
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in audio_exts:
                file_path = os.path.join(root, file)
                metadata = extract_metadata(file_path)
                if metadata:
                    metadata_list.append(metadata)
    return metadata_list

# Generates the HTML content with embedded JSON data and JS logic
# @param {list} metadata_list 
# @returns {str}
def generate_html(metadata_list):
    for m in metadata_list:
        m['length_display'] = format_length(m['length'])

    # ensure_ascii=False writes actual unicode characters to the source code
    json_data = json.dumps(metadata_list, ensure_ascii=False)

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio Library</title>
    <style>
        :root {{
            --bg-color: #121212;
            --surface-color: #1e1e1e;
            --primary-color: #bb86fc;
            --text-color: #ffffff;
            --border-color: #444;
            --hover-color: #333;
            --input-bg: #2d2d2d;
            --success-color: #03dac6;
            --danger-color: #cf6679;
        }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: var(--bg-color); 
            color: var(--text-color); 
            overflow-x: hidden;
        }}
        
        .controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .controls-right {{ display: flex; gap: 10px; align-items: center; }}
        button {{
            background-color: var(--surface-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 14px;
        }}
        button:hover {{ background-color: var(--hover-color); }}
        button.primary {{ background-color: var(--primary-color); color: #000; border: none; font-weight: bold; }}
        button.danger {{ background-color: var(--danger-color); color: #000; border: none; }}
        button.small {{ padding: 4px 8px; font-size: 12px; }}
        
        /* Table */
        .table-container {{ overflow-x: auto; min-height: 400px; padding-bottom: 50px; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            min-width: 800px;
        }}
        th, td {{ 
            border: 1px solid var(--border-color); 
            padding: 8px; 
            text-align: left; 
            font-size: 14px;
        }}
        th {{ 
            background-color: #2c2c2c; 
            cursor: pointer; 
            user-select: none;
            white-space: nowrap;
        }}
        th:hover {{ background-color: var(--hover-color); }}
        
        .sort-icon {{ margin-left: 5px; opacity: 0.5; font-size: 12px; }}
        th.asc .sort-icon::after {{ content: '▲'; opacity: 1; color: var(--primary-color); }}
        th.desc .sort-icon::after {{ content: '▼'; opacity: 1; color: var(--primary-color); }}
        
        .filter-trigger {{
            margin-right: 8px;
            cursor: pointer;
            opacity: 0.4;
            font-size: 14px;
            display: inline-block;
        }}
        .filter-trigger:hover {{ opacity: 1; }}
        .filter-trigger.active {{ opacity: 1; color: var(--primary-color); font-weight: bold; }}

        tr:nth-child(even) {{ background-color: var(--surface-color); }}
        tr:hover {{ background-color: var(--hover-color); }}
        
        td img {{ 
            width: 50px; 
            height: 50px; 
            object-fit: cover; 
            border-radius: 4px;
        }}

        /* Common Modal/Popup Styles */
        .modal {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        .modal.active {{ display: flex; }}
        .modal-content {{
            background: var(--surface-color);
            padding: 20px;
            border-radius: 8px;
            width: 500px;
            max-width: 90%;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border-color);
        }}
        .modal-header {{ font-size: 18px; font-weight: bold; margin-bottom: 15px; display: flex; justify-content: space-between; }}
        .modal-body {{ overflow-y: auto; flex-grow: 1; margin-bottom: 15px; }}
        .modal-footer {{ text-align: right; display: flex; justify-content: flex-end; gap: 10px; }}

        /* Filter Popup */
        .filter-popup {{
            display: none;
            position: absolute;
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            padding: 15px;
            z-index: 100;
            border-radius: 6px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.7);
            min-width: 300px;
            max-width: 90vw;
            box-sizing: border-box;
        }}
        .filter-popup.show {{ display: block; }}
        .filter-list {{ 
            margin-bottom: 10px; max-height: 150px; overflow-y: auto; 
            border-bottom: 1px solid var(--border-color); padding-bottom: 5px;
        }}
        .filter-chip {{
            display: inline-flex; align-items: center;
            background: var(--bg-color); border: 1px solid var(--border-color);
            padding: 4px 8px; margin: 0 4px 4px 0; border-radius: 12px; font-size: 11px;
            max-width: 100%; box-sizing: border-box;
        }}
        .filter-chip span {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .filter-chip button {{
            background: none; border: none; color: var(--danger-color);
            font-weight: bold; margin-left: 5px; padding: 0; cursor: pointer; flex-shrink: 0;
        }}
        .filter-row {{ display: flex; gap: 5px; margin-bottom: 5px; flex-wrap: wrap; }}
        .filter-options {{ display: flex; gap: 10px; margin: 8px 0; font-size: 12px; color: #ccc; flex-wrap: wrap; }}
        
        input, select, textarea {{
            background: var(--input-bg); border: 1px solid var(--border-color);
            color: #fff; padding: 6px; border-radius: 3px; font-family: inherit;
        }}
        textarea {{ width: 100%; box-sizing: border-box; min-height: 100px; resize: vertical; }}

        /* Column List (Customize & Export) */
        .column-list {{
            border: 1px solid var(--border-color); padding: 5px; background: var(--bg-color);
            max-height: 300px; overflow-y: auto;
        }}
        .column-item {{
            display: flex; align-items: center; padding: 8px;
            border-bottom: 1px solid #333; background: var(--surface-color);
            user-select: none; margin-bottom: 2px;
        }}
        .column-item:hover {{ background-color: var(--hover-color); }}
        .column-item label {{ flex-grow: 1; margin-left: 10px; cursor: pointer; }}
        
        .export-options, .import-options {{ margin-bottom: 15px; display: flex; flex-direction: column; gap: 10px; }}
        .row {{ display: flex; gap: 10px; align-items: center; }}
        
    </style>
</head>
<body>
    <div class="controls">
        <h1>Audio Library</h1>
        <div class="controls-right">
            <span id="count-display">0 items</span>
            <button id="btn-customize">Customize View</button>
            <button id="btn-import">Import</button>
            <button id="btn-export">Export</button>
        </div>
    </div>

    <div class="table-container">
        <table id="audio-table">
            <thead><!-- JS --></thead>
            <tbody><!-- JS --></tbody>
        </table>
    </div>

    <!-- Filter Popup -->
    <div id="filter-popup" class="filter-popup">
        <div style="font-weight: bold; margin-bottom: 5px; font-size: 14px; display:flex; justify-content:space-between;">
            <span>Filters</span>
            <button id="btn-clear-column" class="small danger" style="padding: 2px 6px;">Clear</button>
        </div>
        <div id="filter-list" class="filter-list"></div>
        <div class="new-filter-section">
            <div class="filter-row">
                <select id="filter-op" style="width: 40%; min-width: 100px;"></select>
                <input type="text" id="filter-val1" placeholder="Value..." style="width: 50%; min-width: 100px;">
            </div>
            <div id="row-val2" class="filter-row" style="display:none;">
                <input type="text" id="filter-val2" placeholder="To Value..." style="width: 100%">
            </div>
            <div id="text-options" class="filter-options" style="display:none;">
                <label><input type="checkbox" id="chk-case"> Match Case</label>
                <label><input type="checkbox" id="chk-word"> Whole Word</label>
                <label><input type="checkbox" id="chk-regex"> Regex</label>
            </div>
            <button id="btn-add-filter" class="primary small" style="width:100%; margin-top:5px;">+ Add Filter</button>
        </div>
        <div style="margin-top: 10px; display: flex; justify-content: flex-end; gap: 5px;">
            <button id="btn-close-filter" class="small">Close</button>
            <button id="btn-apply-filters" class="small primary">Apply Changes</button>
        </div>
    </div>

    <!-- Customize Modal -->
    <div id="modal-customize" class="modal">
        <div class="modal-content">
            <div class="modal-header">Customize Columns</div>
            <div class="modal-body">
                <p style="font-size: 12px; margin-top:0; color: #aaa;">Drag items to reorder.</p>
                <div class="column-list" id="column-list-container"></div>
            </div>
            <div class="modal-footer">
                <button id="btn-close-modal">Cancel</button>
                <button id="btn-save-modal" class="primary">Apply</button>
            </div>
        </div>
    </div>

    <!-- Export Modal -->
    <div id="modal-export" class="modal">
        <div class="modal-content">
            <div class="modal-header">Export Data</div>
            <div class="modal-body">
                <div class="export-options">
                    <div class="row">
                        <label>Format:</label>
                        <select id="export-format">
                            <option value="csv">CSV (.csv)</option>
                            <option value="txt">Text (.txt)</option>
                            <option value="clipboard">Clipboard (View)</option>
                        </select>
                    </div>
                    <div class="row">
                        <label>Delimiter:</label>
                        <select id="export-delimiter">
                            <option value=",">Comma (,)</option>
                            <option value="\\t">Tab (\\t)</option>
                            <option value=";">Semicolon (;)</option>
                            <option value="|">Pipe (|)</option>
                        </select>
                    </div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                    <label>Columns to Export:</label>
                    <div>
                        <button id="btn-export-select-all" class="small">Select All</button>
                        <button id="btn-export-deselect-all" class="small">Deselect All</button>
                    </div>
                </div>
                <div class="column-list" id="export-column-list">
                    <!-- Checkboxes -->
                </div>
                <!-- Clipboard Area -->
                <div id="export-clipboard-area" style="display:none; margin-top: 10px;">
                    <label>Preview / Copy:</label>
                    <textarea id="export-textarea" readonly></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button id="btn-close-export">Close</button>
                <button id="btn-perform-export" class="primary">Export</button>
            </div>
        </div>
    </div>

    <!-- Import Modal -->
    <div id="modal-import" class="modal">
        <div class="modal-content">
            <div class="modal-header">Import Data</div>
            <div class="modal-body">
                <div class="import-options">
                    <div class="row">
                        <label>Delimiter:</label>
                        <select id="import-delimiter">
                            <option value=",">Comma (,)</option>
                            <option value="\\t">Tab (\\t)</option>
                            <option value=";">Semicolon (;)</option>
                            <option value="|">Pipe (|)</option>
                        </select>
                    </div>
                    <div>
                        <label>Select File:</label>
                        <input type="file" id="import-file" accept=".csv,.txt">
                    </div>
                    <div style="text-align: center; margin: 5px;">- OR -</div>
                    <div>
                        <label>Paste Data:</label>
                        <textarea id="import-textarea" placeholder="Paste CSV/Text data here..."></textarea>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button id="btn-close-import">Close</button>
                <button id="btn-perform-import" class="primary">Load Data</button>
            </div>
        </div>
    </div>

    <script>
        // Use let so we can overwrite on Import
        let audioData = {json_data};

        // Config
        let columns = [
            {{ key: 'cover', label: 'Cover Art', visible: true, type: 'image' }},
            {{ key: 'track_name', label: 'Title', visible: true, type: 'text' }},
            {{ key: 'artist', label: 'Artist', visible: true, type: 'text' }},
            {{ key: 'album_artist', label: 'Album Artist', visible: true, type: 'text' }},
            {{ key: 'album_name', label: 'Album', visible: true, type: 'text' }},
            {{ key: 'year', label: 'Year', visible: true, type: 'number' }},
            {{ key: 'disc_number', label: 'Disc #', visible: true, type: 'number' }},
            {{ key: 'track_number', label: 'Track #', visible: true, type: 'number' }},
            {{ key: 'genre', label: 'Genre', visible: true, type: 'text' }},
            {{ key: 'composer', label: 'Composer', visible: true, type: 'text' }},
            {{ key: 'lyricist', label: 'Lyricist', visible: true, type: 'text' }},
            {{ key: 'publisher', label: 'Publisher', visible: true, type: 'text' }},
            {{ key: 'language', label: 'Language', visible: true, type: 'text' }},
            {{ key: 'comment', label: 'Comment', visible: true, type: 'text' }},
            {{ key: 'rating', label: 'Rating', visible: true, type: 'number' }},
            {{ key: 'length', label: 'Length', visible: false, type: 'duration' }},
            {{ key: 'bpm', label: 'BPM', visible: false, type: 'number' }},
            {{ key: 'bitrate', label: 'Bitrate (kbps)', visible: false, type: 'number' }},
            {{ key: 'sample_rate', label: 'Sample Rate (Hz)', visible: false, type: 'number' }},
            {{ key: 'copyright', label: 'Copyright', visible: false, type: 'text' }},
            {{ key: 'isrc', label: 'ISRC', visible: false, type: 'text' }},
        ];

        let currentSort = {{ key: null, asc: true }};
        let activeFilters = {{}}; 
        let visibleData = [];
        let pendingFilters = []; 
        let activeFilterColumn = null;

        // DOM Elements
        const table = document.getElementById('audio-table');
        const countDisplay = document.getElementById('count-display');
        const filterPopup = document.getElementById('filter-popup');

        document.addEventListener('DOMContentLoaded', () => {{
            processData();
            setupCustomizeModal();
            setupFilterUI();
            setupExportModal();
            setupImportModal();
            
            // Global click to close popups
            document.addEventListener('click', (e) => {{
                if (filterPopup.classList.contains('show')) {{
                    if (!filterPopup.contains(e.target) && !e.target.classList.contains('filter-trigger')) {{
                        filterPopup.classList.remove('show');
                    }}
                }}
            }});
        }});

        // --- Data Logic ---
        function processData() {{
            visibleData = audioData.filter(item => {{
                for (let key in activeFilters) {{
                    const rules = activeFilters[key];
                    if (!rules || rules.length === 0) continue;
                    let rawVal = item[key];
                    const isNum = (
                        key === 'year' || key === 'track_number' || key === 'disc_number' || 
                        key === 'bpm' || key === 'bitrate' || key === 'sample_rate' || 
                        key === 'rating' || key === 'length'
                    );
                    const numVal = isNum ? Number(rawVal) : 0;
                    const strVal = String(rawVal || ""); 

                    for (let rule of rules) {{
                        if (!checkRule(rule, numVal, strVal, isNum)) return false;
                    }}
                }}
                return true;
            }});
            sortData();
            renderTable();
            countDisplay.textContent = `${{visibleData.length}} items`;
        }}

        function checkRule(rule, numVal, strVal, isNum) {{
            if (isNum) {{
                const f1 = parseFloat(rule.value);
                const f2 = parseFloat(rule.value2);
                if (isNaN(f1)) return true; 
                switch (rule.operator) {{
                    case 'gt': return numVal > f1;
                    case 'lt': return numVal < f1;
                    case 'eq': return numVal === f1;
                    case 'between': return numVal >= f1 && numVal <= f2;
                    default: return true;
                }}
            }} 
            let target = strVal;
            let search = rule.value;
            if (rule.useRegex) {{
                try {{
                    let pattern = search;
                    if (rule.wholeWord) pattern = '\\\\b' + pattern + '\\\\b';
                    if (rule.operator === 'eq') pattern = '^' + pattern + '$';
                    if (rule.operator === 'starts') pattern = '^' + pattern;
                    if (rule.operator === 'ends') pattern = pattern + '$';
                    const flags = rule.matchCase ? '' : 'i';
                    const re = new RegExp(pattern, flags);
                    const match = re.test(target);
                    return rule.operator === 'not_contains' ? !match : match;
                }} catch (e) {{ return false; }}
            }} else {{
                if (!rule.matchCase) {{ target = target.toLowerCase(); search = search.toLowerCase(); }}
                if (rule.wholeWord) {{
                    const esc = search.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
                    const flags = rule.matchCase ? '' : 'i';
                    const re = new RegExp('\\\\b' + esc + '\\\\b', flags);
                    const match = re.test(target);
                    return rule.operator === 'not_contains' ? !match : match;
                }}
                switch (rule.operator) {{
                    case 'contains': return target.includes(search);
                    case 'not_contains': return !target.includes(search);
                    case 'starts': return target.startsWith(search);
                    case 'ends': return target.endsWith(search);
                    case 'eq': return target === search;
                    default: return true;
                }}
            }}
        }}

        function sortData() {{
            if (!currentSort.key) return;
            visibleData.sort((a, b) => {{
                let valA = a[currentSort.key];
                let valB = b[currentSort.key];
                if (valA === null || valA === undefined) valA = '';
                if (valB === null || valB === undefined) valB = '';
                if (typeof valA === 'number' && typeof valB === 'number') {{
                    return currentSort.asc ? valA - valB : valB - valA;
                }}
                valA = valA.toString().toLowerCase();
                valB = valB.toString().toLowerCase();
                if (valA < valB) return currentSort.asc ? -1 : 1;
                if (valA > valB) return currentSort.asc ? 1 : -1;
                return 0;
            }});
        }}

        // --- Rendering ---
        function renderTable() {{
            const thead = table.querySelector('thead');
            const tbody = table.querySelector('tbody');
            thead.innerHTML = '';
            tbody.innerHTML = '';

            const trHead = document.createElement('tr');
            columns.forEach(col => {{
                if (!col.visible) return;
                const th = document.createElement('th');
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.alignItems = 'center';

                if (col.key !== 'cover') {{
                    const hasFilter = activeFilters[col.key] && activeFilters[col.key].length > 0;
                    const filterSpan = document.createElement('span');
                    filterSpan.className = 'filter-trigger ' + (hasFilter ? 'active' : '');
                    filterSpan.innerHTML = '&#x1F702;'; 
                    filterSpan.onclick = (e) => {{ e.stopPropagation(); openFilterPopup(col, filterSpan); }};
                    div.appendChild(filterSpan);
                }}

                const labelSpan = document.createElement('span');
                labelSpan.textContent = col.label;
                div.appendChild(labelSpan);
                const sortSpan = document.createElement('span');
                sortSpan.className = 'sort-icon';
                div.appendChild(sortSpan);
                th.appendChild(div);
                th.onclick = () => handleSort(col.key);
                if (currentSort.key === col.key) th.classList.add(currentSort.asc ? 'asc' : 'desc');
                trHead.appendChild(th);
            }});
            thead.appendChild(trHead);

            const fragment = document.createDocumentFragment();
            visibleData.forEach(item => {{
                const tr = document.createElement('tr');
                columns.forEach(col => {{
                    if (!col.visible) return;
                    const td = document.createElement('td');
                    if (col.type === 'image') {{
                        if (item[col.key]) {{
                            const img = document.createElement('img');
                            img.src = item[col.key]; img.loading = 'lazy'; td.appendChild(img);
                        }}
                    }} else if (col.type === 'duration') {{
                        td.textContent = item['length_display'] || '0:00';
                    }} else {{
                        td.textContent = item[col.key] !== null ? item[col.key] : '';
                    }}
                    tr.appendChild(td);
                }});
                fragment.appendChild(tr);
            }});
            tbody.appendChild(fragment);
        }}

        function handleSort(key) {{
            if (currentSort.key === key) currentSort.asc = !currentSort.asc;
            else {{ currentSort.key = key; currentSort.asc = true; }}
            processData();
        }}

        // --- Filter Logic ---
        function setupFilterUI() {{
            const valInput = document.getElementById('filter-val1');
            const valInput2 = document.getElementById('filter-val2');

            const addRule = () => {{
                const op = document.getElementById('filter-op').value;
                const v1 = valInput.value;
                const v2 = valInput2.value;
                if (v1.trim() === '') return;
                const rule = {{ 
                    operator: op, value: v1, value2: v2,
                    matchCase: document.getElementById('chk-case').checked,
                    wholeWord: document.getElementById('chk-word').checked,
                    useRegex: document.getElementById('chk-regex').checked
                }};
                pendingFilters.push(rule);
                valInput.value = ''; valInput2.value = ''; valInput.focus();
                renderPendingFilters();
            }};

            document.getElementById('btn-add-filter').onclick = addRule;
            valInput.addEventListener('keypress', (e) => {{ if (e.key === 'Enter') addRule(); }});
            valInput2.addEventListener('keypress', (e) => {{ if (e.key === 'Enter') addRule(); }});

            document.getElementById('btn-apply-filters').onclick = () => {{
                if (activeFilterColumn) {{
                    if (pendingFilters.length > 0) activeFilters[activeFilterColumn.key] = [...pendingFilters];
                    else delete activeFilters[activeFilterColumn.key];
                }}
                filterPopup.classList.remove('show');
                processData();
            }};
            document.getElementById('btn-clear-column').onclick = () => {{ pendingFilters = []; renderPendingFilters(); }};
            document.getElementById('btn-close-filter').onclick = () => {{ filterPopup.classList.remove('show'); }};
            document.getElementById('filter-op').onchange = (e) => {{
                document.getElementById('row-val2').style.display = e.target.value === 'between' ? 'flex' : 'none';
            }};
        }}

        function openFilterPopup(col, triggerEl) {{
            activeFilterColumn = col;
            pendingFilters = activeFilters[col.key] ? [...activeFilters[col.key]] : [];
            const selOp = document.getElementById('filter-op');
            selOp.innerHTML = '';
            
            const isNum = (col.type === 'number' || col.type === 'duration');
            const ops = isNum 
                ? [{{v:'eq',t:'Equals'}}, {{v:'gt',t:'Greater Than'}}, {{v:'lt',t:'Less Than'}}, {{v:'between',t:'Between'}}]
                : [{{v:'contains',t:'Contains'}}, {{v:'not_contains',t:'Does not contain'}}, {{v:'starts',t:'Starts with'}}, {{v:'ends',t:'Ends with'}}, {{v:'eq',t:'Equals'}}];
            ops.forEach(o => {{
                const opt = document.createElement('option'); opt.value = o.v; opt.textContent = o.t; selOp.appendChild(opt);
            }});
            selOp.value = ops[0].v;
            document.getElementById('filter-val1').value = '';
            document.getElementById('filter-val2').value = '';
            document.getElementById('row-val2').style.display = 'none';
            document.getElementById('text-options').style.display = isNum ? 'none' : 'flex';
            document.getElementById('chk-case').checked = false;
            document.getElementById('chk-word').checked = false;
            document.getElementById('chk-regex').checked = false;

            const input1 = document.getElementById('filter-val1');
            input1.type = isNum ? 'number' : 'text';
            document.getElementById('filter-val2').type = 'number';
            renderPendingFilters();

            const rect = triggerEl.getBoundingClientRect();
            const scrollX = window.scrollX || window.pageXOffset;
            const scrollY = window.scrollY || window.pageYOffset;
            const viewportWidth = document.documentElement.clientWidth;
            const popupWidth = 320; 
            let left = rect.left + scrollX;
            if (left + popupWidth > viewportWidth) left = viewportWidth - popupWidth - 10;
            if (left < 10) left = 10;

            filterPopup.style.top = (rect.bottom + scrollY + 5) + 'px';
            filterPopup.style.left = left + 'px';
            filterPopup.classList.add('show');
            setTimeout(() => input1.focus(), 100);
        }}

        function renderPendingFilters() {{
            const container = document.getElementById('filter-list');
            container.innerHTML = '';
            if (pendingFilters.length === 0) {{
                container.innerHTML = '<div style="padding:10px; color:#777; font-size:12px; text-align:center">No active filters</div>';
                return;
            }}
            pendingFilters.forEach((f, idx) => {{
                const chip = document.createElement('div');
                chip.className = 'filter-chip';
                let text = `${{f.operator}} "${{f.value}}"`;
                if (f.operator === 'between') text += ` - "${{f.value2}}"`;
                if (f.matchCase) text += ' [Aa]';
                if (f.wholeWord) text += ' [""]';
                if (f.useRegex) text += ' [.*]';
                const span = document.createElement('span'); span.textContent = text;
                const btn = document.createElement('button'); btn.textContent = '✕';
                btn.onclick = (e) => {{ e.stopPropagation(); pendingFilters.splice(idx, 1); renderPendingFilters(); }};
                chip.appendChild(span); chip.appendChild(btn); container.appendChild(chip);
            }});
        }}

        // --- Export & Import ---
        function setupExportModal() {{
            const modal = document.getElementById('modal-export');
            const list = document.getElementById('export-column-list');
            const formatSel = document.getElementById('export-format');
            const txtAreaDiv = document.getElementById('export-clipboard-area');

            document.getElementById('btn-export').onclick = () => {{
                // Populate columns
                list.innerHTML = '';
                columns.forEach(col => {{
                    const div = document.createElement('div');
                    div.className = 'column-item';
                    const cb = document.createElement('input');
                    cb.type = 'checkbox';
                    cb.checked = col.visible; 
                    cb.value = col.key;
                    const lbl = document.createElement('label');
                    lbl.textContent = col.label;
                    lbl.onclick = () => cb.click();
                    div.appendChild(cb); div.appendChild(lbl); list.appendChild(div);
                }});
                txtAreaDiv.style.display = 'none';
                modal.classList.add('active');
            }};

            document.getElementById('btn-close-export').onclick = () => modal.classList.remove('active');

            document.getElementById('btn-export-select-all').onclick = () => {{
                list.querySelectorAll('input[type="checkbox"]').forEach(c => c.checked = true);
            }};

            document.getElementById('btn-export-deselect-all').onclick = () => {{
                list.querySelectorAll('input[type="checkbox"]').forEach(c => c.checked = false);
            }};

            document.getElementById('btn-perform-export').onclick = () => {{
                const format = formatSel.value;
                let delimiter = document.getElementById('export-delimiter').value;
                if (delimiter === '\\t') delimiter = '\\t';

                const selectedKeys = Array.from(list.querySelectorAll('input:checked')).map(cb => cb.value);
                if (selectedKeys.length === 0) {{ alert("Select at least one column."); return; }}

                // Header
                const header = selectedKeys.map(k => {{
                    const c = columns.find(col => col.key === k);
                    return escapeCSV(c.label, delimiter);
                }}).join(delimiter);

                // Rows
                const rows = visibleData.map(item => {{
                    return selectedKeys.map(k => {{
                        let val = item[k];
                        if (k === 'length') val = item['length_display'];
                        return escapeCSV(String(val || ''), delimiter);
                    }}).join(delimiter);
                }}).join('\\n');

                const content = header + '\\n' + rows;

                if (format === 'clipboard') {{
                    const ta = document.getElementById('export-textarea');
                    ta.value = content;
                    txtAreaDiv.style.display = 'block';
                    ta.select();
                    document.execCommand('copy'); 
                }} else {{
                    // Add Byte Order Mark (BOM) for Excel to read UTF-8 correctly
                    const bom = new Uint8Array([0xEF, 0xBB, 0xBF]); 
                    const blob = new Blob([bom, content], {{ type: 'text/csv;charset=utf-8' }});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `audio_library_export.${{format}}`;
                    a.click();
                    URL.revokeObjectURL(url);
                    modal.classList.remove('active');
                }}
            }};
        }}

        function escapeCSV(str, delimiter) {{
            if (str.includes(delimiter) || str.includes('"') || str.includes('\\n')) {{
                return '"' + str.replace(/"/g, '""') + '"';
            }}
            return str;
        }}

        function setupImportModal() {{
            const modal = document.getElementById('modal-import');
            document.getElementById('btn-import').onclick = () => modal.classList.add('active');
            document.getElementById('btn-close-import').onclick = () => modal.classList.remove('active');

            document.getElementById('btn-perform-import').onclick = () => {{
                const fileInput = document.getElementById('import-file');
                const ta = document.getElementById('import-textarea');
                let delimiter = document.getElementById('import-delimiter').value;
                if (delimiter === '\\t') delimiter = '\\t';

                if (fileInput.files.length > 0) {{
                    const reader = new FileReader();
                    reader.onload = (e) => parseImport(e.target.result, delimiter, modal);
                    reader.readAsText(fileInput.files[0]);
                }} else if (ta.value.trim() !== '') {{
                    parseImport(ta.value, delimiter, modal);
                }} else {{
                    alert("Please select a file or paste data.");
                }}
            }};
        }}

        function parseImport(text, delimiter, modal) {{
            const lines = text.trim().split('\\n');
            if (lines.length < 2) {{ alert("Invalid data format."); return; }}

            // Parse Header
            const headers = splitCSV(lines[0], delimiter).map(h => h.trim());
            const keyMap = {{}};
            headers.forEach((h, idx) => {{
                const col = columns.find(c => c.label.toLowerCase() === h.toLowerCase() || c.key.toLowerCase() === h.toLowerCase());
                if (col) keyMap[idx] = col.key;
            }});

            const newData = [];
            for (let i = 1; i < lines.length; i++) {{
                if (!lines[i].trim()) continue;
                const vals = splitCSV(lines[i], delimiter);
                const obj = {{}};
                columns.forEach(c => obj[c.key] = (c.type === 'number' ? 0 : ''));
                
                vals.forEach((v, idx) => {{
                    if (keyMap[idx]) {{
                        let val = v.trim();
                        const col = columns.find(c => c.key === keyMap[idx]);
                        if (col.type === 'number') val = Number(val) || 0;
                        if (col.key === 'length') {{
                            if (val.includes(':')) {{
                                const parts = val.split(':').map(Number);
                                if (parts.length === 2) val = parts[0]*60 + parts[1];
                                if (parts.length === 3) val = parts[0]*3600 + parts[1]*60 + parts[2];
                            }} else {{
                                val = Number(val);
                            }}
                        }}
                        obj[keyMap[idx]] = val;
                    }}
                }});
                obj['length_display'] = formatLengthJS(obj['length']);
                newData.push(obj);
            }}
            
            audioData = newData;
            processData();
            modal.classList.remove('active');
            alert(`Imported ${{newData.length}} items.`);
        }}

        function splitCSV(str, delimiter) {{
            const result = [];
            let current = '';
            let inQuote = false;
            for (let i = 0; i < str.length; i++) {{
                const char = str[i];
                if (char === '"' && str[i+1] === '"') {{
                    current += '"'; i++;
                }} else if (char === '"') {{
                    inQuote = !inQuote;
                }} else if (char === delimiter && !inQuote) {{
                    result.push(current);
                    current = '';
                }} else {{
                    current += char;
                }}
            }}
            result.push(current);
            return result;
        }}

        function formatLengthJS(seconds) {{
            if (!seconds) return "0:00";
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = Math.floor(seconds % 60);
            const sStr = s.toString().padStart(2, '0');
            if (h > 0) return `${{h}}:${{m.toString().padStart(2, '0')}}:${{sStr}}`;
            return `${{m}}:${{sStr}}`;
        }}

        // --- Customize Modal Logic (retained) ---
        function setupCustomizeModal() {{
            const modal = document.getElementById('modal-customize');
            const list = document.getElementById('column-list-container');
            document.getElementById('btn-customize').onclick = () => {{
                renderDragList(list);
                modal.classList.add('active');
            }};
            document.getElementById('btn-close-modal').onclick = () => modal.classList.remove('active');
            document.getElementById('btn-save-modal').onclick = () => {{
                const items = Array.from(list.children);
                const newColumns = [];
                items.forEach(item => {{
                    const key = item.dataset.key;
                    const checkbox = item.querySelector('input[type="checkbox"]');
                    const colConfig = columns.find(c => c.key === key);
                    if (colConfig) {{
                        colConfig.visible = checkbox.checked;
                        newColumns.push(colConfig);
                    }}
                }});
                columns = newColumns;
                renderTable();
                modal.classList.remove('active');
            }};
        }}

        let dragSrcEl = null;
        function renderDragList(container) {{
            container.innerHTML = '';
            columns.forEach((col) => {{
                const div = document.createElement('div');
                div.className = 'column-item'; div.draggable = true; div.dataset.key = col.key;
                div.addEventListener('dragstart', handleDragStart);
                div.addEventListener('dragover', handleDragOver);
                div.addEventListener('dragenter', handleDragEnter);
                div.addEventListener('dragleave', handleDragLeave);
                div.addEventListener('drop', handleDrop);
                div.addEventListener('dragend', handleDragEnd);
                const grip = document.createElement('span'); grip.innerHTML = '&#9776;'; grip.style.marginRight = '10px'; grip.style.color = '#666'; grip.style.cursor = 'grab';
                const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.checked = col.visible; checkbox.onmousedown = (e) => e.stopPropagation(); 
                const label = document.createElement('label'); label.textContent = col.label; label.onclick = () => checkbox.click();
                div.appendChild(grip); div.appendChild(checkbox); div.appendChild(label); container.appendChild(div);
            }});
        }}
        function handleDragStart(e) {{ dragSrcEl = this; e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/html', this.innerHTML); this.classList.add('dragging'); }}
        function handleDragOver(e) {{ if (e.preventDefault) e.preventDefault(); e.dataTransfer.dropEffect = 'move'; return false; }}
        function handleDragEnter(e) {{ this.classList.add('over'); }}
        function handleDragLeave(e) {{ this.classList.remove('over'); }}
        function handleDrop(e) {{
            if (e.stopPropagation) e.stopPropagation();
            if (dragSrcEl !== this) {{
                const container = this.parentNode;
                const items = [...container.children];
                const fromIndex = items.indexOf(dragSrcEl);
                const toIndex = items.indexOf(this);
                if (fromIndex < toIndex) container.insertBefore(dragSrcEl, this.nextSibling);
                else container.insertBefore(dragSrcEl, this);
            }}
            return false;
        }}
        function handleDragEnd(e) {{ this.classList.remove('dragging'); this.parentNode.querySelectorAll('.column-item').forEach(i => i.classList.remove('over')); }}
    </script>
</body>
</html>"""

    return html_template.format(json_data=json_data)

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