import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "autoservice_db.json"

# ─────────────────────────────────────────────────────────────
# 🗄 Работа с данными (JSON вместо БД)
# ─────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "clients": [],
        "cars": [],
        "orders": [],
        "services": [
            {"id": 1, "name": "Замена масла", "price": 800},
            {"id": 2, "name": "Компьютерная диагностика", "price": 1200},
            {"id": 3, "name": "Замена тормозных колодок", "price": 2500},
            {"id": 4, "name": "Развал-схождение", "price": 1800},
            {"id": 5, "name": "Замена свечей зажигания", "price": 600}
        ]
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────────────────────
# 🎨 Интерфейс и логика
# ─────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="ИС Автосервис", layout="wide", page_icon="🔧")
    if "data" not in st.session_state:
        st.session_state.data = load_data()

    st.title("🔧 Информационная система «Автосервис»")
    st.markdown("---")
    
    menu = st.sidebar.radio("📌 Меню", ["📊 Главная", "👥 Клиенты", "🚗 Автомобили", "📝 Новый заказ", "📋 Журнал заказов"])

    if menu == "📊 Главная": 
        show_dashboard()
    elif menu == "👥 Клиенты": 
        show_clients()
    elif menu == "🚗 Автомобили": 
        show_cars()
    elif menu == "📝 Новый заказ": 
        show_new_order()
    elif menu == "📋 Журнал заказов": 
        show_orders()

    st.sidebar.markdown("---")
    if st.sidebar.button("🗑 Сбросить все данные"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.session_state.data = load_data()
            st.success("✅ Данные сброшены!")
            st.rerun()

# ─────────────────────────────────────────────────────────────
# 📊 Главная
# ─────────────────────────────────────────────────────────────
def show_dashboard():
    data = st.session_state.data
    st.header("📊 Сводка по автосервису")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Всего клиентов", len(data["clients"]))
    col2.metric("🚗 Автомобилей", len(data["cars"]))
    col3.metric("📝 Заказов", len(data["orders"]))
    
    total_revenue = sum(o["total"] for o in data["orders"] if o["status"] == "Оплачен")
    col4.metric("💰 Выручка", f"{total_revenue} ₽")

    st.markdown("---")
    st.subheader("📋 Последние заказы")
    if data["orders"]:
        recent = sorted(data["orders"], key=lambda x: x["id"], reverse=True)[:5]
        for o in recent:
            status_emoji = {"Новый": "", "В работе": "", "Готов": "✅", "Оплачен": "💰"}.get(o["status"], "📄")
            st.info(f"{status_emoji} **Заказ #{o['id']}** | {o['client']} | {o['car']} | {o['total']} ₽ | {o['status']}")
    else:
        st.info("📭 Заказов пока нет")

# ─────────────────────────────────────────────────────────────
# 👥 Клиенты
# ─────────────────────────────────────────────────────────────
def show_clients():
    st.header("👥 Управление клиентами")
    data = st.session_state.data
    
    with st.form("client_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("ФИО клиента *", placeholder="Иванов Иван Иванович")
        with col2:
            phone = st.text_input("Номер телефона *", placeholder="+7 (999) 123-45-67")
        
        submitted = st.form_submit_button("➕ Добавить клиента", use_container_width=True)
        
        if submitted:
            if not full_name.strip():
                st.error("❌ Поле «ФИО клиента» обязательно для заполнения!")
            elif not phone.strip():
                st.error("❌ Поле «Номер телефона» обязательно для заполнения!")
            elif not phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "").isdigit():
                st.error("❌ В номере телефона допускаются только цифры!")
            else:
                # Проверяем, нет ли уже такого телефона
                phone_digits = "".join(filter(str.isdigit, phone))
                for client in data["clients"]:
                    if "".join(filter(str.isdigit, client["phone"])) == phone_digits:
                        st.error("❌ Клиент с таким номером телефона уже существует!")
                        return
                
                data["clients"].append({
                    "id": len(data["clients"]) + 1, 
                    "full_name": full_name.strip(), 
                    "phone": phone.strip()
                })
                save_data(data)
                st.success("✅ Клиент успешно добавлен!")
                st.rerun()

    st.markdown("---")
    st.subheader(f"📋 Список клиентов (всего: {len(data['clients'])})")
    
    if data["clients"]:
        clients_df = []
        for c in data["clients"]:
            clients_df.append({
                "ID": c["id"],
                "ФИО": c["full_name"],
                "Телефон": c["phone"]
            })
        st.dataframe(clients_df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Клиентов пока нет. Добавьте первого клиента выше!")

# ─────────────────────────────────────────────────────────────
# 🚗 Автомобили
# ─────────────────────────────────────────────────────────────
def show_cars():
    st.header("🚗 Парк автомобилей")
    data = st.session_state.data
    
    clients = {c["id"]: c["full_name"] for c in data["clients"]}
    
    if not clients:
        st.warning("⚠️ Сначала добавьте клиентов в разделе «👥 Клиенты»")
        return

    with st.form("car_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            client_id = st.selectbox("Владелец автомобиля *", options=list(clients.keys()), format_func=lambda x: clients[x])
            brand = st.text_input("Марка автомобиля *", placeholder="Toyota")
        with col2:
            model = st.text_input("Модель *", placeholder="Camry")
            plate = st.text_input("Государственный номер *", placeholder="А123БВ777")
        
        submitted = st.form_submit_button("🚗 Добавить автомобиль", use_container_width=True)
        
        if submitted:
            if not brand.strip():
                st.error("❌ Поле «Марка автомобиля» обязательно для заполнения!")
            elif not plate.strip():
                st.error("❌ Поле «Государственный номер» обязательно для заполнения!")
            else:
                data["cars"].append({
                    "id": len(data["cars"]) + 1, 
                    "client_id": client_id, 
                    "brand": brand.strip(), 
                    "model": model.strip(), 
                    "plate": plate.strip().upper()
                })
                save_data(data)
                st.success("✅ Автомобиль успешно добавлен!")
                st.rerun()

    st.markdown("---")
    st.subheader(f"📋 Все автомобили (всего: {len(data['cars'])})")
    
    if data["cars"]:
        cars_df = []
        for c in data["cars"]:
            cars_df.append({
                "ID": c["id"],
                "Владелец": clients[c["client_id"]],
                "Марка": c["brand"],
                "Модель": c["model"],
                "Гос. номер": c["plate"]
            })
        st.dataframe(cars_df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Автомобилей пока нет")

# ─────────────────────────────────────────────────────────────
# 📝 Новый заказ
# ─────────────────────────────────────────────────────────────
def show_new_order():
    st.header("📝 Создание заказ-наряда")
    data = st.session_state.data
    
    if not data["clients"] or not data["cars"]:
        st.warning("⚠️ Необходимо добавить клиентов и автомобили")
        return

    cars_map = {c["id"]: f"{c['brand']} {c['model']} ({c['plate']})" for c in data["cars"]}
    client_map = {c["id"]: c["full_name"] for c in data["clients"]}
    car_owner = {c["id"]: c["client_id"] for c in data["cars"]}

    with st.form("order_form", clear_on_submit=True):
        car_id = st.selectbox("Выберите автомобиль *", options=list(cars_map.keys()), format_func=lambda x: cars_map[x])
        
        st.markdown("**🔧 Выберите услуги:**")
        services = st.multiselect(
            "Услуги", 
            options=[s["name"] for s in data["services"]],
            help="Выберите одну или несколько услуг"
        )
        
        if services:
            total = sum(s["price"] for s in data["services"] if s["name"] in services)
            st.success(f"💰 **Итого к оплате: {total} ₽**")
        else:
            st.info("💰 Итого: 0 ₽")
        
        submitted = st.form_submit_button("✅ Оформить заказ", use_container_width=True)
        
        if submitted:
            if not services:
                st.error("❌ Выберите хотя бы одну услугу!")
            else:
                cid = car_owner[car_id]
                new_order = {
                    "id": len(data["orders"]) + 1,
                    "client_id": cid,
                    "client": client_map[cid],
                    "car": cars_map[car_id],
                    "services": services,
                    "total": total,
                    "status": "Новый",
                    "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
                }
                data["orders"].append(new_order)
                save_data(data)
                st.success("✅ Заказ успешно создан!")
                st.rerun()

# ─────────────────────────────────────────────────────────────
# 📋 Журнал заказов
# ─────────────────────────────────────────────────────────────
def show_orders():
    st.header("📋 Журнал заказов")
    data = st.session_state.data
    
    if not data["orders"]:
        st.info("📭 Заказов пока нет")
        return

    # Фильтры
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Фильтр по статусу", ["Все", "Новый", "В работе", "Готов", "Оплачен"])
    
    filtered_orders = data["orders"]
    if status_filter != "Все":
        filtered_orders = [o for o in data["orders"] if o["status"] == status_filter]
    
    st.markdown(f"**Всего заказов:** {len(filtered_orders)}")
    st.markdown("---")

    for i, o in enumerate(data["orders"]):
        if status_filter != "Все" and o["status"] != status_filter:
            continue
            
        status_emoji = {"Новый": "🆕", "В работе": "🔧", "Готов": "✅", "Оплачен": "💰"}.get(o["status"], "📄")
        
        with st.expander(f"{status_emoji} **Заказ #{o['id']}** | {o['client']} | {o['car']} | {o['total']} ₽ | {o['status']}"):
            st.write(f"📅 **Дата создания:** {o['created_at']}")
            st.write(f"🔧 **Услуги:** {', '.join(o['services'])}")
            st.write(f"💰 **Сумма:** {o['total']} ₽")
            
            st.markdown("**Изменить статус:**")
            col1, col2, col3, col4 = st.columns(4)
            for status, col, emoji in [("Новый", col1, "🆕"), ("В работе", col2, "🔧"), ("Готов", col3, "✅"), ("Оплачен", col4, "💰")]:
                if col.button(f"{emoji} {status}", key=f"status_{o['id']}_{status}", use_container_width=True):
                    data["orders"][i]["status"] = status
                    save_data(data)
                    st.success(f"✅ Статус заказа #{o['id']} изменён на «{status}»")
                    st.rerun()

# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()