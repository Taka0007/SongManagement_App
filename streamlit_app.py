import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import StringIO
import os
from datetime import datetime
import subprocess

st.title("🎤 カラオケ曲リスト管理アプリ")

# CSVファイルのパス
CSV_FILE_PATH = 'song_list.csv'

# 初期データの読み込みまたは作成
if os.path.exists(CSV_FILE_PATH):
    song_df = pd.read_csv(CSV_FILE_PATH)
else:
    song_df = pd.DataFrame(columns=["曲名", "アーティスト名", "得点"])

# セッション状態にデータフレームを保存
if 'song_df' not in st.session_state:
    st.session_state['song_df'] = song_df.copy()

# 曲の追加フォーム
st.header("➕ 曲の追加")
with st.form("add_song_form"):
    song_name = st.text_input("曲名を入力")
    artist_name = st.text_input("アーティスト名を入力")
    score = st.number_input("得点を入力（0-100）", min_value=0.0, max_value=100.0, step=0.1)
    submitted = st.form_submit_button("曲を追加")

    if submitted and song_name and artist_name:
        new_entry = {"曲名": song_name, "アーティスト名": artist_name, "得点": score}
        st.session_state['song_df'] = st.session_state['song_df'].append(new_entry, ignore_index=True)
        st.success(f"「{song_name}」をリストに追加しました。")

        # CSVに保存
        st.session_state['song_df'].to_csv(CSV_FILE_PATH, index=False)

        # GitHubにプッシュ
        # push_to_github()  # 後述の関数を参照

# 曲の検索
st.header("🔍 曲の検索")
search_option = st.selectbox("検索条件を選択", ["曲名", "アーティスト名"])
search_query = st.text_input("検索キーワードを入力")
if st.button("検索"):
    if search_query:
        filtered_df = st.session_state['song_df'][st.session_state['song_df'][search_option].str.contains(search_query, na=False)]
        if not filtered_df.empty:
            st.table(filtered_df)
        else:
            st.warning("該当する結果が見つかりませんでした。")
    else:
        st.warning("検索キーワードを入力してください。")

# 曲リストの表示
st.header("🎶 現在の曲リスト")
if not st.session_state['song_df'].empty:
    st.table(st.session_state['song_df'])
else:
    st.write("曲リストはまだ空です。")

# 曲の削除機能
st.header("🗑️ 曲の削除")
delete_song = st.text_input("削除したい曲名を入力")
if st.button("曲を削除"):
    if delete_song:
        initial_count = len(st.session_state['song_df'])
        st.session_state['song_df'] = st.session_state['song_df'][st.session_state['song_df']['曲名'] != delete_song]
        if len(st.session_state['song_df']) < initial_count:
            st.success(f"「{delete_song}」を削除しました。")
            st.session_state['song_df'].to_csv(CSV_FILE_PATH, index=False)
            # GitHubにプッシュ
            # push_to_github()
        else:
            st.warning(f"「{delete_song}」が見つかりませんでした。")
    else:
        st.warning("削除したい曲名を入力してください。")

# 得点の統計情報とグラフ表示
st.header("📊 得点の統計情報と分布")
if not st.session_state['song_df'].empty and st.session_state['song_df']['得点'].notnull().any():
    score_series = st.session_state['song_df']['得点'].dropna()
    st.write("**基礎統計量**")
    st.write(score_series.describe())

    st.write("**得点分布のヒストグラム**")
    fig, ax = plt.subplots()
    sns.histplot(score_series, bins=10, kde=True, ax=ax)
    st.pyplot(fig)
else:
    st.write("得点データがありません。")

# GitHubにプッシュする関数（キーやトークンは別途設定が必要）
def push_to_github():
    commit_message = f"データ更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "add", CSV_FILE_PATH])
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push", "origin", "main"])
