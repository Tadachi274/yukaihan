input_filename = "html.txt"  # 読み込むファイル名
output_filename = "output.txt"  # 保存するファイル名

with open(input_filename, "r", encoding="utf-8") as infile, open(output_filename, "w", encoding="utf-8") as outfile:
    for line in infile:
        outfile.write(line.lstrip('#'))  # 行頭の#を削除して書き込む