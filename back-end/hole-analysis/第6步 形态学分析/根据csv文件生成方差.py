
import pandas as pd

# 输入 CSV 文件路径
csv_file = "2.csv"

# 1. 加载 CSV 文件
print("加载 CSV 文件...")
df = pd.read_csv(csv_file)
print("文件加载完成，数据如下：")
print(df.head())  # 显示前几行数据

# 2. 计算数值列的标准化方差
# 假设你希望计算 Volume 和 Surface Area 的标准化方差

# 首先计算方差
numerical_columns = ['Volume']
variance = df[numerical_columns].var()  # 计算方差

# 计算熔痕的总表面积或体积
total_area = df['Volume'].sum()  # 假设使用总表面积进行标准化


# 3. 计算标准化方差
standardized_variance_area = variance / total_area

# 4. 输出计算结果
print("标准化方差计算结果（以表面积为标准）：")
print(standardized_variance_area)

