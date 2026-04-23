# map.com (農地・山林マッチングサービス)

遊休農地や山林の売買・活用を促進する、地図ベースの土地マッチングプラットフォーム

##  概要
地方における使われていない農地や山林を、新しく農業を始めたい方や土地を活用したい方と結びつけるためのサービスです。
地図情報をベースに直感的に土地を探せるUIを提供し、煩雑な土地の管理や売買のハードルを下げることで、地域課題の解決を目指しています。

##  特徴
- 地図ベースの直感的な検索: マップ上から直接、対象となる農地や山林の場所・広さ・条件を確認可能。
- 遊休地の可視化: 管理が難しくなった土地の情報をデジタル化し、データベースとして整理。
- スムーズなマッチング: 土地の所有者と活用希望者を繋ぐ情報共有機能。

##  使用技術
- Backend: Python (Flask / Django 等)
- Frontend: HTML / CSS / JavaScript (Leaflet.js / Google Maps API 等)
- Database: SQLite / PostgreSQL

##  セットアップ
1. リポジトリのクローン
   ```bash
   git clone [https://github.com/jiantailang/map.com.git](https://github.com/jiantailang/map.com.git)
２.プロジェクトディレクトリへ移動
   cd map.com

３.依存関係のインストール
pip install -r requirements.txt

４.環境変数の設定 (マップAPIキーなどが必要な場合)
.env ファイルを作成し、各種キーを設定してください。
MAP_API_KEY=your_api_key

５.実行
python main.py
