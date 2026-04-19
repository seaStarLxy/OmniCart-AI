import os

def merge_python_files(source_dir, output_file):
    """
    将 source_dir 目录下所有的 .py 文件合并到 output_file 中，并跳过隐藏目录。
    """
    output_filename = os.path.basename(output_file)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(source_dir):
            # 原地修改 dirs 列表，过滤掉所有以 . 开头的隐藏目录
            # 这样 os.walk 就不会进入这些目录进行递归
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # 排除以 . 开头的隐藏文件以及输出文件本身
                if file.endswith('.py') and not file.startswith('.') and file != output_filename:
                    file_path = os.path.join(root, file)
                    
                    outfile.write(f"\n{'='*60}\n")
                    outfile.write(f"文件路径: {file_path}\n")
                    outfile.write(f"{'='*60}\n\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                            outfile.write("\n\n")
                        print(f"已成功合并: {file_path}")
                    except Exception as e:
                        print(f"读取文件 {file_path} 时出错: {e}")

if __name__ == "__main__":
    target_directory = "." 
    result_filename = "all_code_summary.txt"
    
    merge_python_files(target_directory, result_filename)
    print(f"\n所有 Python 代码已总结至: {result_filename} (已跳过隐藏目录)")