import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.write("✅ 所有依赖包已成功导入")

# 测试数据文件加载
try:
    df = pd.read_excel('合并后的文件.xlsx')
    st.write(f"✅ 数据文件加载成功！共 {len(df):,} 条记录")
    st.write(f"包含的列：{df.columns.tolist()}")
except Exception as e:
    st.write(f"❌ 数据文件加载失败: {str(e)}")
