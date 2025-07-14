import streamlit as st
from streamlit_echarts import st_echarts

st.title("Streamlit ECharts 桑基图示例")

# 1. 基本桑基图
st.header("1. 基本桑基图 - 能源流向")

basic_sankey_options = {
    "title": {"text": "能源流向桑基图"},
    "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    "series": [
        {
            "type": "sankey",
            "data": [
                {"name": "煤炭"},
                {"name": "石油"},
                {"name": "天然气"},
                {"name": "电力"},
                {"name": "热力"},
                {"name": "工业"},
                {"name": "交通"},
                {"name": "居民"},
                {"name": "商业"},
            ],
            "links": [
                {"source": "煤炭", "target": "电力", "value": 40},
                {"source": "煤炭", "target": "热力", "value": 20},
                {"source": "煤炭", "target": "工业", "value": 15},
                {"source": "石油", "target": "交通", "value": 35},
                {"source": "石油", "target": "工业", "value": 10},
                {"source": "天然气", "target": "电力", "value": 25},
                {"source": "天然气", "target": "热力", "value": 15},
                {"source": "天然气", "target": "居民", "value": 20},
                {"source": "电力", "target": "工业", "value": 30},
                {"source": "电力", "target": "居民", "value": 25},
                {"source": "电力", "target": "商业", "value": 10},
                {"source": "热力", "target": "居民", "value": 20},
                {"source": "热力", "target": "商业", "value": 15},
            ],
            "emphasis": {"focus": "adjacency"},
            "lineStyle": {"color": "gradient", "curveness": 0.5},
        }
    ],
}

st_echarts(options=basic_sankey_options, height="500px", theme="dark")

# 2. 网站流量桑基图
st.header("2. 网站流量分析")

traffic_sankey_options = {
    "title": {"text": "网站流量桑基图"},
    "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    "series": [
        {
            "type": "sankey",
            "data": [
                {"name": "搜索引擎"},
                {"name": "社交媒体"},
                {"name": "直接访问"},
                {"name": "邮件营销"},
                {"name": "首页"},
                {"name": "产品页"},
                {"name": "博客"},
                {"name": "购买"},
                {"name": "注册"},
                {"name": "离开"},
            ],
            "links": [
                {"source": "搜索引擎", "target": "首页", "value": 300},
                {"source": "搜索引擎", "target": "产品页", "value": 200},
                {"source": "搜索引擎", "target": "博客", "value": 100},
                {"source": "社交媒体", "target": "首页", "value": 150},
                {"source": "社交媒体", "target": "博客", "value": 80},
                {"source": "直接访问", "target": "首页", "value": 250},
                {"source": "邮件营销", "target": "产品页", "value": 120},
                {"source": "首页", "target": "产品页", "value": 180},
                {"source": "首页", "target": "注册", "value": 100},
                {"source": "首页", "target": "离开", "value": 420},
                {"source": "产品页", "target": "购买", "value": 150},
                {"source": "产品页", "target": "离开", "value": 350},
                {"source": "博客", "target": "首页", "value": 60},
                {"source": "博客", "target": "离开", "value": 120},
            ],
            "emphasis": {"focus": "adjacency"},
            "lineStyle": {"color": "gradient", "curveness": 0.5},
            "itemStyle": {"borderWidth": 1, "borderColor": "#aaa"},
            "label": {"fontSize": 12},
        }
    ],
}

st_echarts(options=traffic_sankey_options, height="500px")

# 3. 自定义样式的桑基图
st.header("3. 自定义样式桑基图")

custom_sankey_options = {
    "title": {"text": "销售渠道分析", "textStyle": {"fontSize": 16}},
    "tooltip": {
        "trigger": "item",
        "triggerOn": "mousemove",
        "formatter": "{a} <br/>{b} : {c}",
    },
    "series": [
        {
            "type": "sankey",
            "layout": "none",
            "data": [
                {"name": "线上渠道", "itemStyle": {"color": "#2E86AB"}},
                {"name": "线下渠道", "itemStyle": {"color": "#A23B72"}},
                {"name": "合作伙伴", "itemStyle": {"color": "#F18F01"}},
                {"name": "华北", "itemStyle": {"color": "#C73E1D"}},
                {"name": "华南", "itemStyle": {"color": "#7209B7"}},
                {"name": "华东", "itemStyle": {"color": "#560BAD"}},
                {"name": "产品A", "itemStyle": {"color": "#480CA8"}},
                {"name": "产品B", "itemStyle": {"color": "#3A0CA3"}},
                {"name": "产品C", "itemStyle": {"color": "#3F37C9"}},
            ],
            "links": [
                {"source": "线上渠道", "target": "华北", "value": 200},
                {"source": "线上渠道", "target": "华南", "value": 150},
                {"source": "线上渠道", "target": "华东", "value": 300},
                {"source": "线下渠道", "target": "华北", "value": 100},
                {"source": "线下渠道", "target": "华南", "value": 180},
                {"source": "线下渠道", "target": "华东", "value": 120},
                {"source": "合作伙伴", "target": "华北", "value": 80},
                {"source": "合作伙伴", "target": "华南", "value": 60},
                {"source": "华北", "target": "产品A", "value": 150},
                {"source": "华北", "target": "产品B", "value": 130},
                {"source": "华北", "target": "产品C", "value": 100},
                {"source": "华南", "target": "产品A", "value": 120},
                {"source": "华南", "target": "产品B", "value": 140},
                {"source": "华南", "target": "产品C", "value": 130},
                {"source": "华东", "target": "产品A", "value": 180},
                {"source": "华东", "target": "产品B", "value": 160},
                {"source": "华东", "target": "产品C", "value": 80},
            ],
            "emphasis": {"focus": "adjacency"},
            "lineStyle": {"color": "gradient", "curveness": 0.5, "opacity": 0.7},
            "itemStyle": {"borderWidth": 2, "borderColor": "#fff"},
            "label": {"fontSize": 12, "fontWeight": "bold"},
        }
    ],
}

