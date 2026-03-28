import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re
import os

st.set_page_config(
    page_title="AI生图能力对比工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "AI生图能力对比工具 - 对比不同AI生图模型的能力表现"
    }
)

st.markdown("""
<style>
    /* 移动端优化 */
    @media (max-width: 768px) {
        /* 主容器 */
        .main .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 0.8rem !important;
            max-width: 100% !important;
        }
        
        /* 标题放大 */
        h1 {
            font-size: 1.8rem !important;
            margin-bottom: 0.5rem !important;
        }
        h2 {
            font-size: 1.5rem !important;
            margin-top: 1.5rem !important;
            margin-bottom: 0.8rem !important;
        }
        h3 {
            font-size: 1.3rem !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* 多选框放大 */
        .stMultiSelect > label {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin-bottom: 0.5rem !important;
        }
        .stMultiSelect {
            margin-bottom: 1rem !important;
        }
        div[data-baseweb="select"] {
            font-size: 1rem !important;
            min-height: 48px !important;
        }
        div[data-baseweb="select"] > div {
            min-height: 48px !important;
            padding: 8px !important;
        }
        
        /* 按钮放大 */
        .stButton button {
            font-size: 1.1rem !important;
            padding: 12px 24px !important;
            min-height: 48px !important;
        }
        
        /* 复选框放大 */
        .stCheckbox {
            font-size: 1.1rem !important;
        }
        .stCheckbox > label {
            font-size: 1.1rem !important;
            padding: 8px 0 !important;
        }
        .stCheckbox > label > div {
            width: 24px !important;
            height: 24px !important;
        }
        
        /* 数据表格放大 */
        .stDataFrame {
            font-size: 1rem !important;
        }
        .stDataFrame th {
            font-size: 0.95rem !important;
            padding: 10px 8px !important;
        }
        .stDataFrame td {
            font-size: 0.95rem !important;
            padding: 10px 8px !important;
        }
        
        /* 图表高度增加 */
        .stPlotlyChart {
            height: 400px !important;
        }
        
        /* 隐藏工具栏 */
        .js-plotly-plot .plotly .modebar {
            display: none !important;
        }
        
        /* 折叠面板 */
        .stExpander {
            margin-bottom: 1rem !important;
        }
        .stExpander header {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            padding: 15px !important;
            min-height: 50px !important;
        }
        .stExpander content {
            padding: 15px !important;
        }
        
        /* 信息提示 */
        .stAlert {
            font-size: 1rem !important;
            padding: 15px !important;
        }
        
        /* Markdown 文字 */
        .stMarkdown {
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }
        .stMarkdown p {
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }
        .stMarkdown li {
            font-size: 1rem !important;
            line-height: 1.8 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* 分隔线 */
        hr {
            margin: 1.5rem 0 !important;
        }
        
        /* 下拉选项 */
        [data-baseweb="popover"] {
            font-size: 1rem !important;
        }
        [data-baseweb="popover"] li {
            padding: 12px 16px !important;
            font-size: 1rem !important;
        }
        
        /* 标签 */
        .stMultiSelect > label p {
            font-size: 1.1rem !important;
        }
        
        /* 选中的标签 */
        .stMultiSelect [data-baseweb="tag"] {
            font-size: 1rem !important;
            padding: 6px 12px !important;
            margin: 4px !important;
        }
        
        /* 滚动条 */
        ::-webkit-scrollbar {
            width: 8px !important;
            height: 8px !important;
        }
        ::-webkit-scrollbar-thumb {
            background: #888 !important;
            border-radius: 4px !important;
        }
    }
    
    /* 桌面端样式 */
    @media (min-width: 769px) {
        .stSidebar {
            width: 280px !important;
        }
    }
    
    /* 通用样式 */
    .stExpander header {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI生图能力对比工具")
st.markdown("<p style='font-size: 0.75rem; color: #888; margin-top: -0.5rem;'>本评测数据集最后更新于2026 年 3 月 21 日，评测结果基于单次生成采样获取，数据结果仅供参考。</p>", unsafe_allow_html=True)
st.markdown("---")

def remove_brackets(text):
    if pd.isna(text):
        return text
    return re.sub(r'[（(].*?[）)]', '', str(text)).strip()

def parse_score(score_str):
    if pd.isna(score_str):
        return None, None
    score_str = str(score_str).strip()
    match = re.match(r'(\d)分[-\s]*(\d+)[sS]?', score_str)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

@st.cache_data(ttl=1)
def load_data():
    file1 = '模型评测20260317第一二三行.csv'
    file2 = '模型评测20260317第四至十一行.csv'
    
    df1 = pd.read_csv(file1, encoding='utf-8-sig')
    df2 = pd.read_csv(file2, encoding='utf-8-sig')
    
    df = pd.concat([df1, df2], ignore_index=True)
    
    known_models = [
        'GPT Image 1.5',
        'Midjourney-v6.0',
        'Nano Banana 2',
        '万相2.6',
        '腾讯混元（HunyuanImage3.0-instruct）',
        '即梦（Seedream5.0 Lite）',
        '可灵（3.0 Omini）',
        '智谱清言（GLM image）',
        '文心一格',
        '秒画（Mira Image v-1.0）',
        '豆包（Seedream4.5）',
        'Vidu-Q2',
        'Liblib（V2-flash）'
    ]
    
    exclude_columns = [
        '测试大类', 
        '测试小类', 
        '测试提示词', 
        '测试提示词 ',
        '评分标准', 
        '评测维度（主）', 
        '评测维度（次）',
        '评测维度（其他）',
        '统一设定建议比例',
        '主记分点 (1-5分)'
    ]
    
    all_columns = df.columns.tolist()
    model_columns = [col for col in all_columns if col not in exclude_columns and not col.startswith('Unnamed')]
    
    final_model_columns = []
    for model in known_models:
        if model in model_columns:
            final_model_columns.append(model)
    
    for col in model_columns:
        if col not in final_model_columns:
            final_model_columns.append(col)
    
    return df, final_model_columns

df, model_columns = load_data()

valid_rows = df[df['测试大类'].notna() & (df['测试大类'] != '')].copy()

valid_rows['测试大类_简化'] = valid_rows['测试大类'].apply(remove_brackets)
valid_rows['评测维度_简化'] = valid_rows['评测维度（主）'].apply(remove_brackets)

test_categories = valid_rows['测试大类_简化'].unique().tolist()

model_colors = [
    '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
    '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52',
    '#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD',
    '#8C564B', '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF'
]

model_color_map = {model: model_colors[i % len(model_colors)] for i, model in enumerate(model_columns)}

st.subheader("选择测试类别")
selected_category = st.multiselect(
    "测试类别",
    test_categories,
    default=test_categories,
    label_visibility="collapsed"
)

st.subheader("选择模型")
selected_models = st.multiselect(
    "模型列表",
    model_columns,
    default=model_columns,
    label_visibility="collapsed"
)

filtered_df = valid_rows[valid_rows['测试大类_简化'].isin(selected_category)]

st.markdown("---")
st.header("模型总分对比")

scores_data = []
for model in selected_models:
    scores = []
    for idx, row in filtered_df.iterrows():
        score, _ = parse_score(row.get(model))
        if score is not None:
            scores.append(score)
    if scores:
        avg_score = sum(scores) / len(scores)
        scores_data.append({
            '模型': model,
            '平均分': round(avg_score, 2),
            '测试项数': len(scores)
        })

if scores_data:
    scores_df = pd.DataFrame(scores_data)
    scores_df = scores_df.sort_values('平均分', ascending=True)
    
    bar_colors = [model_color_map[m] for m in scores_df['模型']]
    
    fig_bar = go.Figure(go.Bar(
        x=scores_df['平均分'],
        y=scores_df['模型'],
        orientation='h',
        text=scores_df['平均分'],
        textposition='outside',
        marker_color=bar_colors,
        textfont=dict(size=14)
    ))
    fig_bar.update_layout(
        height=max(500, len(scores_df) * 50),
        xaxis_title="平均分数",
        yaxis_title="",
        xaxis=dict(range=[0, 5.5], tickfont=dict(size=13)),
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(tickfont=dict(size=13))
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
if '文生图' in selected_category:
    st.header("文成图综合分数对比")
    
    wensheng_df = filtered_df[filtered_df['测试大类_简化'] == '文生图']
    scores_data = []
    for model in selected_models:
        scores = []
        for idx, row in wensheng_df.iterrows():
            score, _ = parse_score(row.get(model))
            if score is not None:
                scores.append(score)
        if scores:
            avg_score = sum(scores) / len(scores)
            scores_data.append({
                '模型': model,
                '平均分': round(avg_score, 2),
                '测试项数': len(scores)
            })
    
    if scores_data:
        scores_df = pd.DataFrame(scores_data)
        scores_df = scores_df.sort_values('平均分', ascending=True)
        
        bar_colors = [model_color_map[m] for m in scores_df['模型']]
        
        fig_bar = go.Figure(go.Bar(
            x=scores_df['平均分'],
            y=scores_df['模型'],
            orientation='h',
            text=scores_df['平均分'],
            textposition='outside',
            marker_color=bar_colors,
            textfont=dict(size=14)
        ))
        fig_bar.update_layout(
            height=max(500, len(scores_df) * 50),
            xaxis_title="平均分数",
            yaxis_title="",
            xaxis=dict(range=[0, 5.5], tickfont=dict(size=13)),
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(tickfont=dict(size=13))
        )
        st.plotly_chart(fig_bar, use_container_width=True)

if '图生图' in selected_category:
    st.markdown("---")
    st.header("图生图综合分数对比")
    
    tusheng_df = filtered_df[filtered_df['测试大类_简化'] == '图生图']
    scores_data = []
    for model in selected_models:
        scores = []
        for idx, row in tusheng_df.iterrows():
            score, _ = parse_score(row.get(model))
            if score is not None:
                scores.append(score)
        if scores:
            avg_score = sum(scores) / len(scores)
            scores_data.append({
                '模型': model,
                '平均分': round(avg_score, 2),
                '测试项数': len(scores)
            })
    
    if scores_data:
        scores_df = pd.DataFrame(scores_data)
        scores_df = scores_df.sort_values('平均分', ascending=True)
        
        bar_colors = [model_color_map[m] for m in scores_df['模型']]
        
        fig_bar = go.Figure(go.Bar(
            x=scores_df['平均分'],
            y=scores_df['模型'],
            orientation='h',
            text=scores_df['平均分'],
            textposition='outside',
            marker_color=bar_colors,
            textfont=dict(size=14)
        ))
        fig_bar.update_layout(
            height=max(500, len(scores_df) * 50),
            xaxis_title="平均分数",
            yaxis_title="",
            xaxis=dict(range=[0, 5.5], tickfont=dict(size=13)),
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(tickfont=dict(size=13))
        )
        st.plotly_chart(fig_bar, use_container_width=True)

if '文生图' in selected_category:
    st.markdown("---")
    st.header("文生图 - 按评测维度对比")
    
    wensheng_df = filtered_df[filtered_df['测试大类_简化'] == '文生图']
    wensheng_dims = wensheng_df['评测维度_简化'].dropna().unique().tolist()
    
    dimension_scores = []
    for dim in wensheng_dims:
        dim_df = wensheng_df[wensheng_df['评测维度_简化'] == dim]
        for model in selected_models:
            scores = []
            for idx, row in dim_df.iterrows():
                score, _ = parse_score(row.get(model))
                if score is not None:
                    scores.append(score)
            if scores:
                dimension_scores.append({
                    '评测维度': dim,
                    '模型': model,
                    '平均分': round(sum(scores) / len(scores), 2)
                })
    
    if dimension_scores:
        dim_df_plot = pd.DataFrame(dimension_scores)
        
        fig_dim = go.Figure()
        models_in_data = dim_df_plot['模型'].unique()
        
        for model in models_in_data:
            model_data = dim_df_plot[dim_df_plot['模型'] == model]
            fig_dim.add_trace(go.Bar(
                name=model,
                x=model_data['评测维度'],
                y=model_data['平均分'],
                marker_color=model_color_map[model]
            ))
        
        fig_dim.update_layout(
            barmode='group',
            height=450,
            yaxis_title="平均分数",
            xaxis_title="",
            yaxis=dict(range=[0, 5.5], tickfont=dict(size=13)),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(tickfont=dict(size=12))
        )
        st.plotly_chart(fig_dim, use_container_width=True)

if '图生图' in selected_category:
    st.markdown("---")
    st.header("图生图 - 按评测维度对比")
    
    tusheng_df = filtered_df[filtered_df['测试大类_简化'] == '图生图']
    tusheng_dims = tusheng_df['评测维度_简化'].dropna().unique().tolist()
    
    dimension_scores = []
    for dim in tusheng_dims:
        dim_df = tusheng_df[tusheng_df['评测维度_简化'] == dim]
        for model in selected_models:
            scores = []
            for idx, row in dim_df.iterrows():
                score, _ = parse_score(row.get(model))
                if score is not None:
                    scores.append(score)
            if scores:
                dimension_scores.append({
                    '评测维度': dim,
                    '模型': model,
                    '平均分': round(sum(scores) / len(scores), 2)
                })
    
    if dimension_scores:
        dim_df_plot = pd.DataFrame(dimension_scores)
        
        fig_dim = go.Figure()
        models_in_data = dim_df_plot['模型'].unique()
        
        for model in models_in_data:
            model_data = dim_df_plot[dim_df_plot['模型'] == model]
            fig_dim.add_trace(go.Bar(
                name=model,
                x=model_data['评测维度'],
                y=model_data['平均分'],
                marker_color=model_color_map[model]
            ))
        
        fig_dim.update_layout(
            barmode='group',
            height=450,
            yaxis_title="平均分数",
            xaxis_title="",
            yaxis=dict(range=[0, 5.5], tickfont=dict(size=13)),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(tickfont=dict(size=12))
        )
        st.plotly_chart(fig_dim, use_container_width=True)

st.markdown("---")
st.header("雷达图对比")

radar_models = st.multiselect(
    "选择要对比的模型",
    selected_models,
    default=selected_models,
    key="radar_select"
)

if len(radar_models) >= 1:
    all_dimensions = filtered_df['评测维度_简化'].dropna().unique().tolist()
    
    # 创建维度到类别的映射
    dim_category_map = {}
    for dim in all_dimensions:
        dim_rows = filtered_df[filtered_df['评测维度_简化'] == dim]
        if not dim_rows.empty:
            category = dim_rows['测试大类_简化'].iloc[0]
            dim_category_map[dim] = category
    
    radar_data = {}
    for model in radar_models:
        dim_scores = {}
        for dim in all_dimensions:
            dim_df = filtered_df[filtered_df['评测维度_简化'] == dim]
            scores = []
            for idx, row in dim_df.iterrows():
                score, _ = parse_score(row.get(model))
                if score is not None:
                    scores.append(score)
            if scores:
                dim_scores[dim] = sum(scores) / len(scores)
        if dim_scores:
            radar_data[model] = dim_scores
    
    if radar_data:
        all_dims_with_data = set()
        for model_scores in radar_data.values():
            all_dims_with_data = all_dims_with_data.union(model_scores.keys())
        all_dims_with_data = list(all_dims_with_data)
        
        # 为维度添加类别标签
        labeled_dims = [f"{dim} ({dim_category_map.get(dim, '未知')})" for dim in all_dims_with_data]
        
        if all_dims_with_data:
            fig_radar = go.Figure()
            
            for model, scores in radar_data.items():
                values = [scores.get(dim, 0) for dim in all_dims_with_data]
                values.append(values[0])
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=labeled_dims + [labeled_dims[0]],
                    fill='toself',
                    name=model,
                    line_color=model_color_map[model]
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5],
                        tickfont=dict(size=12)
                    ),
                    angularaxis=dict(tickfont=dict(size=12))
                ),
                showlegend=True,
                height=600,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11)),
                margin=dict(l=20, r=20, t=20, b=100)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

if '文生图' in selected_category:
    st.markdown("---")
    st.header("文生图各项能力对比")
    
    radar_models_ws = st.multiselect(
        "选择要对比的模型（文生图）",
        selected_models,
        default=selected_models,
        key="radar_select_wensheng"
    )
    
    if len(radar_models_ws) >= 1:
        wensheng_df = filtered_df[filtered_df['测试大类_简化'] == '文生图']
        ws_dimensions = wensheng_df['评测维度_简化'].dropna().unique().tolist()
        
        radar_data = {}
        for model in radar_models_ws:
            dim_scores = {}
            for dim in ws_dimensions:
                dim_df = wensheng_df[wensheng_df['评测维度_简化'] == dim]
                scores = []
                for idx, row in dim_df.iterrows():
                    score, _ = parse_score(row.get(model))
                    if score is not None:
                        scores.append(score)
                if scores:
                    dim_scores[dim] = sum(scores) / len(scores)
            if dim_scores:
                radar_data[model] = dim_scores
        
        if radar_data:
            all_dims_with_data = set()
            for model_scores in radar_data.values():
                all_dims_with_data = all_dims_with_data.union(model_scores.keys())
            all_dims_with_data = list(all_dims_with_data)
            
            if all_dims_with_data:
                fig_radar = go.Figure()
                
                for model, scores in radar_data.items():
                    values = [scores.get(dim, 0) for dim in all_dims_with_data]
                    values.append(values[0])
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=all_dims_with_data + [all_dims_with_data[0]],
                        fill='toself',
                        name=model,
                        line_color=model_color_map[model]
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 5],
                            tickfont=dict(size=12)
                        ),
                        angularaxis=dict(tickfont=dict(size=12))
                    ),
                    showlegend=True,
                    height=600,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11)),
                    margin=dict(l=20, r=20, t=20, b=100)
                )
                st.plotly_chart(fig_radar, use_container_width=True)

if '图生图' in selected_category:
    st.markdown("---")
    st.header("图生图各项能力对比")
    
    radar_models_ts = st.multiselect(
        "选择要对比的模型（图生图）",
        selected_models,
        default=selected_models,
        key="radar_select_tusheng"
    )
    
    if len(radar_models_ts) >= 1:
        tusheng_df = filtered_df[filtered_df['测试大类_简化'] == '图生图']
        ts_dimensions = tusheng_df['评测维度_简化'].dropna().unique().tolist()
        
        radar_data = {}
        for model in radar_models_ts:
            dim_scores = {}
            for dim in ts_dimensions:
                dim_df = tusheng_df[tusheng_df['评测维度_简化'] == dim]
                scores = []
                for idx, row in dim_df.iterrows():
                    score, _ = parse_score(row.get(model))
                    if score is not None:
                        scores.append(score)
                if scores:
                    dim_scores[dim] = sum(scores) / len(scores)
            if dim_scores:
                radar_data[model] = dim_scores
        
        if radar_data:
            all_dims_with_data = set()
            for model_scores in radar_data.values():
                all_dims_with_data = all_dims_with_data.union(model_scores.keys())
            all_dims_with_data = list(all_dims_with_data)
            
            if all_dims_with_data:
                fig_radar = go.Figure()
                
                for model, scores in radar_data.items():
                    values = [scores.get(dim, 0) for dim in all_dims_with_data]
                    values.append(values[0])
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=all_dims_with_data + [all_dims_with_data[0]],
                        fill='toself',
                        name=model,
                        line_color=model_color_map[model]
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 5],
                            tickfont=dict(size=12)
                        ),
                        angularaxis=dict(tickfont=dict(size=12))
                    ),
                    showlegend=True,
                    height=600,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11)),
                    margin=dict(l=20, r=20, t=20, b=100)
                )
                st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")
st.header("详细数据表")

st.subheader("生成时间对比")

time_data = []
for model in selected_models:
    times = []
    for idx, row in filtered_df.iterrows():
        _, time_s = parse_score(row.get(model))
        if time_s is not None:
            times.append(time_s)
    if times:
        avg_time = sum(times) / len(times)
        time_data.append({
            '模型': model,
            '平均生成时间(秒)': round(avg_time, 1),
            '测试次数': len(times)
        })

if time_data:
    time_df = pd.DataFrame(time_data)
    time_df = time_df.sort_values('平均生成时间(秒)', ascending=True)
    
    bar_colors = [model_color_map[m] for m in time_df['模型']]
    
    fig_time = go.Figure(go.Bar(
        x=time_df['平均生成时间(秒)'],
        y=time_df['模型'],
        orientation='h',
        text=time_df['平均生成时间(秒)'],
        textposition='outside',
        marker_color=bar_colors,
        textfont=dict(size=14)
    ))
    fig_time.update_layout(
        height=max(500, len(time_df) * 50),
        xaxis_title="平均生成时间 (秒)",
        yaxis_title="",
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(tickfont=dict(size=13)),
        xaxis=dict(tickfont=dict(size=13))
    )
    st.plotly_chart(fig_time, use_container_width=True)
    
    st.dataframe(time_df, use_container_width=True, height=400, hide_index=True)
else:
    st.info("暂无生成时间数据")

st.markdown("---")

if '文生图' in selected_category:
    st.subheader("文生图数据")
    table_data = []
    wensheng_df = filtered_df[filtered_df['测试大类_简化'] == '文生图']
    for idx, row in wensheng_df.iterrows():
        dimension = row.get('评测维度_简化', '')
        if pd.isna(dimension):
            continue
        row_data = {'评测维度': dimension}
        for model in selected_models:
            score, _ = parse_score(row.get(model))
            if score is not None:
                row_data[model] = score
            else:
                row_data[model] = "-"
        table_data.append(row_data)
    if table_data:
        table_df = pd.DataFrame(table_data)
        st.dataframe(table_df, use_container_width=True, height=400, hide_index=True)
    else:
        st.info("暂无文生图数据")

if '图生图' in selected_category:
    st.subheader("图生图数据")
    table_data = []
    tusheng_df = filtered_df[filtered_df['测试大类_简化'] == '图生图']
    for idx, row in tusheng_df.iterrows():
        dimension = row.get('评测维度_简化', '')
        if pd.isna(dimension):
            continue
        row_data = {'评测维度': dimension}
        for model in selected_models:
            score, _ = parse_score(row.get(model))
            if score is not None:
                row_data[model] = score
            else:
                row_data[model] = "-"
        table_data.append(row_data)
    if table_data:
        table_df = pd.DataFrame(table_data)
        st.dataframe(table_df, use_container_width=True, height=400, hide_index=True)
    else:
        st.info("暂无图生图数据")

st.markdown("---")
st.header("生成图片展示")

image_base_dir = "images"

def get_image_path(category, dimension, model):
    dimension_dir = os.path.join(image_base_dir, category, dimension)
    if os.path.exists(dimension_dir):
        model_dir = os.path.join(dimension_dir, model)
        if os.path.exists(model_dir):
            for file in os.listdir(model_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    return os.path.join(model_dir, file)
    return None

def display_images_for_category(category_name, category_df, selected_models):
    st.subheader(f"{category_name}生成图片")
    
    dimensions = category_df['评测维度_简化'].dropna().unique().tolist()
    
    for dimension in dimensions:
        st.markdown(f"#### {dimension}")
        
        cols_per_row = 4
        models_to_show = selected_models
        
        for i in range(0, len(models_to_show), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(models_to_show):
                    model = models_to_show[i + j]
                    image_path = get_image_path(category_name, dimension, model)
                    
                    with col:
                        st.markdown(f"**{model}**")
                        if image_path and os.path.exists(image_path):
                            st.image(image_path, use_container_width=True)
                        else:
                            st.info("暂无图片")
        
        st.markdown("---")

if '文生图' in selected_category:
    wensheng_df = filtered_df[filtered_df['测试大类_简化'] == '文生图']
    if not wensheng_df.empty:
        display_images_for_category('文生图', wensheng_df, selected_models)

if '图生图' in selected_category:
    tusheng_df = filtered_df[filtered_df['测试大类_简化'] == '图生图']
    if not tusheng_df.empty:
        display_images_for_category('图生图', tusheng_df, selected_models)

st.markdown("---")
st.markdown("""
### 评分标准说明
- **5分 (优秀)**：完美遵循所有指令约束；画面无任何结构性扭曲或逻辑硬伤；质感与指定风格完全吻合。
- **4分 (良好)**：遵循绝大多数指令约束；核心主体无结构错误，仅在非视觉中心区域存在轻微瑕疵。
- **3分 (及格)**：画面基本呈现了提示词的大意；但存在1-2处明显的指令遗漏或局部结构畸变。
- **2分 (较差)**：严重偏离提示词核心约束；或画面出现大面积的解剖学崩坏、透视错误。
- **1分 (极差)**：未能响应提示词的核心概念；或生成内容完全崩坏。
""")
