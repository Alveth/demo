import streamlit as st
import time
import uuid
from datetime import datetime
import pydeck as pdk
import math
import random
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="救急救命支援アプリ MVP", layout="wide")

# ---------------------------
# 初期データ
# ---------------------------
if "users" not in st.session_state:
    st.session_state.users = {}
if "medical_profiles" not in st.session_state:
    st.session_state.medical_profiles = {}
if "help_events" not in st.session_state:
    st.session_state.help_events = {}
if "responders_notified" not in st.session_state:
    st.session_state.responders_notified = []
if "aed_data" not in st.session_state:
    st.session_state.aed_data = [
        {"id": "1", "name": "駅前AED", "lat": 35.681236, "lon": 139.767125},
        {"id": "2", "name": "市役所AED", "lat": 35.682500, "lon": 139.770000},
    ]

# ---------------------------
# ユーティリティ関数
# ---------------------------
def show_disclaimer():
    st.warning("⚠ このアプリは医療行為を提供するものではありません。119通報を最優先してください。応急救護を支援する目的です。")

def distance_km(loc1, loc2):
    return round(random.uniform(0.1, 0.9),3)

def update_location():
    loc = get_geolocation()
    if loc and "coords" in loc:
        lat = loc["coords"]["latitude"]
        lon = loc["coords"]["longitude"]
        if "current_user" in st.session_state:
            st.session_state.users[st.session_state.current_user]["location"] = {"lat":lat,"lon":lon}
        st.success(f"現在地取得: {lat}, {lon}")
    else:
        st.warning("位置情報を取得できませんでした（ブラウザで許可してください）")

def create_help_event(user_id, situation):
    event_id = str(uuid.uuid4())
    location = st.session_state.users[user_id]["location"]
    st.session_state.help_events[event_id] = {
        "id": event_id,
        "creatorUserId": user_id,
        "createdAt": datetime.now(),
        "location": location,
        "status": "発生",
        "situationType": situation,
        "responders": [],
    }
    notify_responders(event_id)
    return event_id

def notify_responders(event_id):
    event = st.session_state.help_events[event_id]
    for user_id, user in st.session_state.users.items():
        if user["role"]=="救助者" and user["available"]:
            st.session_state.responders_notified.append({"userId":user_id,"eventId":event_id,"notifiedAt":datetime.now()})

# ---------------------------
# テストユーザー初期化
# ---------------------------
if "current_user" not in st.session_state:
    user_id = str(uuid.uuid4())
    st.session_state.current_user = user_id
    st.session_state.users[user_id] = {
        "id": user_id,
        "role": "一般",
        "name": "テストユーザー",
        "location": {"lat":35.564311,"lon":139.715093},
        "notificationSound": True,
        "available": True,
        "score":0,
        "dispatch_count":0,
        "arrival_count":0,
    }

if len(st.session_state.users)==1:
    user_id = str(uuid.uuid4())
    st.session_state.users[user_id] = {
        "id":user_id,
        "role":"救助者",
        "name":"救助者テスト",
        "location":{"lat":35.6825,"lon":139.7690},
        "notificationSound":True,
        "available":True,
        "score":0,
        "dispatch_count":0,
        "arrival_count":0,
    }

update_location()

# ---------------------------
# 下部ナビゲーション（互換性高く安全）
# ---------------------------
st.markdown("---")
cols = st.columns(5)

buttons = [
    {"label": "🏠ホーム", "color": "#e74c3c", "page": "ホーム"},
    {"label": "📘救命手順ガイド", "color": "#3498db", "page": "手順ガイド"},
    {"label": "🧾プロフィール", "color": "#2ecc71", "page": "プロフィール"},
    {"label": "🦺救助者プロフィール", "color": "#f39c12", "page": "救助者プロフィール"},
    {"label": "⚙設定", "color": "#9b59b6", "page": "設定"},
]

for col, btn in zip(cols, buttons):
    if col.button(btn["label"]):
        st.session_state.page = btn["page"]
    # ボタン色を反映
    col.markdown(f"""
        <style>
        div.stButton button:first-child {{
            background-color: {btn['color']};
            color: white;
            font-weight: bold;
        }}
        </style>
    """, unsafe_allow_html=True)

# page変数に必ず代入
if "page" not in st.session_state:
    st.session_state.page = "ホーム"
page = st.session_state.page

# ユーザー切替（テスト用）
if len(st.session_state.users)>1:
    user_list=list(st.session_state.users.keys())
    user_options=[f"{st.session_state.users[u]['name']} ({u[:4]})" for u in user_list]
    selected_user_idx=st.sidebar.selectbox("ユーザー切替（試運転用）", range(len(user_list)), format_func=lambda i:user_options[i])
    st.session_state.current_user=user_list[selected_user_idx]

# ---------------------------
# オンボーディング
# ---------------------------
if "onboarded" not in st.session_state:
    show_disclaimer()
    if st.button("同意して開始"):
        st.session_state.onboarded=True
        st.rerun()
    st.stop()

