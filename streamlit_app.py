import streamlit as st
import time
import uuid
from datetime import datetime
import pydeck as pdk
import math
import random
from streamlit_js_eval import get_geolocation  # ← ここを追加

st.set_page_config(page_title="救急救命支援アプリ MVP", layout="wide")

# ---------------------------
# 位置情報取得（Streamlit Cloud対応）
# ---------------------------
def update_location():
    loc = get_geolocation()

    if loc and "coords" in loc:
        lat = loc["coords"]["latitude"]
        lon = loc["coords"]["longitude"]

        if "current_user" in st.session_state:
            st.session_state.users[st.session_state.current_user]["location"] = {
                "lat": lat,
                "lon": lon
            }

        st.success(f"現在地取得: {lat}, {lon}")
    else:
        st.warning("位置情報を取得できませんでした（ブラウザで許可してください）")

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
# テストユーザー（Requester）
# ---------------------------
if "current_user" not in st.session_state:
    user_id = str(uuid.uuid4())
    st.session_state.current_user = user_id
    st.session_state.users[user_id] = {
        "id": user_id,
        "role": "一般",
        "name": "テストユーザー",
        "location": {"lat": 35.564311, "lon": 139.715093},
        "notificationSound": True,
        "available": True,
        "score": 0,
        "dispatch_count": 0,
        "arrival_count": 0,
    }

# テストユーザー（Responder）
if len(st.session_state.users) == 1:
    user_id = str(uuid.uuid4())
    st.session_state.users[user_id] = {
        "id": user_id,
        "role": "救助者",
        "name": "救助者テスト",
        "location": {"lat": 35.6825, "lon": 139.7690},
        "notificationSound": True,
        "available": True,
        "score": 0,
        "dispatch_count": 0,
        "arrival_count": 0,
    }

# 🔥 ここで現在地を更新
update_location()

# ---------------------------
# ユーティリティ関数
# ---------------------------
def show_disclaimer():
    st.warning("⚠ このアプリは医療行為を提供するものではありません。119通報を最優先してください。応急救護を支援する目的です。")

def distance_km(loc1, loc2):
    # MVP用ダミー（実際はハバーサイン計算可能）
    return round(random.uniform(0.1, 0.9), 3)

# ---------------------------
# HELPイベント作成と通知
# ---------------------------
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
        if user["role"] == "救助者" and user["available"]:
            st.session_state.responders_notified.append({
                "userId": user_id,
                "eventId": event_id,
                "notifiedAt": datetime.now()
            })

# ---------------------------
# 以降、あなたの元コードと同じ
# ---------------------------

# 下部ナビゲーション、ページ切替、ホーム画面、手順ガイド、
# プロフィール、救助者プロフィール、HELP履歴、設定
# 元のコードをそのまま残す