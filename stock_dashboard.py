import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 设置页面配置
st.set_page_config(
    page_title="股票数字化转型指数仪表盘",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加标题和描述
st.title("📈 股票数字化转型指数仪表盘")
st.markdown("基于合并后的年报数据和行业分类，展示上市公司数字化转型情况")

# 数据加载函数
@st.cache_data

def load_data():
    df = pd.read_excel('合并后的文件.xlsx')
    return df

# 加载数据
try:
    df = load_data()
    st.success(f"✅ 数据加载成功！共 {len(df):,} 条记录")
except Exception as e:
    st.error(f"❌ 数据加载失败: {str(e)}")
    st.stop()

# 显示数据概览
st.subheader("数据概览")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总记录数", f"{len(df):,}")
with col2:
    st.metric("上市公司数量", df["股票代码"].nunique())
with col3:
    st.metric("年份范围", f"{df['年份'].min()}-{df['年份'].max()}")
with col4:
    st.metric("行业数量", df["行业代码"].nunique())

# 侧边栏筛选器
st.sidebar.header("筛选条件")

# 年份筛选
year_list = sorted(df["年份"].unique())
selected_years = st.sidebar.multiselect(
    "选择年份",
    year_list,
    default=[year_list[-2]]  # 默认选择倒数第二年，避免选择2023年无行业数据
)

# 行业筛选
# 过滤掉NaN值并确保数据类型一致
industry_list = sorted([industry for industry in df["行业名称"].unique() if pd.notna(industry)])
selected_industries = st.sidebar.multiselect(
    "选择行业",
    industry_list,
    default=None
)

# 显示提示信息
if selected_industries:
    st.sidebar.info("已选择行业筛选")
else:
    st.sidebar.info("未选择行业，将显示所有数据")

# 股票代码搜索
stock_code = st.sidebar.text_input(
    "搜索股票代码",
    placeholder="输入股票代码，如：600000"
)

# 企业名称搜索
company_name = st.sidebar.text_input(
    "搜索企业名称",
    placeholder="输入企业名称，如：浦发银行"
)

# 应用筛选条件
filtered_df = df.copy()

# 年份筛选
if selected_years:
    filtered_df = filtered_df[filtered_df["年份"].isin(selected_years)]
    st.sidebar.info(f"已筛选 {len(selected_years)} 个年份")

# 行业筛选
if selected_industries:
    # 当选择了行业时，筛选出行业名称在选择列表中的数据
    filtered_df = filtered_df[filtered_df["行业名称"].isin(selected_industries)]
    st.sidebar.info(f"已筛选 {len(selected_industries)} 个行业")
else:
    # 当没有选择行业时，保留所有数据（包括行业名称为空的数据）
    st.sidebar.info("未选择行业，将显示所有数据")

# 股票代码筛选
if stock_code:
    filtered_df = filtered_df[filtered_df["股票代码"].astype(str).str.contains(stock_code)]

# 企业名称筛选
if company_name:
    filtered_df = filtered_df[filtered_df["企业名称"].str.contains(company_name, case=False)]

# 显示筛选结果
if len(filtered_df) == 0:
    st.warning("⚠️ 没有找到符合条件的数据！")
    st.info("提示：\n1. 尝试调整筛选条件\n2. 2022-2023年数据无行业分类\n3. 检查输入的股票代码或企业名称是否正确")
    
    # 显示数据可用性说明
    st.subheader("数据可用性说明")
    year_industry_data = {}
    for year in sorted(df["年份"].unique()):
        year_data = df[df["年份"] == year]
        has_industry = year_data["行业名称"].notna().any()
        year_industry_data[year] = has_industry
    
    st.write("各年份行业数据可用性：")
    for year, has_industry in year_industry_data.items():
        status = "✅ 有行业数据" if has_industry else "❌ 无行业数据"
        st.write(f"- {year}: {status}")
    
    # 显示前几行原始数据作为示例
    st.subheader("数据示例")
    st.write("原始数据的前10行：")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.stop()
else:
    st.success(f"找到 {len(filtered_df):,} 条符合条件的数据")

# 数据展示
st.subheader("数据表格")

# 选择要显示的列
display_columns = st.multiselect(
    "选择要显示的列",
    df.columns.tolist(),
    default=["股票代码", "企业名称", "年份", "行业名称", "数字化转型指数", "技术维度", "应用维度"]
)

# 显示筛选后的数据
default_rows = min(10, len(filtered_df))
show_all = st.checkbox("显示所有数据", value=False)

if show_all:
    st.dataframe(filtered_df[display_columns], use_container_width=True)
else:
    st.dataframe(filtered_df[display_columns].head(default_rows), use_container_width=True)
    st.caption(f"显示前{default_rows}行，共{len(filtered_df)}行数据")

# 数据可视化
st.subheader("数据可视化")

# 选择可视化类型
chart_type = st.selectbox(
    "选择图表类型",
    ["年度趋势分析", "行业对比分析", "词频分析", "数字化转型指数分布"]
)

# 年度趋势分析
if chart_type == "年度趋势分析":
    st.write("### 年度数字化转型指数趋势")
    
    # 按年份分组计算平均值
    trend_data = filtered_df.groupby("年份").agg({
        "数字化转型指数": "mean",
        "技术维度": "mean",
        "应用维度": "mean"
    }).reset_index()
    
    # 创建折线图
    fig = px.line(
        trend_data,
        x="年份",
        y=["数字化转型指数", "技术维度", "应用维度"],
        title="年度数字化转型指数趋势",
        labels={"value": "指数值", "variable": "指标类型"},
        markers=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 行业对比分析
elif chart_type == "行业对比分析":
    st.write("### 行业数字化转型指数对比")
    
    # 按行业分组计算平均值
    industry_data = filtered_df.groupby("行业名称").agg({
        "数字化转型指数": "mean"
    }).reset_index()
    
    # 只显示有行业名称的数据
    industry_data = industry_data.dropna(subset=["行业名称"])
    
    if len(industry_data) > 0:
        # 排序并取前20个行业
        industry_data = industry_data.sort_values("数字化转型指数", ascending=False).head(20)
        
        # 创建柱状图
        fig = px.bar(
            industry_data,
            x="行业名称",
            y="数字化转型指数",
            title="各行业数字化转型指数对比（前20名）",
            labels={"数字化转型指数": "平均数字化转型指数"},
            color="数字化转型指数",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("没有足够的行业数据生成对比图")
        st.info("提示：2022-2023年数据无行业分类")

# 词频分析
elif chart_type == "词频分析":
    st.write("### 数字技术词频分析")
    
    # 选择词频类型
    word_freq_type = st.radio(
        "选择词频类型",
        ["人工智能词频数", "大数据词频数", "云计算词频数", "区块链词频数", "数字技术运用词频数"]
    )
    
    # 按年份分组计算平均值
    word_freq_data = filtered_df.groupby("年份").agg({
        word_freq_type: "mean"
    }).reset_index()
    
    # 创建柱状图
    fig = px.bar(
        word_freq_data,
        x="年份",
        y=word_freq_type,
        title=f"年度{word_freq_type}趋势",
        labels={word_freq_type: "平均词频数"},
        color=word_freq_type,
        color_continuous_scale=px.colors.sequential.Blues
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 数字化转型指数分布
elif chart_type == "数字化转型指数分布":
    st.write("### 数字化转型指数分布")
    
    # 创建直方图
    fig = px.histogram(
        filtered_df,
        x="数字化转型指数",
        title="数字化转型指数分布",
        labels={"数字化转型指数": "数字化转型指数", "count": "企业数量"},
        color_discrete_sequence=["#3498db"],
        nbins=50
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 个股分析
if len(filtered_df) > 0:
    st.subheader("个股分析")
    
    # 获取筛选后数据中的股票列表
    stock_options = sorted(filtered_df["股票代码"].unique())
    
    if stock_options:
        selected_stock = st.selectbox(
            "选择股票代码",
            stock_options
        )
        
        if selected_stock:
            stock_data = filtered_df[filtered_df["股票代码"] == selected_stock]
            if not stock_data.empty:
                company_name = stock_data["企业名称"].iloc[0]
                st.write(f"### {company_name}（{selected_stock}）数字化转型分析")
                
                # 显示基本信息
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**基本信息**")
                    st.write(f"企业名称：{company_name}")
                    
                    # 处理行业名称可能为空的情况
                    industry = stock_data['行业名称'].iloc[0]
                    st.write(f"行业：{industry if pd.notna(industry) else '无行业数据'}")
                    
                    st.write(f"数据年份范围：{stock_data['年份'].min()} - {stock_data['年份'].max()}")
                
                with col2:
                    st.write("**最新年度数据（数字化转型指数）**")
                    latest_data = stock_data[stock_data['年份'] == stock_data['年份'].max()]
                    st.metric("数字化转型指数", f"{latest_data['数字化转型指数'].iloc[0]:.2f}")
                    st.metric("技术维度", f"{latest_data['技术维度'].iloc[0]:.2f}")
                    st.metric("应用维度", f"{latest_data['应用维度'].iloc[0]:.2f}")
                
                # 显示个股趋势
                st.write("**年度趋势**")
                if len(stock_data) > 1:
                    fig = px.line(
                        stock_data,
                        x="年份",
                        y=["数字化转型指数", "技术维度", "应用维度"],
                        title=f"{company_name}数字化转型趋势",
                        labels={"value": "指数值", "variable": "指标类型"},
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("只有一年数据，无法显示趋势图")
                
                # 显示词频趋势
                st.write("**词频趋势**")
                if len(stock_data) > 1:
                    fig = px.line(
                        stock_data,
                        x="年份",
                        y=["人工智能词频数", "大数据词频数", "云计算词频数", "区块链词频数", "数字技术运用词频数"],
                        title=f"{company_name}数字技术词频趋势",
                        labels={"value": "词频数", "variable": "技术类型"},
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("只有一年数据，无法显示词频趋势图")
            else:
                st.warning("未找到该股票的数据")
    else:
        st.info("当前筛选条件下没有可用的股票数据")

# 添加页脚
st.markdown("---")
st.markdown("© 2025 股票数字化转型指数分析仪表盘 | 基于Streamlit构建")