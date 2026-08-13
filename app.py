import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime, timedelta
import plotly.express as px

DATA_FILE = "fitness_data.csv"

# 设置页面基础配置
st.set_page_config(page_title="我的健身打卡 - 100%无限重复动画版", page_icon="🎮", layout="wide")
st.title("🎮 健身英雄榜 & 综合仪表盘")

# 🌟 带动态时间戳的黄金 LEVEL UP 特效（添加时间戳强制每次打卡都百分百重新重绘渲染）
def render_energy_glow():
    timestamp = time.time()  # 获得唯一时间戳
    glow_html = f"""
    <style>
        @keyframes floatUp_{int(timestamp)} {{
            0% {{
                opacity: 0;
                transform: translate(-50%, -30%) scale(0.5);
            }}
            20% {{
                opacity: 1;
                transform: translate(-50%, -50%) scale(1.2);
            }}
            70% {{
                opacity: 1;
                transform: translate(-50%, -50%) scale(1.0);
            }}
            100% {{
                opacity: 0;
                transform: translate(-50%, -70%) scale(0.8);
            }}
        }}
        .energy-overlay-{int(timestamp)} {{
            position: fixed;
            top: 45%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 999999;
            pointer-events: none;
            animation: floatUp_{int(timestamp)} 2.2s ease-out forwards;
            text-align: center;
        }}
        .energy-badge {{
            font-size: 80px;
            filter: drop-shadow(0 0 25px #ffd700);
        }}
        .energy-text {{
            font-size: 32px;
            font-weight: 900;
            color: #FFD700;
            text-shadow: 0 0 10px #ffaa00, 0 0 20px #ff4500;
            font-family: system-ui, -apple-system, sans-serif;
            letter-spacing: 2px;
        }}
    </style>
    <div class="energy-overlay-{int(timestamp)}">
        <div class="energy-badge">🔥 🏋️‍♂️ ⚡</div>
        <div class="energy-text">LEVEL UP! 经验值 +100</div>
    </div>
    """
    st.markdown(glow_html, unsafe_allow_html=True)

# 1. 保存/更新数据函数
def save_data(date_val, workout, duration, notes):
    new_data = pd.DataFrame([[date_val, workout, duration, notes]], 
                            columns=["日期", "运动类型", "时长(分钟)", "备注"])
    if not os.path.exists(DATA_FILE):
        new_data.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    else:
        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')

# 2. 连续打卡计算逻辑
def calculate_streak(df):
    if df.empty:
        return 0
    unique_dates = pd.to_datetime(df['日期']).dt.date.unique()
    sorted_dates = sorted(unique_dates, reverse=True)
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    if sorted_dates[0] < yesterday:
        return 0
    
    streak = 0
    check_date = sorted_dates[0]
    for d in sorted_dates:
        if d == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak

# 3. 侧边栏打卡区域
with st.sidebar:
    st.header("📝 今日训练记录")
    with st.form("workout_form"):
        workout_date = st.date_input("日期", value=date.today())
        workout_type = st.selectbox("运动类型", ["跑步 🏃‍♂️", "力量训练 🏋️‍♀️", "瑜伽 🧘‍♀️", "游泳 🏊‍♂️", "骑行 🚴‍♂️"])
        duration = st.number_input("时长 (分钟)", min_value=5, value=30, step=5)
        notes = st.text_input("心情/备注")
        submit_button = st.form_submit_button("打卡升级 🚀", use_container_width=True)

    if submit_button:
        save_data(workout_date, workout_type, duration, notes)
        
        # ⚡ 每次提交打卡都强制生成带唯一时间戳的 HTML 动画
        render_energy_glow()
        st.toast(f"🔥 打卡成功！获得 {duration * 10} 点经验值！", icon="🏋️‍♂️")

# 4. 主界面展示
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['日期'] = pd.to_datetime(df['日期']).dt.date
    
    # 顶栏 KPI 数据卡片
    total_minutes = int(df["时长(分钟)"].sum())
    total_count = len(df)
    current_streak = calculate_streak(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="🔥 当前连续打卡", value=f"{current_streak} 天")
    col2.metric(label="⚡ 总获得经验值 (XP)", value=f"{total_minutes * 10} XP")
    col3.metric(label="🏅 打卡总次数", value=f"{total_count} 次")

    st.markdown("---")

    # 🎯 目标进度条
    st.subheader("🎯 本周目标")
    today_dt = date.today()
    start_of_week = today_dt - timedelta(days=today_dt.weekday())
    this_week_df = df[df['日期'] >= start_of_week]
    weekly_minutes = int(this_week_df["时长(分钟)"].sum())
    
    weekly_target = 150
    progress = min(weekly_minutes / weekly_target, 1.0)
    st.progress(progress)
    st.caption(f"本周已完成 **{weekly_minutes} / {weekly_target}** 分钟 ({int(progress * 100)}%)")

    # 🏆 勋章陈列柜
    st.subheader("🏆 成就勋章陈列柜")
    all_types = df["运动类型"].unique()
    max_duration = df["时长(分钟)"].max()
    
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    
    with b_col1:
        if total_count >= 1:
            st.success("🌱 **初出茅庐**\n\n完成首次打卡！")
        else:
            st.info("🔒 **初出茅庐**\n\n(完成 1 次打卡)")

    with b_col2:
        if current_streak >= 3:
            st.success("🔥 **三连胜**\n\n连续打卡 3 天！")
        else:
            st.info(f"🔒 **三连胜**\n\n(连续打卡3天，当前:{current_streak})")

    with b_col3:
        if len(all_types) >= 3:
            st.success("🌟 **全能战士**\n\n解锁 3 种以上运动！")
        else:
            st.info(f"🔒 **全能战士**\n\n(解锁3种运动，当前:{len(all_types)})")

    with b_col4:
        if max_duration >= 60:
            st.success("💪 **高能战士**\n\n单次运动超过 60 分钟！")
        else:
            st.info("🔒 **高能战士**\n\n(单次运动 ≥ 60 分钟)")

    st.markdown("---")

    # 🛠️ 核心交互标签页
    tab1, tab2, tab3 = st.tabs(["📊 统计图表", "✏️ 直接在表格修改/删除", "🗑️ 单行精准删除"])

    with tab1:
        chart_df = df.groupby("运动类型", as_index=False)["时长(分钟)"].sum()
        fig = px.bar(chart_df, x="运动类型", y="时长(分钟)", color="运动类型", 
                     color_discrete_sequence=px.colors.qualitative.Pastel, text="时长(分钟)")
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("💡 提示：双击单元格即可修改，修改完点击保存")
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="data_editor"
        )
        if st.button("💾 保存全表修改", type="primary"):
            edited_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.success("修改已保存！")
            st.rerun()

    with tab3:
        st.subheader("🗑️ 快速删除指定记录")
        if not df.empty:
            df['display_text'] = df.apply(lambda row: f"【{row['日期']}】 {row['运动类型']} - {row['时长(分钟)']}分钟 ({row['备注']})", axis=1)
            selected_option = st.selectbox("选择要删除的记录：", df['display_text'])
            
            if st.button("确认删除该记录 ❌", type="secondary"):
                selected_index = df[df['display_text'] == selected_option].index
                df_updated = df.drop(selected_index).drop(columns=['display_text'])
                df_updated.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.success("记录已成功删除！")
                st.rerun()
        else:
            st.info("当前没有任何打卡数据。")

else:
    st.info("🎮 欢迎来到健身打卡应用！请在左侧侧边栏提交你的第一笔打卡记录。")