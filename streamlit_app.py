import streamlit as st
import time
import uuid
from datetime import datetime
import random

st.set_page_config(page_title="救急救命支援アプリ MVP", layout="wide")

# ---------------------------
# 初期データ（セッション保存）
# ---------------------------
if "users" not in st.session_state:
    st.session_state.users = {}
if "medical_profiles" not in st.session_state:
    st.session_state.medical_profiles = {}
if "qualifications" not in st.session_state:
    st.session_state.qualifications = {}
if "help_events" not in st.session_state:
    st.session_state.help_events = {}
if "responders" not in st.session_state:
    st.session_state.responders = []
if "aed_data" not in st.session_state:
    st.session_state.aed_data = [
        {"id": "1", "name": "駅前AED", "lat": 35.0, "lon": 139.0},
        {"id": "2", "name": "市役所AED", "lat": 35.001, "lon": 139.002},
    ]
if "current_user" not in st.session_state:
    user_id = str(uuid.uuid4())
    st.session_state.current_user = user_id
    st.session_state.users[user_id] = {
        "id": user_id,
        "role": "一般",
        "name": "テストユーザー",
        "location": {"lat": 35.0, "lon": 139.0},
        "notificationSound": True,
        "available": True,
        "score": 0,
        "dispatch_count": 0,
        "arrival_count": 0,
    }

# ---------------------------
# ユーティリティ
# ---------------------------
def show_disclaimer():
    st.warning("⚠ このアプリは医療行為を提供するものではありません。119通報を最優先してください。応急救護を支援する目的です。")

def distance_km(loc1, loc2):
    return round(random.uniform(0.1, 0.9), 2)  # MVPなのでダミー

def create_help_event(user_id, situation):
    event_id = str(uuid.uuid4())
    st.session_state.help_events[event_id] = {
        "id": event_id,
        "creatorUserId": user_id,
        "createdAt": datetime.now(),
        "location": st.session_state.users[user_id]["location"],
        "status": "発生",
        "situationType": situation,
        "responders": [],
    }
    return event_id

# ---------------------------
# サイドバー（画面遷移）
# ---------------------------
st.sidebar.title("メニュー")
page = st.sidebar.radio("画面選択", [
    "ホーム",
    "手順ガイド",
    "プロフィール",
    "救助者プロフィール",
    "HELP履歴",
    "設定"
])

# ---------------------------
# オンボーディング
# ---------------------------
if "onboarded" not in st.session_state:
    show_disclaimer()
    if st.button("同意して開始"):
        st.session_state.onboarded = True
        st.rerun()
    st.stop()

# ---------------------------
# ホーム画面
# ---------------------------
if page == "ホーム":
    st.title("🆘 救急救命支援")

    st.subheader("現在地")
    st.write("緯度:", st.session_state.users[st.session_state.current_user]["location"]["lat"])
    st.write("経度:", st.session_state.users[st.session_state.current_user]["location"]["lon"])

    situation = st.selectbox("状況を選択", [
        "意識なし",
        "呼吸が弱い・ない",
        "胸痛",
        "転倒・骨折疑い",
        "大出血",
        "けいれん",
        "その他"
    ])

    st.markdown("## ⛑ HELPボタン（3秒長押し）")

    if st.button("🆘 HELP 発動"):
        show_disclaimer()
        with st.spinner("3秒長押し中..."):
            time.sleep(3)

        event_id = create_help_event(st.session_state.current_user, situation)

        st.success("近隣の救助者へ通知しました！")
        cancel = st.button("5秒以内にキャンセル")

        time.sleep(2)

        if cancel:
            st.session_state.help_events[event_id]["status"] = "キャンセル"
            st.warning("HELPをキャンセルしました")
        else:
            st.info("119へ通報してください！")
            st.session_state.active_event = event_id

    # アクティブイベント表示
    if "active_event" in st.session_state:
        event = st.session_state.help_events[st.session_state.active_event]
        if event["status"] == "発生":
            st.subheader("🚑 現場マップ（簡易）")
            st.map([
                {
                    "lat": event["location"]["lat"],
                    "lon": event["location"]["lon"]
                }
            ])
            st.write("状況:", event["situationType"])

# ---------------------------
# 手順ガイド
# ---------------------------
elif page == "手順ガイド":
    st.title("📘 救命手順ガイド")

    st.subheader("胸骨圧迫")
    st.info("1. 胸の中央を強く速く押す\n2. 1分間に100-120回\n3. 中断しない")

    tempo = st.toggle("CPRテンポ音 ON/OFF")
    if tempo:
        st.success("♪ テンポ: 100-120 BPM")

    st.subheader("AEDの使い方")
    st.info("1. 電源ON\n2. パッド装着\n3. 音声指示に従う")

# ---------------------------
# プロフィール（患者側）
# ---------------------------
elif page == "プロフィール":
    st.title("🧾 医療情報")

    conditions = st.text_input("持病")
    allergies = st.text_input("アレルギー")
    meds = st.text_input("服薬")
    emergency = st.text_input("緊急連絡先")

    if st.button("保存"):
        st.session_state.medical_profiles[st.session_state.current_user] = {
            "conditions": conditions,
            "allergies": allergies,
            "meds": meds,
            "emergency": emergency
        }
        st.success("保存しました")

# ---------------------------
# 救助者プロフィール
# ---------------------------
elif page == "救助者プロフィール":
    st.title("🦺 救助者プロフィール")

    role = st.selectbox("資格区分", [
        "未申請",
        "医師",
        "看護師",
        "救急救命士",
        "応急手当講習修了"
    ])

    status = st.selectbox("審査ステータス", [
        "未申請",
        "審査中",
        "承認済み"
    ])

    available = st.toggle("救助可能 ON/OFF")

    st.session_state.users[st.session_state.current_user]["available"] = available

    st.write("出動回数:", st.session_state.users[st.session_state.current_user]["dispatch_count"])
    st.write("到着回数:", st.session_state.users[st.session_state.current_user]["arrival_count"])

# ---------------------------
# HELP履歴
# ---------------------------
elif page == "HELP履歴":
    st.title("📜 HELP履歴")

    for event_id, event in st.session_state.help_events.items():
        st.write("日時:", event["createdAt"])
        st.write("状況:", event["situationType"])
        st.write("状態:", event["status"])
        st.divider()

# ---------------------------
# 設定
# ---------------------------
elif page == "設定":
    st.title("⚙ 設定")

    sound = st.toggle("通知音あり")
    st.session_state.users[st.session_state.current_user]["notificationSound"] = sound

    if st.button("免責を再表示"):
        show_disclaimer()

    st.subheader("🎬 デモモード")
    if st.button("疑似HELP発生"):
        event_id = create_help_event(st.session_state.current_user, "意識なし")
        st.success("デモHELPを発生させました")