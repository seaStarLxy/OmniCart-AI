import os
from pathlib import Path


def merge_python_files(source_dir, output_file, exclude_dirs=None):
    """
    将 source_dir 目录下所有的 .py 文件合并到 output_file 中。
    
    :param source_dir: 目标根目录
    :param output_file: 输出文件路径
    :param exclude_dirs: 要排除的目录名列表（如 ['venv', 'node_modules']）
    """
    source_path = Path(source_dir)
    output_path = Path(output_file)
    exclude_dirs = set(exclude_dirs) if exclude_dirs else set()
    
    # 使用 count 记录合并的文件数量
    merged_count = 0

    with output_path.open('w', encoding='utf-8') as outfile:
        # 使用 os.walk 是因为原地修改 dirs 列表是过滤目录最高效的方式
        for root, dirs, files in os.walk(source_path):
            # 1. 过滤掉隐藏目录和指定的排除目录
            # dirs[:] 原地修改会直接影响 os.walk 的后续遍历
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in exclude_dirs]
            
            for file in files:
                # 2. 过滤非 .py 文件、隐藏文件以及输出文件本身
                if not file.endswith('.py') or file.startswith('.') or file == output_path.name:
                    continue
                
                file_path = Path(root) / file
                
                # 3. 写入文件头信息
                outfile.write(f"\n{'='*60}\n")
                outfile.write(f"FILE: {file_path.relative_to(source_path)}\n")
                outfile.write(f"{'='*60}\n\n")
                
                try:
                    with file_path.open('r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                        outfile.write("\n\n")
                    print(f"✅ 已合并: {file_path}")
                    merged_count += 1
                except Exception as e:
                    print(f"❌ 读取错误 {file_path}: {e}")

    return merged_count

if __name__ == "__main__":
    # 配置
    target_dir = "." 
    result_file = "all_code_summary.txt"
    # 在这里添加你想排除的目录
    ignore = ["venv", ".venv", "env", "__pycache__", "build", "dist", "frontend"]
    
    print(f"开始扫描目录: {os.path.abspath(target_dir)}\n")
    
    count = merge_python_files(target_dir, result_file, exclude_dirs=ignore)
    
    print(f"\n{'*'*30}")
    print(f"合并完成！共处理 {count} 个 Python 文件。")
    print(f"结果已保存至: {result_file}")