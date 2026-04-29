import pandas as pd
import re

def clean_text(text):
    """
    核心清洗逻辑
    """
    if pd.isna(text) or not isinstance(text, str):
        return text
    
    # 1. 去除双引号 (包含中英文引号)
    text = re.sub(r'["“”]', '', text)
    
    # 2. 去除连续的大写字母 (2个及以上)
    text = re.sub(r'[A-Z]{2,}', '', text)
    
    # 3. 去除特殊符号/乱码（只保留英文字母、数字、常用标点和空格）
    text = re.sub(r'[^a-zA-Z0-9\s,.\'\-]', '', text)
    
    # 4. 去除首尾多余空格
    return text.strip()

def process_excel_pro(input_file, output_file):
    # 读取 Excel 文件
    print(f"正在读取文件: {input_file}...")
    df = pd.read_excel(input_file)
    original_count = len(df)
    
    # --- 步骤 1: 去重 (完全重复的行) ---
    df = df.drop_duplicates().reset_index(drop=True)
    after_dedup_count = len(df)
    
    # --- 步骤 2: 文本清洗 ---
    # 对全表所有的字符串列进行清洗
    for col in df.columns:
        if df[col].dtype == 'object':  # 只处理文本类型的列
            df[col] = df[col].apply(clean_text)
            
    # --- 步骤 3: 再次去重 (防止清洗后产生的重复) ---
    # 比如两行原本因为乱码不同，清洗后变一模一样了，需再次去重
    df = df.drop_duplicates().reset_index(drop=True)
    final_count = len(df)
    
    # 保存结果
    df.to_excel(output_file, index=False)
    
    # 打印统计报告
    print("-" * 30)
    print(f"处理完成！报告如下：")
    print(f"1. 原始数据量: {original_count} 条")
    print(f"2. 剔除重复行及无效数据后: {final_count} 条")
    print(f"3. 总计减少: {original_count - final_count} 条")
    print(f"结果已保存至: {output_file}")

# --- 执行 ---
if __name__ == "__main__":
    # 请确保 book_descriptions910-940.xlsx 在当前目录下，或者填写完整路径
    process_excel_pro('book_descriptions910-940.xlsx', 'cleaned_output.xlsx')