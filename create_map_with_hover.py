# create_map_with_hover.py
import folium
import pandas as pd
from branca.element import Element

# ---------- サンプルデータ（ここを編集してテストできます） ----------
data = {
    'owner': ['田中 太郎', '田中 太郎', '鈴木 一郎', '鈴木 一郎', '佐藤 花子'],
    'age': [75, 75, 52, 52, 43],
    'address': [
        '草井町100番地 (A-1)',
        '草井町105番地 (A-2)',
        '草井町110番地 (B-1)',
        '草井町112番地 (B-2)',
        '草井町120番地 (C-1)'
    ],
    'status_sell': ['売りたい', '売りたい', '売りたくない', '売りたくない', '売りたくない'],
    'status_help': ['人手不足', '人手不足', '人手不足', '人手は足りている', '人手は足りている'],
    # 架空の緯度経度（江南市の近辺、デモ用）
    'lat': [35.3450, 35.3455, 35.3420, 35.3425, 35.3400],
    'lon': [136.8700, 136.8710, 136.8720, 136.8730, 136.8740],
    'profile': [
        '後継者不在。土地をまとめて手放したい。',
        '後継者不在。土地をまとめて手放したい。',
        '特産のネギを栽培。収穫期に人手不足。',
        '特産のネギを栽培。収穫期に人手不足。',
        '兼業農家。現状維持で満足。'
    ]
}
df = pd.DataFrame(data)

# ---------- 地図作成 ----------
center_lat = 35.3338
center_lon = 136.8668
m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

marker_info = []
for idx, row in df.iterrows():
    # 色分けルール（カスタマイズ可）
    color = 'green'
    if row['status_sell'] == '売りたい':
        color = 'red'
    elif row['status_help'] == '人手不足':
        color = 'orange'

    popup_html = f"""
    <div style="min-width:200px">
      <b>所有者: {row['owner']} ({row['age']}歳)</b><br>
      所在地: {row['address']}<br>
      <hr style="margin:6px 0;">
      <b>土地の意向: {row['status_sell']}</b><br>
      <b>人手の状況: {row['status_help']}</b><br>
      <hr style="margin:6px 0;">
      <div style="font-size:90%;">プロフィール:<br>{row['profile']}</div>
    </div>
    """

    icon = folium.Icon(color=color, icon='leaf', prefix='fa')
    marker = folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{row['owner']} の土地 ({row['address']})",
        icon=icon
    )
    marker.add_to(m)

    marker_info.append({
        'js_var': marker.get_name(),
        'owner': row['owner'],
        'color': color
    })

# ---------- JS を生成して地図に埋め込む（ホバーで同一所有者をハイライト） ----------
js_lines = []
for info in marker_info:
    owner_js_key = info['owner'].replace("'", "\\'")
    js_lines.append(f"if(!ownerMap['{owner_js_key}']) ownerMap['{owner_js_key}'] = [];")
    js_lines.append(f"ownerMap['{owner_js_key}'].push({info['js_var']});")
    js_lines.append(f"{info['js_var']}.originalColor = '{info['color']}';")

for info in marker_info:
    owner_js_key = info['owner'].replace("'", "\\'")
    js_lines.append(
        f"""{info['js_var']}.on('mouseover', function(e) {{ highlightOwner('{owner_js_key}', true); }});"""
    )
    js_lines.append(
        f"""{info['js_var']}.on('mouseout', function(e) {{ highlightOwner('{owner_js_key}', false); }});"""
    )

full_js = f"""
<script>
(function() {{
  var ownerMap = {{}};

  {chr(10).join(js_lines)}

  function highlightOwner(owner, on) {{
    var arr = ownerMap[owner];
    if(!arr) return;
    arr.forEach(function(m) {{
      if(on) {{
        m.setIcon(L.AwesomeMarkers.icon({{icon: 'leaf', prefix: 'fa', markerColor: 'blue'}}));
      }} else {{
        var orig = m.originalColor || 'green';
        m.setIcon(L.AwesomeMarkers.icon({{icon: 'leaf', prefix: 'fa', markerColor: orig}}));
      }}
    }});
  }}
}})();
</script>
"""

m.get_root().html.add_child(Element(full_js))

# ---------- ファイル保存 ----------
map_filename = 'konan_map.html'
m.save(map_filename)
print(f"地図ファイル '{map_filename}' が作成されました。")
