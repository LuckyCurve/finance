import numpy as np
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

st.title("Streamlit ECharts 饼状图完整指南")

# 1. 基本饼状图
st.header("1. 基本饼状图")

basic_pie_options = {
    "title": {"text": "销售来源分布", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"orient": "vertical", "left": "left"},
    "series": [
        {
            "name": "销售来源",
            "type": "pie",
            "radius": "50%",
            "data": [
                {"value": 1048, "name": "搜索引擎"},
                {"value": 735, "name": "直接访问"},
                {"value": 580, "name": "邮件营销"},
                {"value": 484, "name": "联盟广告"},
                {"value": 300, "name": "视频广告"},
            ],
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                }
            },
        }
    ],
}

st_echarts(options=basic_pie_options, height="400px", theme="dark")

# 2. 环形饼状图
st.header("2. 环形饼状图")

donut_pie_options = {
    "title": {"text": "市场份额", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "市场份额",
            "type": "pie",
            "radius": ["40%", "70%"],  # 内径和外径
            "avoidLabelOverlap": False,
            "data": [
                {"value": 335, "name": "产品A"},
                {"value": 310, "name": "产品B"},
                {"value": 234, "name": "产品C"},
                {"value": 135, "name": "产品D"},
                {"value": 1548, "name": "产品E"},
            ],
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                }
            },
            "labelLine": {"show": False},
            "label": {"show": False, "position": "center"},
        }
    ],
}

st_echarts(options=donut_pie_options, height="400px")

# 3. 南丁格尔玫瑰图
st.header("3. 南丁格尔玫瑰图")

rose_pie_options = {
    "title": {"text": "南丁格尔玫瑰图", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "访问来源",
            "type": "pie",
            "radius": [20, 100],
            "center": ["50%", "50%"],
            "roseType": "area",  # 玫瑰图类型
            "itemStyle": {"borderRadius": 8},
            "data": [
                {"value": 40, "name": "搜索引擎"},
                {"value": 38, "name": "直接访问"},
                {"value": 32, "name": "邮件营销"},
                {"value": 30, "name": "联盟广告"},
                {"value": 28, "name": "视频广告"},
                {"value": 26, "name": "百度"},
                {"value": 22, "name": "谷歌"},
                {"value": 18, "name": "必应"},
                {"value": 1800, "name": "必应2"},
            ],
        }
    ],
}

st_echarts(options=rose_pie_options, height="400px")

# 4. 多层饼状图
st.header("4. 多层饼状图")

multi_pie_options = {
    "title": {"text": "多层饼状图", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "内层",
            "type": "pie",
            "selectedMode": "single",
            "radius": [0, "30%"],
            "label": {"position": "inner", "fontSize": 14},
            "labelLine": {"show": False},
            "data": [
                {"value": 1548, "name": "移动端", "selected": True},
                {"value": 775, "name": "PC端"},
            ],
        },
        {
            "name": "外层",
            "type": "pie",
            "radius": ["45%", "60%"],
            "labelLine": {"length": 30},
            "label": {
                "formatter": "{a|{a}}{abg|}\n{hr|}\n{b|{b}：}{c}  {per|{d}%}",
                "backgroundColor": "#F6F8FC",
                "borderColor": "#8C8D8E",
                "borderWidth": 1,
                "borderRadius": 4,
            },
            "data": [
                {"value": 435, "name": "iOS"},
                {"value": 679, "name": "Android"},
                {"value": 434, "name": "微信小程序"},
                {"value": 335, "name": "Windows"},
                {"value": 440, "name": "Mac"},
            ],
        },
    ],
}

st_echarts(options=multi_pie_options, height="500px")

# 5. 自定义颜色饼状图
st.header("5. 自定义颜色饼状图")

custom_colors = [
    "#FF6B6B",
    "#4ECDC4",
    "#45B7D1",
    "#96CEB4",
    "#FECA57",
    "#FF9FF3",
    "#54A0FF",
]

custom_color_pie_options = {
    "title": {"text": "自定义颜色饼状图", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "color": custom_colors,
    "series": [
        {
            "name": "访问来源",
            "type": "pie",
            "radius": "55%",
            "center": ["50%", "60%"],
            "data": [
                {"value": 335, "name": "直接访问"},
                {"value": 310, "name": "邮件营销"},
                {"value": 234, "name": "联盟广告"},
                {"value": 135, "name": "视频广告"},
                {"value": 1548, "name": "搜索引擎"},
                {"value": 251, "name": "百度"},
                {"value": 147, "name": "谷歌"},
            ],
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                }
            },
        }
    ],
}

st_echarts(options=custom_color_pie_options, height="400px")

# 6. 带动画的饼状图
st.header("6. 带动画的饼状图")