st_echarts(options=custom_sankey_options, height="600px")

# 4. 动态数据桑基图
st.header("4. 动态数据桑基图")

# 添加控制组件
col1, col2 = st.columns(2)
with col1:
    scale_factor = st.slider("数据缩放倍数", 0.5, 2.0, 1.0, 0.1)
with col2:
    show_values = st.checkbox("显示数值", value=True)

import numpy as np
import pandas as pd

# 生成动态数据
np.random.seed(42)
base_data = {
    "source": ["A", "A", "A", "B", "B", "C", "C", "C"],
    "target": ["D", "E", "F", "D", "E", "D", "E", "F"],
    "value": [20, 30, 25, 15, 35, 10, 20, 15],
}

df = pd.DataFrame(base_data)
df["value"] = (df["value"] * scale_factor).round().astype(int)

# 构建桑基图数据
nodes = list(set(df["source"].tolist() + df["target"].tolist()))
links = df.to_dict("records")

dynamic_sankey_options = {
    "title": {"text": f"动态桑基图 (缩放: {scale_factor}x)"},
    "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    "series": [
        {
            "type": "sankey",
            "data": [{"name": name} for name in nodes],
            "links": links,
            "emphasis": {"focus": "adjacency"},
            "lineStyle": {"color": "gradient", "curveness": 0.5},
            "label": {"show": show_values, "fontSize": 12},
        }
    ],
}

st_echarts(options=dynamic_sankey_options, height="400px")

# 5. 使用 Pandas 数据的桑基图
st.header("5. 从 CSV 数据创建桑基图")

# 创建示例数据
sample_data = pd.DataFrame(
    {
        "from": [
            "步骤1",
            "步骤1",
            "步骤1",
            "步骤2",
            "步骤2",
            "步骤3",
            "步骤3",
            "步骤4",
        ],
        "to": ["步骤2", "步骤3", "步骤4", "步骤3", "步骤4", "步骤4", "步骤5", "步骤5"],
        "value": [100, 80, 20, 60, 40, 90, 50, 100],
        "category": [
            "流程A",
            "流程B",
            "流程C",
            "流程A",
            "流程B",
            "流程A",
            "流程B",
            "流程A",
        ],
    }
)

st.subheader("数据预览")
st.dataframe(sample_data)

# 构建桑基图
all_nodes = list(set(sample_data["from"].tolist() + sample_data["to"].tolist()))
links_data = (
    sample_data[["from", "to", "value"]]
    .rename(columns={"from": "source", "to": "target"})
    .to_dict("records")
)

pandas_sankey_options = {
    "title": {"text": "基于 Pandas 数据的桑基图"},
    "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    "series": [
        {
            "type": "sankey",
            "data": [{"name": name} for name in all_nodes],
            "links": links_data,
            "emphasis": {"focus": "adjacency"},
            "lineStyle": {"color": "gradient", "curveness": 0.5},
            "label": {"fontSize": 12},
        }
    ],
}

st_echarts(options=pandas_sankey_options, height="450px")

# 6. 高级配置说明
st.header("6. 桑基图配置选项说明")

st.markdown("""
### 主要配置项：

1. **数据格式**:
   - `data`: 节点列表，每个节点包含 `name` 属性
   - `links`: 连接列表，每个连接包含 `source`, `target`, `value` 属性

2. **样式配置**:
   - `itemStyle`: 节点样式配置
   - `lineStyle`: 连线样式配置
   - `label`: 标签样式配置

3. **交互配置**:
   - `emphasis.focus`: 高亮模式 ('adjacency' 或 'series')
   - `tooltip`: 提示框配置

4. **布局配置**:
   - `layout`: 布局方式 ('none' 或不设置)
   - `nodeWidth`: 节点宽度
   - `nodeGap`: 节点间距
   - `layoutIterations`: 布局迭代次数

### 使用场景：
- 能源流向分析
- 网站流量分析
- 销售渠道分析
- 资金流向追踪
- 供应链分析
""")

# 显示代码示例
with st.expander("查看基本代码结构"):
    st.code(
        """
sankey_options = {
    "title": {"text": "桑基图标题"},
    "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    "series": [{
        "type": "sankey",
        "data": [
            {"name": "节点1"},
            {"name": "节点2"},
            {"name": "节点3"}
        ],
        "links": [
            {"source": "节点1", "target": "节点2", "value": 100},
            {"source": "节点2", "target": "节点3", "value": 80}
        ],
        "emphasis": {"focus": "adjacency"},
        "lineStyle": {"color": "gradient", "curveness": 0.5}
    }]
}

st_echarts(options=sankey_options, height="500px")
""",
        language="python",
    )
