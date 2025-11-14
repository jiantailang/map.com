# create_map_with_hover.py
# CSV (land_data.csv) を読み込んで konan_map.html を生成するスクリプト
# 以前の挙動（マーカー + hoverで所有者の他土地をハイライト、クリックでポップアップ）を踏襲します。

import folium
import pandas as pd
from branca.element import Element
import os

# ---------- A: 設定 ----------
csv_filename = 'land_data.csv'   # ここにあなたのCSVを置く（同フォルダ）
map_filename = 'konan_map.html'  # 既存ファイルを上書きしたくない場合は別名に変更してください

# ---------- B: CSV 存在確認 ----------
if not os.path.exists(csv_filename):
    raise FileNotFoundError(f"CSVファイル '{csv_filename}' が見つかりません。スクリプトと同じフォルダに置いてください。")

# ---------- C: CSV 読み込み ----------
# 必要なカラム: owner,age,address,status_sell,status_help,lat,lon,profile
df = pd.read_csv(csv_filename, dtype={'owner': str, 'age': str, 'address': str,
                                      'status_sell': str, 'status_help': str, 'profile': str})

# 緯度経度は数値に変換（欠損があるとエラーになるので簡単なチェック）
if 'lat' not in df.columns or 'lon' not in df.columns:
    raise ValueError("CSV に 'lat' と 'lon' の列が必要です（小数で記入）。")

df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
if df['lat'].isnull().any() or df['lon'].isnull().any():
    raise ValueError("CSV の lat/lon に数値でない値が含まれています。確認してください。")

# ---------- D: 地図作成（中心をデータの平均座標に） ----------
if not df.empty:
    center_lat = float(df['lat'].mean())
    center_lon = float(df['lon'].mean())
else:
    center_lat = 35.3338
    center_lon = 136.8668

m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

# ---------- E: マーカー追加（CSVの各行をマーカーへ） ----------
marker_info = []

for idx, row in df.iterrows():
    owner = str(row.get('owner', '')).strip()
    age = str(row.get('age', '')).strip()
    address = str(row.get('address', '')).strip()
    status_sell = str(row.get('status_sell', '')).strip()
    status_help = str(row.get('status_help', '')).strip()
    lat = float(row['lat'])
    lon = float(row['lon'])
    profile = str(row.get('profile', '')).strip()

    # 色の判定ルール（必要ならカスタマイズ）
    color = 'green'
    if status_sell == '売りたい':
        color = 'red'
    elif status_help == '人手不足':
        color = 'orange'

    popup_html = f"""
    <div style="min-width:220px">
      <b>所有者: {owner} ({age}歳)</b><br>
      所在地: {address}<br>
      <hr style="margin:6px 0;">
      <b>土地の意向: {status_sell}</b><br>
      <b>人手の状況: {status_help}</b><br>
      <hr style="margin:6px 0;">
      <div style="font-size:90%;">プロフィール:<br>{profile}</div>
    </div>
    """

    marker = folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=f"{owner} の土地 ({address})",
        icon=folium.Icon(color=color, icon='leaf', prefix='fa')
    )
    marker.add_to(m)

    marker_info.append({
        'js_var': marker.get_name(),
        'owner': owner,
        'color': color
    })

# ---------- F: JS を作ってホバーで同一所有者をハイライト ----------
js_lines = []
for info in marker_info:
    owner_js_key = info['owner'].replace("'", "\\'")
    js_lines.append(f"if(!ownerMap['{owner_js_key}']) ownerMap['{owner_js_key}'] = [];")
    js_lines.append(f"ownerMap['{owner_js_key}'].push({info['js_var']});")
    js_lines.append(f"{info['js_var']}.originalColor = '{info['color']}';")

for info in marker_info:
    owner_js_key = info['owner'].replace("'", "\\'")
    js_lines.append(f"""{info['js_var']}.on('mouseover', function(e) {{ highlightOwner('{owner_js_key}', true); }});""")
    js_lines.append(f"""{info['js_var']}.on('mouseout', function(e) {{ highlightOwner('{owner_js_key}', false); }});""")

full_js = f"""
<script>
(function() {{
  var ownerMap = {{}};

  {chr(10).join(js_lines)}

  function highlightOwner(owner, on) {{
    var arr = ownerMap[owner];
    if(!arr) return;
    arr.forEach(function(m) {{
      try {{
        if(on) {{
          m.setIcon(L.AwesomeMarkers.icon({{icon: 'leaf', prefix: 'fa', markerColor: 'blue'}}));
        }} else {{
          var orig = m.originalColor || 'green';
          m.setIcon(L.AwesomeMarkers.icon({{icon: 'leaf', prefix: 'fa', markerColor: orig}}));
        }}
      }} catch(e) {{
        console.error('アイコン切替に失敗しました', e);
      }}
    }});
  }}
}})();
</script>
"""

m.get_root().html.add_child(Element(full_js))

# ---------- G: 保存（既存の konan_map.html を上書きします） ----------
m.save(map_filename)
print(f"地図ファイル '{map_filename}' が作成（または上書き）されました。")
print("ブラウザで開き、マーカーにマウスを載せると同一所有者の他土地が青くハイライトされます。クリックで詳細が出ます。")
