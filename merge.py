import os
import shutil
from pathlib import Path


def is_binary(file_path):
    try:
        with open(file_path, 'tr') as check_file:
            check_file.read(1024)
            return False
    except Exception:
        return True

def merge_files(source_dir, output_file, exclude_dirs=None):
    source_path = Path(source_dir).resolve()
    output_path = Path(output_file).resolve()
    
    # 获取当前运行脚本的绝对路径，防止“我合并我自己”
    script_path = Path(__file__).resolve()
    
    base_excludes = {'venv', '.venv', 'node_modules', '.git', 'frontend'}
    if exclude_dirs:
        base_excludes.update(exclude_dirs)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_count = 0

    with output_path.open('w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(source_path):
            rel_root = Path(root).relative_to(source_path)
            
            # --- 目录过滤逻辑 ---
            dirs[:] = [d for d in dirs if d not in base_excludes]
            
            # 允许进入 .github/workflows 但过滤掉其他隐藏目录
            if any(part.startswith('.') for part in rel_root.parts):
                if not ('.github' in rel_root.parts and 'workflows' in rel_root.parts):
                    continue

            for file in sorted(files):
                file_path = (Path(root) / file).resolve()
                
                # --- 核心拦截逻辑 ---
                # 1. 排除输出结果文件本身
                # 2. 排除正在运行的脚本自己 (merge_tool.py)
                # 3. 排除二进制文件
                if file_path == output_path or file_path == script_path or is_binary(file_path):
                    continue
                
                rel_path = file_path.relative_to(source_path)

                outfile.write(f"\n{'='*60}\n")
                outfile.write(f"FILE: {rel_path}\n")
                outfile.write(f"{'='*60}\n\n")
                
                try:
                    with file_path.open('r', encoding='utf-8', errors='replace') as infile:
                        shutil.copyfileobj(infile, outfile)
                    outfile.write("\n\n")
                    print(f"✅ 已合并: {rel_path}")
                    merged_count += 1
                except Exception as e:
                    print(f"❌ 跳过: {rel_path} ({e})")

    return merged_count

if __name__ == "__main__":
    TARGET = os.getenv("TARGET_DIR", ".")
    OUTPUT = os.getenv("OUTPUT_FILE", "summary.txt")
    
    print("🚀 开始合并 (包含 CI/CD 配置，排除 frontend，且排除脚本自身)...")
    count = merge_files(TARGET, OUTPUT)
    print(f"\n✨ 完成！共处理 {count} 个文件。")