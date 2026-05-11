import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="car rental system", layout="wide")
st.title(" car rental system")

@st.cache_resource
def init_connection():
    return mysql.connector.connect(
        host="metro.proxy.rlwy.net",
        port=39862,
        database="railway",
        user="root",
        password="QlZQsRoqrNXBLgbFSINHBsaLNrPbgiME"
    )

conn = init_connection()

menu = st.sidebar.selectbox("menu", ["customers", "cars", "reservations", "reports"])

if menu == "customers":
    st.subheader(" customers")
    df = pd.read_sql("select * from customer", conn)
    st.dataframe(df, use_container_width=True)
    
    st.subheader(" add customer")
    with st.form("add_customer"):
        col1, col2 = st.columns(2)
        with col1:
            cid = st.number_input("customer id", step=1)
            name = st.text_input("name")
            phone = st.text_input("phone")
        with col2:
            email = st.text_input("email")
            license_num = st.text_input("license")
        submitted = st.form_submit_button("add")
        if submitted:
            cursor = conn.cursor()
            cursor.execute(f"""
                insert into customer (customer_id, name, phone, email, license) 
                values ({cid}, '{name}', '{phone}', '{email}', '{license_num}')
            """)
            conn.commit()
            st.success("customer added successfully")
            st.rerun()

elif menu == "cars":
    st.subheader(" cars list")
    df = pd.read_sql("select * from car", conn)
    st.dataframe(df, use_container_width=True)
    
    st.subheader(" add new car")
    with st.form("add_car"):
        col1, col2, col3 = st.columns(3)
        with col1:
            car_id = st.number_input("car id", step=1)
            model = st.text_input("model")
            brand = st.text_input("brand")
            year = st.number_input("year", step=1)
        with col2:
            color = st.text_input("color")
            plate_id = st.text_input("plate id")
            price_per_day = st.number_input("price per day", step=100)
        with col3:
            active = st.selectbox("active", ["yes", "no"])
            rented = st.selectbox("rented", ["yes", "no"])
            out_of_service = st.selectbox("out of service", ["yes", "no"])
            office_id = st.number_input("office id", step=1)
        
        submitted = st.form_submit_button("add car")
        if submitted:
            cursor = conn.cursor()
            cursor.execute(f"""
                insert into car (car_id, model, brand, year, color, plate_id, price_per_day, active, rented, out_of_service, office_id) 
                values ({car_id}, '{model}', '{brand}', {year}, '{color}', '{plate_id}', {price_per_day}, '{active}', '{rented}', '{out_of_service}', {office_id})
            """)
            conn.commit()
            st.success("car added successfully")
            st.rerun()
    
    st.subheader(" search available cars")
    brand_search = st.text_input("search by brand")
    if brand_search:
        query = f"select * from car where brand like '%{brand_search}%' and active = 'yes' and rented = 'no'"
        df_search = pd.read_sql(query, conn)
        st.dataframe(df_search)
    
    st.subheader(" update car status")
    with st.form("update_car"):
        car_id_update = st.number_input("car id to update", step=1)
        new_rented = st.selectbox("rented status", ["yes", "no"])
        new_active = st.selectbox("active status", ["yes", "no"])
        update_submitted = st.form_submit_button("update")
        if update_submitted:
            cursor = conn.cursor()
            cursor.execute(f"update car set rented = '{new_rented}', active = '{new_active}' where car_id = {car_id_update}")
            conn.commit()
            st.success("car status updated successfully")
            st.rerun()

elif menu == "reservations":
    st.subheader(" reservations")
    df = pd.read_sql("""
        select r.reservation_id, c.name as customer, ca.model as car, r.start_date, r.end_date, r.total_amount, r.reservation_status
        from reservation r
        join customer c on r.customer_id = c.customer_id
        join car ca on r.car_id = ca.car_id
    """, conn)
    st.dataframe(df, use_container_width=True)
    
    st.subheader(" make new reservation")
    with st.form("add_reservation"):
        col1, col2 = st.columns(2)
        with col1:
            rid = st.number_input("reservation id", step=1)
            cid = st.number_input("customer id", step=1)
            car_id = st.number_input("car id", step=1)
            pickup = st.number_input("pickup office id", step=1)
        with col2:
            return_office = st.number_input("return office id", step=1)
            start = st.date_input("start date")
            end = st.date_input("end date")
            total = st.number_input("total amount", step=100)
            status = st.selectbox("status", ["active", "completed", "reserved"])
        submitted = st.form_submit_button("add reservation")
        if submitted:
            cursor = conn.cursor()
            start_str = start.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")
            cursor.execute(f"""
                insert into reservation (reservation_id, customer_id, car_id, pickup_office_id, return_office_id, start_date, end_date, total_amount, reservation_status) 
                values ({rid}, {cid}, {car_id}, {pickup}, {return_office}, '{start_str}', '{end_str}', {total}, '{status}')
            """)
            conn.commit()
            st.success("reservation added successfully")
            st.rerun()

elif menu == "reports":
    st.subheader(" reports")
    
    st.subheader("daily payments report")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("start date")
    with col2:
        end_date = st.date_input("end date")
    
    if start_date and end_date:
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        query = f"""
            select payment_date, payment_method, sum(amount) as total
            from payment
            where payment_date between '{start_str}' and '{end_str}'
            group by payment_date, payment_method
        """
        df = pd.read_sql(query, conn)
        st.dataframe(df)
    
    st.subheader("cars status on specific day")
    specific_date = st.date_input("specific date")
    if specific_date:
        df_cars = pd.read_sql("select car_id, model, brand, plate_id, active, rented, out_of_service from car", conn)
        st.dataframe(df_cars)
    
    st.subheader("customer reservations report")
    cust_id = st.number_input("customer id", step=1)
    if cust_id:
        query = f"""
            select c.name, ca.model, ca.plate_id, r.start_date, r.end_date, r.reservation_status, r.total_amount
            from reservation r
            join customer c on r.customer_id = c.customer_id
            join car ca on r.car_id = ca.car_id
            where c.customer_id = {cust_id}
        """
        df = pd.read_sql(query, conn)
        st.dataframe(df)
