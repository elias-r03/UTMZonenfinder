from flask import Flask, request, jsonify
import folium
from folium import Element

app = Flask(__name__)

current_selection = None


def get_utm_zone_letter(lat):
    if lat >= -80 and lat < 72:
        letters = 'CDEFGHJKLMNPQRSTUVWX'
        index = int((lat + 80) / 8)
        return letters[index]
    elif lat >= 72 and lat <= 84:
        return 'X'
    else:
        return '?'


def get_latitude_band_bounds(zone_letter):
    letters = 'CDEFGHJKLMNPQRSTUVWX'
    if zone_letter == 'X':
        return (72, 84)
    elif zone_letter in letters:
        index = letters.index(zone_letter)
        lat_min = -80 + (index * 8)
        lat_max = lat_min + 8
        return (lat_min, lat_max)
    else:
        return (0, 0)


def utm_zone_bounds(zone_number, lat):
    lon_min = (zone_number - 1) * 6 - 180
    lon_max = zone_number * 6 - 180

    zone_letter = get_utm_zone_letter(lat)
    lat_min, lat_max = get_latitude_band_bounds(zone_letter)

    return [(lat_min, lon_min), (lat_max, lon_max)]


def create_map(selected_zone=None, selected_lat=None, selected_lon=None):
    if selected_zone and selected_lat is not None and selected_lon is not None:
        m = folium.Map(location=[selected_lat, selected_lon], zoom_start=5)

        bounds = utm_zone_bounds(selected_zone, selected_lat)
        folium.Rectangle(
            bounds,
            color='#FF0000',
            weight=3,
            fill=True,
            fill_color='#FF0000',
            fill_opacity=0.15,
            popup=f'UTM Zone {selected_zone}{get_utm_zone_letter(selected_lat)}'
        ).add_to(m)

        zone_letter = get_utm_zone_letter(selected_lat)
        hemi_text = 'Nördliche Hemisphäre' if selected_lat >= 0 else 'Südliche Hemisphäre'

        popup_content = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <b>Koordinaten:</b><br>
            Breite: {selected_lat:.6f}°<br>
            Länge: {selected_lon:.6f}°<br><br>
            <b>UTM-Zone:</b> {selected_zone}{zone_letter}<br>
            <b>Hemisphäre:</b> {hemi_text}<br><br>
            <small>Verzerrung: &lt; 0,1%</small>
        </div>
        """

        folium.Marker(
            location=[selected_lat, selected_lon],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip='Klicke für Details',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

    else:
        m = folium.Map(location=[20, 0], zoom_start=2)

    map_var = m.get_name()

    click_js = f"""
    <script>
    (function() {{
        function attachClickHandler() {{
            var map = window["{map_var}"];
            if (!map || typeof map.on !== 'function') {{
                setTimeout(attachClickHandler, 50);
                return;
            }}

            function getUTMZoneLetter(lat) {{
                if (lat >= -80 && lat < 72) {{
                    const letters = 'CDEFGHJKLMNPQRSTUVWX';
                    const index = Math.floor((lat + 80) / 8);
                    return letters[index];
                }} else if (lat >= 72 && lat <= 84) {{
                    return 'X';
                }} else {{
                    return '?';
                }}
            }}

            function handleCoordinates(lat, lon) {{
                if (lat < -80 || lat > 84) {{
                    alert('UTM-System ist nur zwischen 80°S und 84°N definiert!');
                    return;
                }}
                if (lon < -180 || lon > 180) {{
                    alert('Längengrad muss zwischen -180° und 180° liegen!');
                    return;
                }}

                var zoneNumber = Math.floor((lon + 180) / 6) + 1;
                var hemi = lat >= 0 ? 'N' : 'S';

                fetch('/update_zone', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        lat: lat,
                        lon: lon,
                        zone: zoneNumber,
                        hemi: hemi
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'ok') {{
                        window.location.href = '/?t=' + Date.now();
                    }}
                }})
                .catch(err => {{
                    console.error('Fehler:', err);
                    alert('Fehler bei der Verarbeitung!');
                }});
            }}

            map.on('click', function(e) {{
                var lat = e.latlng.lat;
                var lon = e.latlng.lng;
                handleCoordinates(lat, lon);
            }});

            window.sendCoordinates = handleCoordinates;
        }}

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', attachClickHandler);
        }} else {{
            attachClickHandler();
        }}
    }})();
    </script>
    """

    form_html = f"""
    <div id="coord-form" style="
        position: absolute; 
        top: 10px; 
        right: 10px; 
        background: white; 
        padding: 15px; 
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 1000;
        font-family: Arial, sans-serif;
        min-width: 220px;">

        <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">
            📍 Koordinaten-Eingabe
        </h3>

        <div style="margin-bottom: 10px;">
            <label style="display: block; margin-bottom: 3px; font-size: 12px; color: #666;">
                Breitengrad (-80° bis 84°):
            </label>
            <input type="number" step="any" id="latInput" 
                   placeholder="z.B. 48.2283" 
                   style="width: 100%; padding: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;"
                   min="-80" max="84">
        </div>

        <div style="margin-bottom: 10px;">
            <label style="display: block; margin-bottom: 3px; font-size: 12px; color: #666;">
                Längengrad (-180° bis 180°):
            </label>
            <input type="number" step="any" id="lonInput" 
                   placeholder="z.B. 12.6247"
                   style="width: 100%; padding: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;"
                   min="-180" max="180">
        </div>

        <button id="goBtn" style="
            width: 100%; 
            padding: 8px; 
            background: #FF0000; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            box-sizing: border-box;">
            UTM-Zone anzeigen
        </button>

        <button id="resetBtn" style="
            width: 100%; 
            padding: 6px; 
            background: #666; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
            font-size: 12px;
            margin-top: 5px;
            box-sizing: border-box;">
            Karte zurücksetzen
        </button>

        <div style="margin-top: 10px; font-size: 10px; color: #999; line-height: 1.3;">
            Klicke auf die Karte oder gib Koordinaten ein
        </div>
    </div>

    <script>
    (function() {{
        document.getElementById('goBtn').addEventListener('click', function() {{
            var lat = parseFloat(document.getElementById('latInput').value);
            var lon = parseFloat(document.getElementById('lonInput').value);

            if (!isNaN(lat) && !isNaN(lon)) {{
                window.sendCoordinates(lat, lon);
            }} else {{
                alert('Bitte gültige Zahlen für Breiten- und Längengrad eingeben!');
            }}
        }});

        document.getElementById('resetBtn').addEventListener('click', function() {{
            fetch('/reset', {{ method: 'POST' }})
            .then(() => {{
                window.location.href = '/?t=' + Date.now();
            }})
            .catch(err => console.error('Reset fehlgeschlagen:', err));
        }});

        document.getElementById('latInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                document.getElementById('goBtn').click();
            }}
        }});

        document.getElementById('lonInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                document.getElementById('goBtn').click();
            }}
        }});
    }})();
    </script>
    """

    m.get_root().html.add_child(Element(click_js + form_html))

    return m


@app.route('/')
def index():
    global current_selection

    if current_selection:
        m = create_map(
            selected_zone=current_selection['zone'],
            selected_lat=current_selection['lat'],
            selected_lon=current_selection['lon']
        )
    else:
        m = create_map()

    return m._repr_html_()


@app.route('/update_zone', methods=['POST'])
def update_zone():
    global current_selection

    data = request.get_json()
    current_selection = {
        'lat': data['lat'],
        'lon': data['lon'],
        'zone': int(data['zone']),
        'hemi': data['hemi']
    }

    return jsonify({'status': 'ok'})


@app.route('/reset', methods=['POST'])
def reset():
    global current_selection
    current_selection = None
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 60)
    print("UTM-Zonen Visualisierung")
    print("=" * 60)
    print("\nFlask-Server läuft auf: http://127.0.0.1:5000")
    print("\nAnleitung:")
    print("  1. Öffne die URL im Browser")
    print("  2. Klicke auf einen Punkt auf der Karte ODER")
    print("  3. Gib Koordinaten manuell ein")
    print("  4. Die UTM-Zone wird automatisch markiert")
    print("\nHinweis: UTM-System ist nur zwischen 80°S und 84°N definiert")
    print("=" * 60)
    print()

    app.run(debug=True, port=5000)



