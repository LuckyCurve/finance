# 方法二：使用 pyecharts 生成 HTML 后嵌入
import streamlit as st
import streamlit.components.v1 as components
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie
from pyecharts.globals import ThemeType


def method2_pyecharts_html() -> None:
    st.title("方法二：使用 pyecharts 生成 HTML")

    # 创建饼图
    pie_chart = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add(
            "水果销量",
            [
                ["苹果", 335],
                ["香蕉", 310],
                ["橙子", 234],
                ["葡萄", 135],
                ["西瓜", 1548],
            ],
            radius=["40%", "75%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="水果销量统计"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="left"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )

    # 渲染为 HTML
    html = pie_chart.render_embed()
    components.html(html, height=500)

    # 创建柱状图
    st.subheader("柱状图示例")

    bar_chart = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add_xaxis(["1月", "2月", "3月", "4月", "5月", "6月"])
        .add_yaxis("销售额", [5, 20, 36, 10, 10, 20])
        .set_global_opts(title_opts=opts.TitleOpts(title="月度销售额"))
    )

    html_bar = bar_chart.render_embed()
    components.html(html_bar, height=500)

    # 创建折线图
    st.subheader("折线图示例")

    line_chart = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add_xaxis(["1月", "2月", "3月", "4月", "5月", "6月"])
        .add_yaxis("销售额", [5, 20, 36, 10, 10, 20])
        .add_yaxis("利润", [3, 15, 25, 8, 8, 15])
        .set_global_opts(title_opts=opts.TitleOpts(title="销售额与利润趋势"))
    )

    html_line = line_chart.render_embed()
    components.html(html_line, height=500)


if __name__ == "__main__":
    method2_pyecharts_html()
