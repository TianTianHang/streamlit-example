import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Wos",
    page_icon="WOS Abstract ",
    layout='wide'
)
st.title('Wos Dataset Abstract')
WIDTH = 1400  # st.slider(label='plot width', min_value=500, max_value=1500, value=1000)


@st.cache_data()
def load_wos_data():
    data = pd.read_json('data/wos/new_novel_counts.json', orient='records')
    data = data.applymap(lambda e: json.loads(e))
    return data


@st.cache_data()
def create_heatmap_plot(data, width):
    # 提取单词和数量数据
    new_words = data["new"]
    novel_words = data["novel"]

    # 整理数据为热力图所需格式
    word_list = get_all_words(data)*2
    types = ["new"] * len(all_words) + ["novel"] * len(all_words)
    counts = [new_words.get(w, 0) for w in all_words] + [novel_words.get(w, 0) for w in all_words]

    heatmap_data = {
        "Word": word_list,
        "Type": types,
        "Count": counts
    }
    # 定义更明显的颜色尺度
    color_scale = [[0.0, 'rgb(255, 255, 255)'], [0.5, 'rgb(255, 200, 200)'], [1.0, 'rgb(255, 0, 0)']]
    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data["Count"],
        x=heatmap_data["Type"],
        y=heatmap_data["Word"],
        colorscale="Viridis",

    ))
    # 设置图表布局
    fig.update_layout(
        title=f"Word Counts for 'new' and 'novel' Pairings in {current_data['year']}",
        xaxis_title="Type",
        yaxis_title="Word",
        yaxis_autorange="reversed",
        width=width,
        height=1000
    )
    return fig


@st.cache_data
def create_scatter_plot(width):
    data = load_wos_data()[0]
    # 整理数据
    years = [entry["year"] for entry in data]
    new_word_counts = [sum(entry["new"].values()) for entry in data]
    novel_word_counts = [sum(entry["novel"].values()) for entry in data]
    # 创建图表
    fig = go.Figure()

    # 添加"new"类型的平均单词数线
    trace_new = go.Scatter(x=years, y=new_word_counts, mode='lines+markers',
                           name="'new' Average Words per Article")
    fig.add_trace(trace_new)

    # 添加"novel"类型的平均单词数线
    trace_novel = go.Scatter(x=years, y=novel_word_counts, mode='lines+markers',
                             name="'novel' Average Words per Article")
    fig.add_trace(trace_novel)

    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=new_word_counts + [x - 1500 for x in new_word_counts][::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='none'
    ))

    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=[x + 1500 for x in new_word_counts] + new_word_counts[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='none'
    ))
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=novel_word_counts + [x - 1500 for x in novel_word_counts][::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='none'
    ))

    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=[x + 1500 for x in novel_word_counts] + novel_word_counts[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='none'
    ))
    # 设置图表布局
    fig.update_layout(
        title="Average Word Counts for 'new' and 'novel' Pairings per Article Over the Years",
        xaxis_title="Year",
        yaxis_title="Average Word Count per Article",
        showlegend=True,  # 显示图例
        width=width
    )
    return fig


@st.cache_data
def create_bar_plot(data, top, width):
    new_word_counts = data["new"]
    novel_word_counts = data["novel"]
    # 取出前十的词汇和计数
    top_new_counts = sorted(new_word_counts.items(), key=lambda x: x[1], reverse=True)[:top]
    top_novel_counts = sorted(novel_word_counts.items(), key=lambda x: x[1], reverse=True)[:top]
    fig = go.Figure()
    # 添加"new"类型的计数子图
    fig.add_trace(go.Bar(x=[word for word, count in top_new_counts],
                         y=[count for word, count in top_new_counts], name="new"))

    # 添加"novel"类型的计数子图
    fig.add_trace(go.Bar(x=[word for word, count in top_novel_counts],
                         y=[count for word, count in top_novel_counts], name="novel"))

    fig.update_layout(title_text=f"Top{top} Word Counts Comparison for {data['year']}",
                      showlegend=True,
                      width=width
                      )
    return fig


@st.cache_data
def get_all_words(data):
    # 获取所有单词列表
    all_words = set()

    all_words.update(data["new"].keys())
    all_words.update(data["novel"].keys())

    return sorted(list(all_words),
                  key=lambda w: max(data["new"].get(w, 0), data["novel"].get(w, 0)), reverse=True)


@st.cache_data
def create_pie_plot(data, selected_word, width):
    new_count = data["new"].get(selected_word, 0)
    novel_count = data["novel"].get(selected_word, 0)
    # 创建饼图
    labels = ["'new' Count", "'novel' Count"]
    values = [new_count, novel_count]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # 设置图表布局
    fig.update_layout(
        title=f"'new' vs. 'novel' Count Ratio for '{selected_word}' in {data['year']}",
        showlegend=True,
        width=width
    )
    return fig


st.plotly_chart(create_scatter_plot(WIDTH))
wos_data = load_wos_data()
current_data = st.select_slider(label="select a time", options=wos_data, key='wos_select',
                                format_func=lambda e: e['year'])
col1, col2 = st.columns(2)
with col1:
    top = st.number_input(label='input number of top', value=10)
    st.plotly_chart(create_bar_plot(current_data, top, WIDTH / 2))
with col2:
    all_words = get_all_words(current_data)
    word = st.selectbox(label='input a word', options=all_words)
    st.plotly_chart(create_pie_plot(current_data, word, WIDTH / 2))
st.plotly_chart(create_heatmap_plot(current_data, WIDTH))
