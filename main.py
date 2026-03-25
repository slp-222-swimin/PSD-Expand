import sys
import re
from pathlib import Path
from psd_tools import PSDImage
from PIL import Image


def sanitize_filename(name: str) -> str:
    """ファイル名として使用できない文字を置換"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def export_layers_recursive(layer_or_group, current_dir: Path, psd_size):
    """再帰的にレイヤー構造をディレクトリとして書き出し（座標保持版）"""
    
    if not layer_or_group.is_visible():
        return

    clean_name = sanitize_filename(layer_or_group.name)

    if layer_or_group.is_group():
        # 📂 グループならフォルダ作成
        group_dir = current_dir / clean_name
        group_dir.mkdir(parents=True, exist_ok=True)
        print(f"  Directory: {group_dir.relative_to(current_dir.parent)}")

        for child in layer_or_group:
            export_layers_recursive(child, group_dir, psd_size)

    else:
        # 🖼️ レイヤーならフルキャンバスで保存
        try:
            layer_image = layer_or_group.composite()
            if layer_image is None:
                return

            # PSD全体サイズの透明画像を作成
            full_image = Image.new("RGBA", psd_size, (0, 0, 0, 0))

            # レイヤーの位置情報取得
            bbox = layer_or_group.bbox  # (left, top, right, bottom)

            # 貼り付け位置（左上）
            paste_position = (bbox.x1, bbox.y1)

            # 元の位置に貼り付け
            full_image.paste(layer_image, paste_position, layer_image)

            # 保存
            output_path = current_dir / f"{clean_name}.png"
            full_image.save(output_path)

            print(f"    Saved (full canvas): {clean_name}.png")

        except Exception as e:
            print(f"    ⚠️ Skip {clean_name}: {e}")


def main():
    """メイン実行フロー"""
    
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print("--- PSD Extraction Tool (Full Canvas Mode) ---")
        input_path = input("PSDのパスを入力してください: ").strip('" ')
        output_path = input("出力フォルダを入力してください: ").strip('" ')

    psd_file = Path(input_path)
    export_root = Path(output_path)

    # バリデーション
    if not psd_file.exists() or psd_file.suffix.lower() != '.psd':
        print(f"❌ エラー: 有効なPSDファイルが見つかりません ({input_path})")
        return

    try:
        print(f"\n🚀 解析開始: {psd_file.name}")
        psd = PSDImage.open(psd_file)

        # PSD全体サイズ取得（超重要）
        psd_size = psd.size  # (width, height)

        # 出力先作成
        export_root.mkdir(parents=True, exist_ok=True)

        # レイヤー処理
        for layer in psd:
            export_layers_recursive(layer, export_root, psd_size)

        print(f"\n✅ 完了！ 出力先: {export_root.absolute()}")

    except Exception as e:
        print(f"❌ 実行中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
