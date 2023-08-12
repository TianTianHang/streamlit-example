import json
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Wos",
    page_icon="WOS Abstract ",
    layout='wide'
)
st.title('Wos Dataset Abstract')
WIDTH = 1000  # st.slider(label='plot width', min_value=500, max_value=1500, value=1000)


@st.cache_data()
def load_wos_data():
    with open('data/wos/new_novel_counts_filter.json', 'r') as f:
        wos_data = json.load(f)

    return wos_data
@st.cache_data()
def load_all_words():
    with open('data/wos/all_words.json', 'r') as f:
        all_words = json.load(f)

    return all_words

@st.cache_data()
def create_heatmap_plot(data, width):
    # 提取单词和数量数据
    new_words = data["new"]
    novel_words = data["novel"]

    # 整理数据为热力图所需格式
    word_list = get_all_words(data) * 2
    types = ["new"] * len(word_list) + ["novel"] * len(word_list)
    counts = [new_words.get(w, 0) for w in word_list] + [novel_words.get(w, 0) for w in word_list]

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
def create_scatter_plot(title, width, words, *datas):
    # 将数据整理为适用于 Plotly Express 的DataFrame
    data_list = []

    for data, word in zip(datas, words):
        years = [entry["year"] for entry in data]
        new_word_counts = [sum(entry["new"].values()) for entry in data]
        novel_word_counts = [sum(entry["novel"].values()) for entry in data]

        for year, new_count, novel_count in zip(years, new_word_counts, novel_word_counts):
            data_list.append({
                "Year": year,
                "WordType": "new",
                "WordCount": new_count,
                "Word": word
            })
            data_list.append({
                "Year": year,
                "WordType": "novel",
                "WordCount": novel_count,
                "Word": word
            })

    df = pd.DataFrame(data_list)

    # 使用 Plotly Express 进行绘图
    fig = px.line(df, x='Year', y='WordCount', color='WordType', title=title,
                  markers=True, symbol='Word')
    # 设置不同的标记样式
    for word in df['Word'].unique():
        fig.update_traces(marker=dict(symbol='diamond', size=10), selector=dict(name=word))

    # fig = go.Figure()
    # for data, word in zip(datas, words):
    #     # 整理数据
    #     years = [entry["year"] for entry in data]
    #     new_word_counts = [sum(entry["new"].values()) for entry in data]
    #     novel_word_counts = [sum(entry["novel"].values()) for entry in data]
    #     gap = sum(new_word_counts + novel_word_counts) / len(new_word_counts + novel_word_counts) / 4
    #     # 添加"new"类型的单词数线
    #     trace_new = go.Line(x=years, y=new_word_counts, mode='lines+markers',
    #                         name=f"'new'-{word}", legendgroup=f'new-{word}',
    #                         marker=dict(size=8, symbol='diamond'),)
    #     fig.add_trace(trace_new)
    #
    #     # 添加"novel"类型的单词数线
    #     trace_novel = go.Line(x=years, y=novel_word_counts, mode='lines+markers',
    #                           name=f"'novel'-{word}", legendgroup=f'novel--{word}',
    #                           marker=dict(size=8, symbol='circle'))
    #     fig.add_trace(trace_novel)

    # fig.add_trace(go.Scatter(
    #     x=years + years[::-1],
    #     y=new_word_counts + [x - gap for x in new_word_counts][::-1],
    #     fill='toself',
    #     fillcolor='rgba(0,100,80,0.2)',
    #     line=dict(color='rgba(255,255,255,0)'),
    #     showlegend=False,
    #     hoverinfo='none',
    #     legendgroup=f'new-{word}'
    # ))
    #
    # fig.add_trace(go.Scatter(
    #     x=years + years[::-1],
    #     y=[x + gap for x in new_word_counts] + new_word_counts[::-1],
    #     fill='toself',
    #     fillcolor='rgba(0,100,80,0.2)',
    #     line=dict(color='rgba(255,255,255,0)'),
    #     showlegend=False,
    #     hoverinfo='none',
    #     legendgroup=f'new-{word}'
    # ))
    # fig.add_trace(go.Scatter(
    #     x=years + years[::-1],
    #     y=novel_word_counts + [x - gap for x in novel_word_counts][::-1],
    #     fill='toself',
    #     fillcolor='rgba(0,100,80,0.2)',
    #     line=dict(color='rgba(255,255,255,0)'),
    #     showlegend=False,
    #     hoverinfo='none',
    #     legendgroup=f'novel--{word}'
    # ))
    #
    # fig.add_trace(go.Scatter(
    #     x=years + years[::-1],
    #     y=[x + gap for x in novel_word_counts] + novel_word_counts[::-1],
    #     fill='toself',
    #     fillcolor='rgba(0,100,80,0.2)',
    #     line=dict(color='rgba(255,255,255,0)'),
    #     showlegend=False,
    #     hoverinfo='none',
    #     legendgroup=f'novel--{word}'
    # ))

    # 设置图表布局
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=" Word Count",
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
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        specs=[[{"type": "bar"}],
               [{"type": "bar"}],
               [{"type": "table"}],
               ],
        subplot_titles=('new', 'novel')
    )
    new_header = [word for word, count in top_new_counts]
    novel_header = [word for word, count in top_novel_counts]
    merged_header = new_header + [item for item in novel_header if item not in new_header]

    # 添加"new"类型的计数子图
    new_trace = go.Bar(
        x=merged_header,
        y=[new_word_counts.get(word, 0) for word in merged_header],
        name="new",
        marker=dict(color=['red' if word in new_header else 'green' for word in merged_header])
    )
    fig.add_trace(new_trace, row=1, col=1)

    # 添加"novel"类型的计数子图
    novel_trace = go.Bar(
        x=merged_header,
        y=[novel_word_counts.get(word, 0) for word in merged_header],
        name="novel",
        marker=dict(color=['blue' if word in novel_header else 'green' for word in merged_header])
    )
    fig.add_trace(novel_trace, row=2, col=1)
    cells = [[new_word_counts.get(word, 0), novel_word_counts.get(word, 0)] for word in merged_header]
    fig.add_trace(go.Table(header=dict(values=[word for word in merged_header]),
                           cells=dict(values=cells)), row=3, col=1)

    fig.update_layout(title_text=f"Top{top} Word Counts Comparison for {data['year']}",
                      showlegend=True,
                      width=width,
                      height=1000
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


@st.cache_data
def get_word_filter_data(word):
    word_filter_data = []
    for data in load_wos_data():
        data['new'] = {word: data['new'].get(word, 0)}
        data['novel'] = {word: data['novel'].get(word, 0)}
        word_filter_data.append(data)
    return word_filter_data


wos_data = load_wos_data()
st.plotly_chart(create_scatter_plot(" Word Counts for 'new' and 'novel' Over the Years",
                                    WIDTH, 'all_words', wos_data))

all_words = load_all_words()
words = st.multiselect(label=f'select a word', options=all_words,
                       key='word_select')
words = words if words else ['method', 'approach']
word_filter_data = [get_word_filter_data(word) for word in words]
word_fig = create_scatter_plot(f" '{','.join(words)}' Counts for 'new' and 'novel' Over the Years", WIDTH,
                               words, *word_filter_data)
st.plotly_chart(word_fig)



current_data = st.sidebar.select_slider(label="select a time", options=wos_data, key='wos_select',
                                        format_func=lambda e: e['year'])

top = st.number_input(label='input number of top', value=5)
st.plotly_chart(create_bar_plot(current_data, top, WIDTH))

pie_word = st.selectbox(label=f'select a word for pie', options=get_all_words(current_data))
st.plotly_chart(create_pie_plot(current_data, pie_word, WIDTH))
