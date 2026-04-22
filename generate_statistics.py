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
output = {
    'abstract_stats': abstract_stats,
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
print(f"  总分类数: {output['ddc_under_100']['total_ddc_classes']}")
print(f"  >= 100 条的分类: {output['ddc_under_100']['ddc_over_100_count']} 个，共 {output['ddc_under_100']['ddc_over_100_total_records']} 条记录")
print(f"  < 100 条的分类:  {output['ddc_under_100']['ddc_under_100_count']}")
