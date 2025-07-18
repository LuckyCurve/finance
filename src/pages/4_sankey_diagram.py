import streamlit as st
import streamlit.components.v1 as components
from pyecharts.charts import Sankey
from pyecharts import options as opts
from pyecharts.globals import ThemeType

def draw_sankey_chart() -> None:
    st.title("桑葚图示例 (Sankey Diagram)")

    # 示例数据：节点和链接
    # 节点代表不同的类别或实体
    # 链接代表节点之间的流动或关系
    nodes = [
        {"name": "A"},
        {"name": "B"},
        {"name": "C"},
        {"name": "D"},
        {"name": "E"},
        {"name": "F"},
    ]

    links = [
        {"source": "A", "target": "B", "value": 10},
        {"source": "A", "target": "C", "value": 5},
        {"source": "B", "target": "D", "value": 8},
        {"source": "B", "target": "E", "value": 3},
        {"source": "C", "target": "E", "value": 4},
        {"source": "C", "target": "F", "value": 2},
        {"source": "D", "target": "F", "value": 6},
        {"source": "E", "target": "F", "value": 7},
    ]

    # 创建 Sankey 图实例
    sankey_chart = (
        Sankey(init_opts=opts.InitOpts(theme=ThemeType.DARK)) # Changed to DARK theme
        .add(
            "流量",  # 系列名称
            nodes,
            links,
            pos_left="10%",  # 图表左边距
            pos_right="10%", # ��表右边距
            pos_top="20%",   # 图表上边距
            pos_bottom="20%",# 图表下边距
            # 设置节点标签的格式
            label_opts=opts.LabelOpts(
                position="right",  # 标签位置
                formatter="{b}",   # 显示节点名称
                font_size=12,
            ),
            # 设置边的样式
            itemstyle_opts=opts.ItemStyleOpts(
                border_color="#000", # 边框颜色
                border_width=1,      # 边框宽度
            ),
            # 设置边的标签样式
            linestyle_opt=opts.LineStyleOpts(
                curve=0.5,           # 边的曲线度
                opacity=0.6,         # 边的透明度
                color="source",      # 边的颜色跟随源节点
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="数据流动分析 - 示例1"), # Updated title
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                trigger_on="mousemove",
                formatter="{a} &rarr; {b}: {c}" # 提示框格式
            ),
        )
    )

    # 渲染图表为 HTML
    html = sankey_chart.render_embed()

    # 在 Streamlit 中嵌入 HTML
    components.html(html, height=600)

    st.subheader("桑葚图示例2：能源流向")

    nodes2 = [
        {"name": "煤炭"}, {"name": "石油"}, {"name": "天然气"},
        {"name": "电力"}, {"name": "工业"}, {"name": "交通"}, {"name": "居民"}
    ]

    links2 = [
        {"source": "煤炭", "target": "电力", "value": 80},
        {"source": "石油", "target": "交通", "value": 60},
        {"source": "天然气", "target": "工业", "value": 40},
        {"source": "电力", "target": "工业", "value": 50},
        {"source": "电力", "target": "居民", "value": 30},
        {"source": "工业", "target": "居民", "value": 10},
    ]

    sankey_chart2 = (
        Sankey(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add(
            "能源流向",
            nodes2,
            links2,
            pos_left="10%",
            pos_right="10%",
            pos_top="20%",
            pos_bottom="20%",
            label_opts=opts.LabelOpts(position="right", formatter="{b}", font_size=12),
            itemstyle_opts=opts.ItemStyleOpts(border_color="#000", border_width=1),
            linestyle_opt=opts.LineStyleOpts(curve=0.5, opacity=0.6, color="source"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="能��流向分析 - 示例2"),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                trigger_on="mousemove",
                formatter="{a} &rarr; {b}: {c}"
            ),
        )
    )
    html2 = sankey_chart2.render_embed()
    components.html(html2, height=600)

    st.subheader("桑葚图示例3：网站用户行为流")

    nodes3 = [
        {"name": "访问首页"}, {"name": "浏览商品"}, {"name": "加入购物车"},
        {"name": "提交订单"}, {"name": "支付成功"}, {"name": "离开"}
    ]

    links3 = [
        {"source": "访问首页", "target": "浏览商品", "value": 100},
        {"source": "访问首页", "target": "离开", "value": 20},
        {"source": "浏览商品", "target": "加入购物车", "value": 70},
        {"source": "浏览商品", "target": "离开", "value": 30},
        {"source": "加入购物车", "target": "提交订单", "value": 50},
        {"source": "加入购物车", "target": "离开", "value": 20},
        {"source": "提交订单", "target": "支付成功", "value": 40},
        {"source": "提交订单", "target": "离开", "value": 10},
        {"source": "支付成功", "target": "离开", "value": 40},
    ]

    sankey_chart3 = (
        Sankey(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add(
            "用户行为流",
            nodes3,
            links3,
            pos_left="10%",
            pos_right="10%",
            pos_top="20%",
            pos_bottom="20%",
            label_opts=opts.LabelOpts(position="right", formatter="{b}", font_size=12),
            itemstyle_opts=opts.ItemStyleOpts(border_color="#000", border_width=1),
            linestyle_opt=opts.LineStyleOpts(curve=0.5, opacity=0.6, color="source"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="网站用户行为流分析 - 示例3"),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                trigger_on="mousemove",
                formatter="{a} &rarr; {b}: {c}"
            ),
        )
    )
    html3 = sankey_chart3.render_embed()
    components.html(html3, height=600)

    st.subheader("桑葚图示例4：供应链物流")

    nodes4 = [
        {"name": "供应商A"}, {"name": "供应商B"}, {"name": "工厂1"}, {"name": "工厂2"},
        {"name": "仓库A"}, {"name": "仓库B"}, {"name": "零售商X"}, {"name": "零售商Y"}
    ]

    links4 = [
        {"source": "供应商A", "target": "���厂1", "value": 50},
        {"source": "供应商A", "target": "工厂2", "value": 30},
        {"source": "供应商B", "target": "工厂1", "value": 40},
        {"source": "供应商B", "target": "工厂2", "value": 60},
        {"source": "工厂1", "target": "仓库A", "value": 70},
        {"source": "工厂1", "target": "仓库B", "value": 20},
        {"source": "工厂2", "target": "仓库A", "value": 30},
        {"source": "工厂2", "target": "仓库B", "value": 80},
        {"source": "仓库A", "target": "零售商X", "value": 60},
        {"source": "仓库A", "target": "零售商Y", "value": 40},
        {"source": "仓库B", "target": "零售商X", "value": 50},
        {"source": "仓库B", "target": "零售商Y", "value": 30},
    ]

    sankey_chart4 = (
        Sankey(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add(
            "供应链物流",
            nodes4,
            links4,
            pos_left="10%",
            pos_right="10%",
            pos_top="20%",
            pos_bottom="20%",
            label_opts=opts.LabelOpts(position="right", formatter="{b}", font_size=12),
            itemstyle_opts=opts.ItemStyleOpts(border_color="#000", border_width=1),
            linestyle_opt=opts.LineStyleOpts(curve=0.5, opacity=0.6, color="source"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="供应链物流分析 - 示例4"),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                trigger_on="mousemove",
                formatter="{a} &rarr; {b}: {c}"
            ),
        )
    )
    html4 = sankey_chart4.render_embed()
    components.html(html4, height=600)


if __name__ == "__main__":
    st.set_page_config(
        page_title="桑葚图示例",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    draw_sankey_chart()
