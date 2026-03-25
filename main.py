import sys
import re
import os
from pathlib import Path
from psd_tools import PSDImage

def sanitize_filename(name: str) -> str:
    """ファイル名として使用できない文字を置換"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def export_layers_recursive(layer_or_group, current_dir: Path):
    """再帰的にレイヤー構造をディレクトリとして書き出し"""
    if not layer_or_group.is_visible():
        return

    clean_name = sanitize_filename(layer_or_group.name)

    if layer_or_group.is_group():
        # 📂 グループならフォルダ作成
        group_dir = current_dir / clean_name
        group_dir.mkdir(parents=True, exist_ok=True)
        print(f"  Directory: {group_dir.relative_to(current_dir.parent)}")

        for child in layer_or_group:
            export_layers_recursive(child, group_dir)
    else:
        # 🖼️ レイヤーなら画像保存
        try:
            image = layer_or_group.composite()
            if image:
                output_path = current_dir / f"{clean_name}.png"
                image.save(output_path)
                print(f"    Saved: {clean_name}.png")
        except Exception as e:
            print(f"    ⚠️ Skip {clean_name}: {e}")

def main():
    """メイン実行フロー"""
    
    # 1. 引数のチェック (Usage: python script.py <input_psd> <output_dir>)
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        # 2. 引数がない場合は対話形式で取得
        print("--- PSD Extraction Tool ---")
        input_path = input("処理したいPSDのパスを入力してください: ").strip('" ')
        output_path = input("書き出し先のディレクトリ名を入力してください: ").strip('" ')

    # パスの正規化
    psd_file = Path(input_path)
    export_root = Path(output_path)

    # バリデーション
    if not psd_file.exists() or psd_file.suffix.lower() != '.psd':
        print(f"❌ エラー: 有効なPSDファイルが見つかりません ({input_path})")
        return

    try:
        print(f"\n🚀 解析開始: {psd_file.name}")
        psd = PSDImage.open(psd_file)
        
        # 出力先のベースフォルダ作成
        export_root.mkdir(parents=True, exist_ok=True)
        
        # 再帰処理の開始
        for layer in psd:
            export_layers_recursive(layer, export_root)
            
        print(f"\n✅ 完了！ 出力先: {export_root.absolute()}")

    except Exception as e:
        print(f"❌ 実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
