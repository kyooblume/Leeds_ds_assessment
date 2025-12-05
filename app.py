import streamlit as st
import pandas as pd
import altair as alt
import re

# =========================================================
# 1. Page Config
# =========================================================
st.set_page_config(layout="wide", page_title="🇬🇧 UK Tourist Analysis: Complete Dashboard")

st.title("🇬🇧 UK Tourist Analysis: Comprehensive Dashboard")
st.markdown("""
**Aim:** To provide a 360-degree view of UK tourists in Japan, from demographics to detailed spending habits, identifying key strategic opportunities.
""")

# =========================================================
# 2. Data Loading & Cleaning
# =========================================================
@st.cache_data
def load_data():
    try:
        df_sum = pd.read_csv("summary_data.csv", encoding='utf-8')
        df_exp = pd.read_csv("expenditure_data.csv", encoding='utf-8')
    except Exception as e:
        st.error(f"❌ Critical Error: Failed to load CSV files. {e}")
        return pd.DataFrame(), pd.DataFrame()
    
    # --- 1. Column Name Normalization ---
    def clean_col_name(name):
        name = name.strip()
        name = re.sub(r'\s*[:：]\s*', '_', name) 
        name = re.sub(r'\s+', '_', name) 
        name = re.sub(r'[¥%()]', '', name)
        return name

    df_sum.columns = [clean_col_name(c) for c in df_sum.columns]
    df_exp.columns = [clean_col_name(c) for c in df_exp.columns]
    
    # --- 2. Remove 'total' rows from Summary ---
    if 'Item' in df_sum.columns:
        df_sum = df_sum[df_sum['Item'] != 'total']

    # --- 3. Clean Item Names in Expenditure ---
    # Remove leading hyphens (e.g., "- Domestic Airfare" -> "Domestic Airfare")
    item_col_exp = next((c for c in df_exp.columns if 'item' in c.lower()), None)
    if item_col_exp:
        df_exp[item_col_exp] = df_exp[item_col_exp].astype(str).str.replace(r'^- ', '', regex=True).str.strip()

    # --- 4. Numeric Conversion ---
    def convert_to_numeric(df):
        for col in df.columns:
            if any(x in col.lower() for x in ['share', 'rate', 'price', 'spending', 'nights', 'count']):
                try:
                    df[col] = pd.to_numeric(
                        df[col].astype(str).str.replace(',', '').str.replace('%', '').str.replace('nan', ''),
                        errors='coerce'
                    ).fillna(0)
                except:
                    pass
        return df

    df_sum = convert_to_numeric(df_sum)
    df_exp = convert_to_numeric(df_exp)

    # --- 5. Calculate Overall Age Distribution ---
    # Merge Male and Female shares to approximate Overall Age
    male_data = df_sum[df_sum['Category'] == 'male'].set_index('Item')
    female_data = df_sum[df_sum['Category'] == 'female'].set_index('Item')
    
    if not male_data.empty and not female_data.empty:
        uk_share_col = [c for c in df_sum.columns if 'uk' in c.lower() and 'share' in c.lower()][0]
        all_share_col = [c for c in df_sum.columns if 'all' in c.lower() and 'share' in c.lower()][0]
        
        age_items = male_data.index.intersection(female_data.index)
        overall_age = pd.DataFrame(index=age_items)
        overall_age['Category'] = 'Age (Overall)'
        overall_age['Item'] = age_items
        overall_age[uk_share_col] = (male_data[uk_share_col] + female_data[uk_share_col]) / 2
        overall_age[all_share_col] = (male_data[all_share_col] + female_data[all_share_col]) / 2
        
        df_sum = pd.concat([df_sum, overall_age.reset_index(drop=True)])

    return df_sum, df_exp

df_summary, df_expenditure = load_data()

if df_summary.empty:
    st.warning("⚠️ Data is empty. Please check your CSV files.")
    st.stop()

# Debug: Option to show raw data if things go wrong
with st.sidebar.expander("🛠️ Debug: Raw Data"):
    st.write("Summary Data Head:", df_summary.head())
    st.write("Expenditure Data Head:", df_expenditure.head())

# =========================================================
# Helper Functions
# =========================================================
def create_bar_chart(df, category_query, title, sort_order=None, height=300):
    available_cats = df['Category'].unique()
    target_cat = None
    
    # Try exact match first, then fuzzy
    if category_query in available_cats:
        target_cat = category_query
    else:
        for c in available_cats:
            if category_query.lower() in str(c).lower():
                target_cat = c
                break
    
    if target_cat is None:
        st.error(f"❌ Data for category '{category_query}' not found. Available categories: {available_cats}")
        return

    data = df[df['Category'] == target_cat].copy()
    
    uk_col = [c for c in data.columns if 'uk' in c.lower() and 'share' in c.lower()][0]
    all_col = [c for c in data.columns if 'all' in c.lower() and 'share' in c.lower()][0]

    melted = data.melt(id_vars=['Item'], value_vars=[all_col, uk_col], 
                       var_name='Group', value_name='Share')
    melted['Group'] = melted['Group'].map({all_col: 'All', uk_col: 'UK'})
    
    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X('Item', sort=sort_order if sort_order else '-y', title="", axis=alt.Axis(labels=True)),
        y=alt.Y('Share', title="Share (%)"),
        color=alt.Color('Group', scale=alt.Scale(domain=['All', 'UK'], range=['#A9A9A9', '#0070C0'])),
        xOffset='Group',
        tooltip=['Item', 'Share', 'Group']
    ).properties(title=title, height=height)
    
    st.altair_chart(chart, use_container_width=True)