animated_pie_options = {
    "title": {"text": "动画饼状图", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "animationType": "scale",
    "animationEasing": "elasticOut",
    "animationDelay": 200,  # 固定延迟
    "series": [
        {
            "name": "访问来源",
            "type": "pie",
            "radius": "50%",
            "data": [
                {"value": 335, "name": "直接访问"},
                {"value": 310, "name": "邮件营销"},
                {"value": 234, "name": "联盟广告"},
                {"value": 135, "name": "视频广告"},
                {"value": 1548, "name": "搜索引擎"},
            ],
            "animationType": "scale",
            "animationEasing": "elasticOut",
            "animationDelay": 200,  # 固定延迟
            "animationDuration": 1000,
        }
    ],
}

st_echarts(options=animated_pie_options, height="400px")

# 7. 交互式饼状图
st.header("7. 交互式饼状图")

col1, col2 = st.columns(2)
with col1:
    pie_type = st.selectbox("选择饼状图类型", ["普通饼状图", "环形图", "玫瑰图"])
with col2:
    show_percentage = st.checkbox("显示百分比", value=True)

# 生成示例数据
categories = ["类别A", "类别B", "类别C", "类别D", "类别E"]
values = [np.random.randint(100, 500) for _ in categories]
pie_data = [{"value": v, "name": n} for v, n in zip(values, categories)]

# 根据选择设置配置
if pie_type == "环形图":
    radius = ["40%", "70%"]
    rose_type = None
elif pie_type == "玫瑰图":
    radius = [20, 100]
    rose_type = "area"
else:
    radius = "55%"
    rose_type = None

interactive_pie_options = {
    "title": {"text": f"交互式{pie_type}", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "数据",
            "type": "pie",
            "radius": radius,
            "data": pie_data,
            "roseType": rose_type,
            "label": {"formatter": "{b}: {c}" + (" ({d}%)" if show_percentage else "")},
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                }
            },
        }
    ],
}

st_echarts(options=interactive_pie_options, height="400px")

# 8. 使用 Pandas 数据的饼状图
st.header("8. 使用 Pandas 数据的饼状图")

# 创建示例数据
df = pd.DataFrame(
    {
        "category": ["产品A", "产品B", "产品C", "产品D", "产品E"],
        "sales": [1200, 800, 600, 400, 300],
        "profit": [300, 200, 150, 100, 75],
    }
)

st.subheader("数据预览")
st.dataframe(df)

# 选择要显示的列
metric = st.selectbox("选择指标", ["sales", "profit"])

# 转换数据格式
pie_data_from_df = [
    {"value": row[metric], "name": row["category"]} for _, row in df.iterrows()
]

pandas_pie_options = {
    "title": {"text": f"{metric.capitalize()} 分布", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": metric.capitalize(),
            "type": "pie",
            "radius": "55%",
            "data": pie_data_from_df,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                }
            },
        }
    ],
}

st_echarts(options=pandas_pie_options, height="400px")

# 9. 高级样式饼状图
st.header("9. 高级样式饼状图")

advanced_pie_options = {
    "title": {
        "text": "高级样式饼状图",
        "left": "center",
        "textStyle": {"fontSize": 18, "fontWeight": "bold"},
    },
    "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b} : {c} ({d}%)"},
    "legend": {"top": "5%", "left": "center", "textStyle": {"fontSize": 12}},
    "series": [
        {
            "name": "访问来源",
            "type": "pie",
            "radius": "55%",
            "center": ["50%", "60%"],
            "data": [
                {"value": 335, "name": "直接访问"},
                {"value": 310, "name": "邮件营销"},
                {"value": 234, "name": "联盟广告"},
                {"value": 135, "name": "视频广告"},
                {"value": 1548, "name": "搜索引擎"},
            ],
            "itemStyle": {"borderRadius": 10, "borderColor": "#fff", "borderWidth": 2},
            "label": {"show": True, "formatter": "{b}\n{d}%"},
            "labelLine": {"show": True, "length": 15, "length2": 10},
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                }
            },
        }
    ],
}

st_echarts(options=advanced_pie_options, height="450px")

# 10. 配置选项说明
st.header("10. 饼状图配置选项说明")

st.markdown("""
### 主要配置项：

1. **基本配置**:
   - `type: "pie"`: 指定为饼状图
   - `radius`: 饼图半径 (可以是数字、百分比或数组)
   - `center`: 饼图中心位置

2. **数据格式**:
   - `data`: 数据数组，每个元素包含 `value` 和 `name` 属性
   - `name`: 数据项名称
   - `value`: 数据项数值

3. **样式配置**:
   - `itemStyle`: 扇形样式
   - `label`: 标签配置
   - `labelLine`: 标签线配置
   - `emphasis`: 高亮样式

4. **特殊类型**:
   - `roseType: "area"`: 玫瑰图
   - `radius: ["内径", "外径"]`: 环形图

5. **交互配置**:
   - `selectedMode`: 选择模式
   - `avoidLabelOverlap`: 避免标签重叠
""")

# 显示代码模板
with st.expander("查看基本代码模板"):
    st.code(
        """
pie_options = {
    "title": {"text": "饼状图标题", "left": "center"},
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [{
        "name": "数据名称",
        "type": "pie",
        "radius": "55%",
        "data": [
            {"value": 335, "name": "类别1"},
            {"value": 310, "name": "类别2"},
            {"value": 234, "name": "类别3"}
        ],
        "emphasis": {
            "itemStyle": {
                "shadowBlur": 10,
                "shadowOffsetX": 0,
                "shadowColor": "rgba(0, 0, 0, 0.5)"
            }
        }
    }]
}

st_echarts(options=pie_options, height="400px")
""",
        language="python",
    )

# 数据转换示例
with st.expander("Pandas 数据转换示例"):
    st.code(
        """
# 从 DataFrame 转换为 ECharts 饼状图数据格式
df = pd.DataFrame({
    'category': ['A', 'B', 'C'],
    'value': [100, 200, 150]
})

# 转换数据格式
pie_data = [
    {"value": row['value'], "name": row['category']} 
    for _, row in df.iterrows()
]

# 或者使用更简洁的方式
pie_data = df.to_dict('records')  # 如果列名已经是 value 和 name
""",
        language="python",
    )