# ---------------------------
# ホーム画面（HELPボタン主体）
# ---------------------------
if page=="ホーム":
    user = st.session_state.users[st.session_state.current_user]
    st.title("🆘 救急救命支援")

    if user["role"]=="一般":
        situation = st.selectbox(
            "状況を選択",
            ["意識なし","呼吸が弱い・ない","胸痛","転倒・骨折疑い","大出血","けいれん","その他"]
        )

        # 中央に大きなHELPボタン
        st.markdown("""
        <style>
        .big-help-button {
            display: flex;
            justify-content: center;
            margin-top: 50px;
            margin-bottom: 50px;
        }
        .big-help-button button {
            width: 300px;
            height: 200px;
            font-size: 48px;
            font-weight: bold;
            background-color: red;
            color: white;
            border-radius: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="big-help-button">', unsafe_allow_html=True)
        help_pressed = st.button("🆘 HELP")
        st.markdown('</div>', unsafe_allow_html=True)

        if help_pressed:
            show_disclaimer()
            with st.spinner("3秒長押し中..."):
                time.sleep(3)
            event_id = create_help_event(st.session_state.current_user, situation)
            st.success("近隣の救助者へ通知しました！")
            st.button("📞 今すぐ119へ", on_click=lambda: st.info("119へ通報してください"))

            # 5秒以内キャンセル可能
            cancel_allowed = True
            start_time = time.time()
            cancel_placeholder = st.empty()
            cancel_clicked = False

            while time.time() - start_time < 5:
                if cancel_placeholder.button("5秒以内にキャンセル"):
                    cancel_clicked = True
                    break
                time.sleep(0.1)  # 微小待機
            cancel_placeholder.empty()  # ボタンを消す

            if cancel_clicked:
                st.session_state.help_events[event_id]["status"] = "キャンセル"
                st.warning("HELPをキャンセルしました")
            else:
                st.session_state.active_event = event_id
                st.info("HELP発生中です。119へ通報してください。")

    elif user["role"]=="救助者":
        st.subheader("🦺 出動可能 HELP通知")
        for notif in st.session_state.responders_notified:
            if notif["userId"]==st.session_state.current_user:
                event=st.session_state.help_events[notif["eventId"]]
                if event["status"]=="発生":
                    st.warning(f"🚨 HELP発生: {event['situationType']}")
                    st.map([event["location"]])
                    if st.button(f"向かいます ({event['id'][:4]})"):
                        if st.session_state.current_user not in event["responders"]:
                            event["responders"].append(st.session_state.current_user)
                            st.success("出動登録をしました。向かってください。")
        
        st.subheader("AED位置情報")
        aed_map_data=[{"lat":a["lat"],"lon":a["lon"]} for a in st.session_state.aed_data]
        st.map(aed_map_data)

# ---------------------------
# 手順ガイド
# ---------------------------
elif page=="手順ガイド":
    st.title("📘 救命手順ガイド")
    st.subheader("胸骨圧迫")
    st.info("1. 胸の中央を強く速く押す\n2. 1分間に100-120回\n3. 中断しない")
    tempo=st.toggle("CPRテンポ音 ON/OFF")
    if tempo: st.success("♪ テンポ: 110 BPM")
    st.subheader("AEDの使い方")
    st.info("1. 電源ON\n2. パッド装着\n3. 音声指示に従う")

# ---------------------------
# プロフィール
# ---------------------------
elif page=="プロフィール":
    st.title("🧾 医療情報")
    conditions=st.text_input("持病")
    allergies=st.text_input("アレルギー")
    meds=st.text_input("服薬")
    emergency=st.text_input("緊急連絡先")
    if st.button("保存"):
        st.session_state.medical_profiles[st.session_state.current_user]={
            "conditions":conditions,"allergies":allergies,"meds":meds,"emergency":emergency
        }
        st.success("保存しました")

# ---------------------------
# 救助者プロフィール
# ---------------------------
elif page=="救助者プロフィール":
    st.title("🦺 救助者プロフィール")
    role=st.selectbox("資格区分",["未申請","医師","看護師","救急救命士","応急手当講習修了"])
    status=st.selectbox("審査ステータス",["未申請","審査中","承認済み"])
    available=st.toggle("救助可能 ON/OFF")
    st.session_state.users[st.session_state.current_user]["available"]=available
    st.write("出動回数:", st.session_state.users[st.session_state.current_user]["dispatch_count"])
    st.write("到着回数:", st.session_state.users[st.session_state.current_user]["arrival_count"])

# ---------------------------
# HELP履歴
# ---------------------------
elif page=="HELP履歴":
    st.title("📜 HELP履歴")
    for event_id,event in st.session_state.help_events.items():
        st.write("日時:", event["createdAt"])
        st.write("状況:", event["situationType"])
        st.write("状態:", event["status"])
        st.write("出動者:", [st.session_state.users[r]["name"] for r in event["responders"]])
        st.divider()

# ---------------------------
# 設定
# ---------------------------
elif page=="設定":
    st.title("⚙ 設定")
    sound=st.toggle("通知音あり")
    st.session_state.users[st.session_state.current_user]["notificationSound"]=sound
    if st.button("免責を再表示"): show_disclaimer()
    st.subheader("🎬 デモモード")
    if st.button("疑似HELP発生"):
        event_id=create_help_event(st.session_state.current_user,"意識なし")
        st.success("デモHELPを発生させました")