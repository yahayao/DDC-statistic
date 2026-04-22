import pandas as pd
import json

INPUT_FILE = 'merged_dedup_all3cols.xlsx'  # 改成 merged_dedup_all3cols.xlsx 也可

print(f"读取: {INPUT_FILE} ...")
df = pd.read_excel(INPUT_FILE)

# ── 1. DDC 统计（只看不足 100 条的分类）──────────────────────────────
ddc_counts = df.groupby('DDC').size().reset_index(name='count')
under_100 = ddc_counts[ddc_counts['count'] < 100].copy()
under_100['gap_to_100'] = 100 - under_100['count']
under_100 = under_100.sort_values('DDC').reset_index(drop=True)

ddc_result = under_100.rename(columns={
    'DDC': 'ddc',
    'count': 'current_count',
    'gap_to_100': 'gap_to_100'
}).to_dict(orient='records')

# ── 2. Abstract/description 长度统计 ─────────────────────────────────
desc_lengths = df['description'].astype(str).str.len()

abstract_stats = {
    'max': int(desc_lengths.max()),
    'min': int(desc_lengths.min()),
    'mean': round(float(desc_lengths.mean()), 2),
    'total_records': len(df)
}

# ── 3. 汇总输出 ───────────────────────────────────────────────────────
# 找出 001-999 中完全缺失的 DDC（整数部分补零后比对）
def pad_ddc(val):
    val = str(val).strip()
    if '.' in val:
        integer, decimal = val.split('.', 1)
        return integer.zfill(3) + '.' + decimal
    return val.zfill(3)

all_ddc = {str(i).zfill(3) for i in range(1, 1000)}
existing_ddc = set(ddc_counts['DDC'].apply(pad_ddc))
# 只取纯整数三位码做对比（忽略带小数点的细分码）
existing_int_ddc = {d for d in existing_ddc if '.' not in d}
missing_ddc = sorted(all_ddc - existing_int_ddc)

output = {
    'abstract_stats': abstract_stats,
    'ddc_missing_001_to_999': {
        'count': len(missing_ddc),
        'codes': missing_ddc
    },
    'ddc_under_100': {
        'total_ddc_classes': int(len(ddc_counts)),
        'ddc_over_100_count': int((ddc_counts['count'] >= 100).sum()),
        'ddc_over_100_total_records': int(ddc_counts[ddc_counts['count'] >= 100]['count'].sum()),
        'ddc_under_100_count': int(len(under_100)),
        'details': ddc_result
    }
}

output_path = 'statistics.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"完成！结果已保存至: {output_path}")
print(f"\n── Abstract 统计 ──")
print(f"  最长: {abstract_stats['max']} 字符")
print(f"  最短: {abstract_stats['min']} 字符")
print(f"  平均: {abstract_stats['mean']} 字符")
print(f"\n── DDC 统计 ──")
print(f"  001-999 中完全缺失的分类: {len(missing_ddc)} 个")
print(f"  缺失列表: {missing_ddc[:20]}{'...' if len(missing_ddc) > 20 else ''}")
print(f"  总分类数: {output['ddc_under_100']['total_ddc_classes']}")
print(f"  >= 100 条的分类: {output['ddc_under_100']['ddc_over_100_count']} 个，共 {output['ddc_under_100']['ddc_over_100_total_records']} 条记录")
print(f"  < 100 条的分类:  {output['ddc_under_100']['ddc_under_100_count']}")
