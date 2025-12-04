import streamlit as st
import pandas as pd
import altair as alt

# =========================================================
# 【重要】 st.set_page_config は必ず最初に実行される Streamlit コマンドにする
# =========================================================
# ↓↓↓↓↓ この行を、import文の直後に移動します ↓↓↓↓↓
st.set_page_config(layout="wide", page_title="訪日旅行者分析ダッシュボード")

# Excelファイルの絶対パスを定義（Raw Stringでバックスラッシュをエスケープ不要にする）
# 【注意】デプロイ時は相対パスに戻す必要があります
EXCEL_FILE_PATH = r"C:\Users\piani\OneDrive - Yokohama City University\Leeds授業\Data Science\Assessment\dashboard\formatted data.xlsx"

# データのロード (キャッシュを使って高速化)
@st.cache_data
def load_data(file_path, sheet_index):
    """
    指定されたExcelファイルパスとシートインデックスからデータを読み込みます。
    """
    # sheet_nameにインデックス（0, 1, ...）を指定
    try:
        # Excelファイルを読み込むには openpyxl が必要です (pip install openpyxl でインストール済みと仮定)
        df = pd.read_excel(file_path, sheet_name=sheet_index)
        return df
    except FileNotFoundError:
        # st.error() が st.set_page_config() より先に呼ばれることで発生するエラーを回避
        st.error(f"エラー: ファイルが見つかりません。パスを確認してください: {file_path}")
        return pd.DataFrame() # 空のDataFrameを返す
    except ValueError:
        st.error(f"エラー: シートインデックス {sheet_index} が存在しないか、ファイル形式が不正です。")
        return pd.DataFrame()

# ---------------------------------------------------------
# データのロードと割り当て
# ---------------------------------------------------------

# シート0 (インデックス 0) を主要なデータとしてロード
df_summary = load_data(EXCEL_FILE_PATH, 0)

# シート1 (インデックス 1) をロード (必要に応じて他の分析に使用)
df_summary_1 = load_data(EXCEL_FILE_PATH, 1)

# データが空の場合は処理を停止
if df_summary.empty:
    st.stop()

# --- Streamlit アプリケーションの開始 ---
st.title("🇯🇵 訪日旅行者データ分析ダッシュボード")
st.markdown("---")

# ロードしたデータフレームの確認 (デバッグ用)
st.sidebar.header("データ情報")
st.sidebar.write(f"シート0 (df_summary): {len(df_summary)} 行")
st.sidebar.write(f"シート1 (df_summary_1): {len(df_summary_1)} 行")

# =========================================================
# グラフ 1: 主要な入国港のシェア比較 (積み上げ棒グラフ)
# =========================================================

st.header("1. 入国港別シェア比較 (全体 vs イギリス人旅行者)")

# 'Category' カラムが存在するか確認（Excelファイルの構造が想定と異なる場合に備える）
if 'Category' not in df_summary.columns:
    st.error("エラー: データフレームに 'Category' カラムが見つかりません。シート0のデータ構造を確認してください。")
    st.stop()

# 'Port of Entry' カテゴリのみを抽出
df_port_entry = df_summary[df_summary['Category'] == 'Port of Entry'].copy() # SettingWithCopyWarningを避けるために.copy()を使用

# 'Item'が不明瞭な行や、シェアが0%の行を除外
df_port_entry = df_port_entry[
    (df_port_entry['Item'] != 'total') & 
    (df_port_entry['all:Share (%)'] > 0)
]

# 比較のためにデータを整形 (Melt操作)
# Note: 'all:Share (%)'と'uk:Share (%)'がExcelのシート0に存在することを前提とします。
if 'all:Share (%)' in df_port_entry.columns and 'uk:Share (%)' in df_port_entry.columns:
    df_chart = df_port_entry.melt(
        id_vars=['Item'],
        value_vars=['all:Share (%)', 'uk:Share (%)'],
        var_name='Group',
        value_name='Share (%)'
    )

    # グループ名を日本語に変換
    df_chart['Group'] = df_chart['Group'].replace({
        'all:Share (%)': '全体 (All)',
        'uk:Share (%)': 'イギリス (UK)'
    })

    # Altairで積み上げ棒グラフを作成
    chart = alt.Chart(df_chart).mark_bar().encode(
        # x軸: シェア
        x=alt.X('Share (%):Q', stack="normalize", axis=alt.Axis(format='%')),
        # y軸: 入国港
        y=alt.Y('Item:N', title='入国港 (Port of Entry)', sort='-x'),
        # 色: グループ (全体 / UK)
        color=alt.Color('Group:N', title='旅行者グループ'),
        # ツールチップ
        tooltip=['Item', 'Group', alt.Tooltip('Share (%):Q', format='.1f')]
    ).properties(
        title="主要入国港のシェア (全体とイギリス人旅行者の比較)"
    ).interactive() # ズームとパンを可能にする

    # Streamlitにグラフを表示
    st.altair_chart(chart, use_container_width=True)

    st.caption("※ Share (%) は各グループ内での割合です。")
else:
    st.warning("警告: グラフ描画に必要なカラム ('all:Share (%)' または 'uk:Share (%)') がシート0のデータフレームに見つかりません。")

# --- (以下にシート1を使った分析などを追加できます) ---
# 例: シート1のデータをサイドバーに表示
# st.sidebar.subheader("シート1の最初の数行")
# st.sidebar.dataframe(df_summary_1.head())