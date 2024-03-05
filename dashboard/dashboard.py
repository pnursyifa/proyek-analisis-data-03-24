import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# FILTER
# resample daily
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

# product performance
def create_sum_order_product_df(df):
    sum_order_product_df = all_df.groupby(by="product_category_name").order_id.nunique().sort_values(ascending=False).reset_index()
    sum_order_product_df.columns = ["product_category_name", "product_category_ordered"]
    
    return sum_order_product_df

# seller performance
def create_seller_performance_df(df):
    seller_performance_df = all_df.groupby(by=["seller_id", "product_category_name"]).agg({
        "order_id": "nunique",
        "price": "sum",}).sort_values(by="price", ascending=False).reset_index()
    seller_performance_df.columns = ["seller_id", "product_category_name", "seller_total_order", "seller_revenue"]

    return seller_performance_df

# load data
all_df = pd.read_csv("./dashboard/all_data.csv")

# agar bisa difilter -> set up datetime
datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# komponen filter
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://s3-us-west-2.amazonaws.com/cbi-image-service-prd/original/4b74afb1-5a08-411d-a791-5cee8af6be67.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
seller_performance_df = create_seller_performance_df(main_df)
sum_order_product_df = create_sum_order_product_df(main_df)

st.header('Brazillian E-Commerce Dashboard by Olist')
st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)


fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="product_category_ordered", y="product_category_name", data=sum_order_product_df.head(5), palette=colors, legend=False, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="product_category_ordered", y="product_category_name", data=sum_order_product_df.sort_values(by="product_category_ordered", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

st.subheader("Best Performing Seller")
 
col1, col2 = st.columns(2)
 
with col1:
    avg_revenue = format_currency(seller_performance_df.seller_revenue.mean(), "BRL", locale='es_CO')
    st.metric("Average Revenue", value=avg_revenue)
 
with col2:
    avg_order_count = round(seller_performance_df.seller_total_order.mean())
    st.metric("Average order", value=avg_order_count)
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(x="seller_id", y="seller_revenue", data=seller_performance_df.sort_values(by="seller_revenue", ascending=False).head(5), palette=colors, legend=False, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35, rotation=45)
 
sns.barplot(x="seller_id", y="seller_total_order", data=seller_performance_df.sort_values(by="seller_total_order", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("seller_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, rotation=45)
 
st.pyplot(fig)
 
st.caption('by Putri Nursyifa')