def create_subset_chart(df, items_list, title, metric_type):
    item_col = next((c for c in df.columns if 'item' in c.lower()), None)
    if not item_col: return
    
    # Robust Filtering: Check if ANY keyword is in the item name
    # We join keywords with '|' for regex OR logic
    pattern = '|'.join(items_list)
    mask = df[item_col].astype(str).str.contains(pattern, case=False, regex=True)
    data = df[mask].copy()
    
    if data.empty:
        st.warning(f"⚠️ No data found for chart: {title}. Keywords: {items_list}")
        return

    # Find columns
    if metric_type == 'Rate':
        uk_col = [c for c in df.columns if 'uk' in c.lower() and 'rate' in c.lower()][0]
        all_col = [c for c in df.columns if 'all' in c.lower() and 'rate' in c.lower()][0]
        y_label = "Participation Rate (%)"
    else:
        uk_col = [c for c in df.columns if 'uk' in c.lower() and 'price' in c.lower()][0]
        all_col = [c for c in df.columns if 'all' in c.lower() and 'price' in c.lower()][0]
        y_label = "Unit Price (¥)"

    melted = data.melt(id_vars=[item_col], value_vars=[all_col, uk_col], 
                       var_name='Group', value_name='Value')
    melted['Group'] = melted['Group'].map({all_col: 'All', uk_col: 'UK'})

    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X(item_col, sort='-y', title=""),
        y=alt.Y('Value', title=y_label),
        color=alt.Color('Group', scale=alt.Scale(domain=['All', 'UK'], range=['#A9A9A9', '#0070C0'])),
        xOffset='Group',
        tooltip=[item_col, 'Value', 'Group']
    ).properties(title=title, height=350)
    
    st.altair_chart(chart, use_container_width=True)

# =========================================================
# 3. Dashboard Tabs (Modified: Tab 4 removed)
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 1. Demographics & Wealth", 
    "✈️ 2. Purpose & Journey", 
    "💰 3. Detailed Expenditure",
    "📝 4. Conclusions"  # Renumbered
])

# --- TAB 1: DEMOGRAPHICS ---
with tab1:
    st.header("Who are they?")
    
    # Age (Overall)
    st.subheader("Age Distribution (Overall)")
    age_order = ['15～19years old', '20～29years old', '30～39years old', '40～49years old', 
                 '50～59years old', '60～69years old', 'over 70years old']
    create_bar_chart(df_summary, 'Age (Overall)', "Age Groups (Male & Female Combined)", sort_order=age_order)

    st.markdown("---")
    st.subheader("Wealth Indicators")
    col1, col2 = st.columns(2)
    with col1:
        create_bar_chart(df_summary, 'Household Annual Income', "Annual Income (Flow)")
    with col2:
        create_bar_chart(df_summary, 'Household Net Financial Assets', "Net Financial Assets (Stock)")

# --- TAB 2: JOURNEY ---
with tab2:
    st.header("Travel Characteristics")
    
    st.subheader("Main Purpose of Visit")
    create_bar_chart(df_summary, 'purpose', "Purpose Breakdown", height=400)
    st.info("💡 **Insight:** Note the high percentage of **'Other Business'** and **'Training'**. UK tourists are not just leisure travelers; many are here for business.")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        create_bar_chart(df_summary, 'Port of Entry', "Entry Airport")
    with col2:
        create_bar_chart(df_summary, 'accommodation type', "Accommodation Preference")
    
    col3, col4 = st.columns(2)
    with col3:
        create_bar_chart(df_summary, 'companion', "Travel Companion")
    with col4:
        stay_order = ['Within 3 days', '4 to 6 days', '7 to 13 days', '14 to 20 days', 
                      '21 to 27 days', '28 to 90 days', '91 days or more']
        create_bar_chart(df_summary, 'Length of Stay', "Stay Duration", sort_order=stay_order)

# --- TAB 3: EXPENDITURE ---
with tab3:
    st.header("💰 Deep Dive: Spending Habits")
    
    if not df_expenditure.empty:
        st.subheader("1. General Overview (Top 10 by Rate)")
        cols = df_expenditure.columns
        uk_rate_cols = [c for c in cols if 'uk' in c.lower() and 'rate' in c.lower()]
        item_col = next((c for c in cols if 'item' in c.lower()), None)
        
        if uk_rate_cols and item_col:
            # Show top 10 items
            df_top = df_expenditure.sort_values(uk_rate_cols[0], ascending=False).head(10)
            top_items = df_top[item_col].astype(str).tolist()
            create_subset_chart(df_expenditure, top_items, "Top 10 Participation Rates", "Rate")

        st.markdown("---")

        # 2. Shopping (Using simplified keywords to ensure matching)
        st.subheader("2. Shopping Preferences")
        shopping_items = ['Confectionery', 'Cosmetics', 'Clothing', 'Shoes', 'Alcohol', 'Crafts', 'Medicine']
        create_subset_chart(df_expenditure, shopping_items, "Shopping Items (Rate %)", "Rate")
        
        # 3. Entertainment
        st.subheader("3. Experience & Entertainment")
        entertain_items = ['Museum', 'Springs', 'Theme', 'Ski', 'Tour', 'Theater', 'Sport', 'Zoo']
        create_subset_chart(df_expenditure, entertain_items, "Entertainment (Rate %)", "Rate")
        
    else:
        st.warning("No Expenditure Data")

# --- TAB 4 (Formerly Tab 5): CONCLUSIONS ---
with tab4:
    st.header("📝 Executive Summary")
    st.markdown("""
    ### **Strategic Recommendations**
    1.  **Target the Wealthy:** Data shows UK tourists are asset-rich. Pitch premium services.
    2.  **Sell Culture, Not Cosmetics:** They buy "Folk Crafts" & "Kimono rentals" more than cosmetics.
    3.  **Long-Stay Hubs:** Promote Haneda + Luxury Hotel as a base for 2-week cultural explorations.
    """)