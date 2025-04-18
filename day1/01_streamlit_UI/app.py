import streamlit as st

# ============================================
# タイトルと説明
# ============================================
st.title("インタラクティブな応答アプリ")
st.write("### テキストを入力すると、応答が返ってきます。")
st.markdown("このデモコードでは入力に関して決まった応答が返ってきます。あなたが入力したテキストにこんにちは、またはありがとうが含まれるときに応答が変わります。")

# ============================================
# ユーザー入力セクション
# ============================================
st.header("💬 ユーザー入力")

# テキスト入力
user_input = st.text_input("何か入力してください:", "")

# 応答を生成
if user_input:
    st.write("あなたが入力した内容:", user_input)
    if "こんにちは" in user_input:
        st.write("こんにちは！今日はどんなご用件ですか？ 😊")
    elif "ありがとう" in user_input:
        st.write("どういたしまして！お役に立てて嬉しいです。 🙌")
    else:
        st.write("入力ありがとうございます！他に何かありますか？")

# ============================================
# フッター
# ============================================
st.write("作成者: あなたの名前")