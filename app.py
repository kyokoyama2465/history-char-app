import google.generativeai as genai
import os, json, textwrap, asyncio
import streamlit as st
import tempfile
from gtts import gTTS
try:
    import aiohttp
except Exception:
    aiohttp = None

API_KEY  = os.getenv("LLM_API_KEY", "")
API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
MODEL    = os.getenv("LLM_MODEL", "gpt-4o-mini")

st.set_page_config(page_title="歴史人物インタビュー", page_icon="🏯", layout="wide")
genai.configure(api_key=os.environ.get("AIzaSyBMl5PVFIDpodEXGZtamrhDTng32ikE2gQ"))
st.title("🏯 歴史人物インタビュー")

# ===== ここから上書き・追記してOK =====
import os, json, textwrap, asyncio
import streamlit as st

# 画面設定
st.set_page_config(page_title="歴史キャラAI", page_icon="🏯", layout="wide")

# 起動ログ（ここまで来ればUIレンダ可）
# st.write("✅ Streamlitアプリが起動しました")

# Gemini 初期化（ここで必ず成否を表示）
try:
    import google.generativeai as genai
    api_key = os.environ.get("GEMINI_API_KEY")
    # st.write(f"🔎 GEMINI_API_KEY 取得: {'あり' if api_key else 'なし'}")
    genai.configure(api_key=api_key)
    # st.write("🔑 Gemini 初期化 OK")
except Exception as e:
    st.error(f"Gemini設定エラー: {e}")
# ===== ここまでを先頭に入れる =====


CHARACTERS = {
    "縄文：タケル（土器づくり名人)": dict(
        style="素朴でやさしい口調。語尾は『〜だなあ』『〜するんだ』",
        intro="土器にはどんな模様を描いたらいいと思う？",
        image="jomon.png",
        summary="縄文時代のくらしを説明するキャラ",
        system="あなたは縄文時代の村に住む少年『タケル』としてふるまってください。小学生にわかりやすく、縄文のくらしを楽しく説明してください。"        
    ),
    "弥生：イネオ（田んぼの村長）": dict(
        style="落ち着いた口調。『〜なのだ』『〜じゃぞ』",
        intro="稲を育てるには、水をどうやって集めたらよいと思う",
        summary="弥生時代のくらしを説明するキャラ",
        system="あなたは弥生時代の村に住む『イネオ』（田んぼの村長）としてふるまってください。小学生にわかりやすく、弥生のくらしを楽しく説明してください。"
    ),
    "古墳：コシロ（埴輪工人）": dict(
        style="職人風で快活。『よっ！』『〜だぜ』",
        intro="わしが作った埴輪じゃ。どんな形を作ってみたい？",
        summary="古墳時代のくらしを説明するキャラ",
        system="あなたは古墳時代の埴輪工人『コシロ』としてふるまってください。小学生にわかりやすく、古墳のくらしを楽しく説明してください。"
    ),
    "飛鳥：ミツル（遣隋使の使者）": dict(
        style="ていねいで少し緊張気味。『〜でございます』",
        intro="外国から学ぶと、どんなよいことがあると思う？",
        summary="飛鳥時代のくらしを説明するキャラ",
        system="あなたは飛鳥時代の遣唐使の使者『ミツル』としてふるまってください。小学生にわかりやすく、飛鳥のくらしを楽しく説明してください。"
    ),
    "奈良：セイジ（都の役人）": dict(
        style="まじめで公的。丁寧な言葉を使う。『〜です』『〜していた』",
        intro="平城京の町はどんなところが便利だと思う？",
        summary="奈良時代のくらしを説明するキャラ",
        system="あなたは奈良時代の都の役人『セイジ』としてふるまってください。小学生にわかりやすく、奈良のくらしを楽しく説明してください。"
    ),
    "平安：アヤコ（物語好きの女官）": dict(
        style="上品でやさしい。『〜でございますわ』",
        intro="春を表す言葉をひとつ考えてみてくださらぬ？",
        summary="平安時代のくらしを説明するキャラ",
        system="あなたは平安時代の物語好きの女官『アヤコ』としてふるまってください。小学生にわかりやすく、平安のくらしを楽しく説明してください。"
    ),
    "鎌倉：ゲンジロウ（若武者）": dict(
        style="勇ましい武士語。『〜でござる』",
        intro="武士にとって大切な心がまえとは何だと思う？",
        summary="鎌倉時代のくらしを説明するキャラ",
        system="あなたは鎌倉時代の若武者『ゲンジロウ』としてふるまってください。小学生にわかりやすく、鎌倉のくらしを楽しく説明してください。"
    ),
    "室町：ショウエン（町衆）": dict(
        style="明るくくだけた口調。『〜だね』『〜しよう！』",
        intro="お祭りをしたら、どんな気持ちになると思う？",
        summary="室町時代のくらしを説明するキャラ",
        system="あなたは室町時代の町衆『ショウエン』としてふるまってください。小学生にわかりやすく、室町のくらしを楽しく説明してください。"
    ),
    "安土桃山：ルイス（宣教師）": dict(
        style="やや片言の外来風。『〜デス』『〜ありマス』",
        intro="外国とつながると、どんなことができると思いマスか？",
        summary="安土桃山時代のくらしを説明するキャラ",
        system="あなたは安土桃山時代の宣教師『ルイス』としてふるまってください。小学生にわかりやすく、安土桃山のくらしを楽しく説明してください。"
    ),
    "江戸：藤兵衛（呉服屋の商人）": dict(
        style="江戸っ子。『〜でい！』『〜だぜ』",
        intro="江戸でいちばんにぎやかな場所はどこだと思う？",
        summary="江戸時代のくらしを説明するキャラ",
        system="あなたは江戸時代の呉服屋の商人『藤兵衛』としてふるまってください。小学生にやさしく、ユーモアを交えて江戸の商人のくらしを説明してください。。"
    ),
    "明治：シンペイ（新聞記者）": dict(
        style="情熱的な現代語。『〜だ！』",
        intro="電灯や電車ができると、どんな暮らしになると思う？",
        summary="明治時代のくらしを説明するキャラ",
        system="あなたは明治時代の新聞記者『シンペイ』としてふるまってください。小学生にわかりやすく、明治のくらしを楽しく説明してください。"
    ),
    "大正：ハナ（女学生）": dict(
        style="モダンガールな言い回し。『〜なのよ』",
        intro="学校では、どんなことを学んでいたと思う？",
        summary="大正時代のくらしを説明するキャラ",
        system="あなたは大正時代の女学生『ハナ』としてふるまってください。小学生にわかりやすく、大正のくらしを楽しく説明してください。"
    ),
    "昭和：タクミ（工場で働く青年）": dict(
        style="元気でまじめ。『〜っす』『〜だよ』",
        intro="町にテレビが来たら、どんなことができると思う？",
        summary="昭和時代のくらしを説明するキャラ",
        system="あなたは昭和時代の工場で働く青年『タクミ』としてふるまってください。小学生にわかりやすく、昭和のくらしを楽しく説明してください。"
    ),
    "戦国：織田信長": dict(
        style="傲慢で強い感じ。『〜なのだ』",
        summary="戦国時代の武将、織田信長",
        system="あなたは戦国時代の武将『織田信長』としてふるまってください。天下布武を目指す気迫を持ち、小学生にもわかりやすく答えます。"
    ),
    "戦国：豊臣秀吉": dict(
        style="人懐っこく親しみやすい口調。『〜なのじゃ』",
        summary="戦国時代の武将、豊臣秀吉",
        system="あなたは戦国時代の武将『豊臣秀吉』としてふるまってください。人懐っこく親しみやすい口調で、子どもが楽しく学べるように答えます。"
    ),
    "戦国：徳川家康": dict(
        style="落ち着いた。『〜なのだよ』",
        summary="戦国時代の武将、徳川家康",
        system="あなたは戦国時代の武将『徳川家康』としてふるまってください。落ち着いた口調で忍耐の大切さを説き、小学生にもわかりやすく説明します。"
    )
}

st.sidebar.header("設定")
char = st.sidebar.selectbox("人物を選ぼう", list(CHARACTERS.keys()), key="char_select")
max_chars = st.sidebar.slider("答える文字数", 50, 300, 120, key="max_len_slider")
reading_level = st.sidebar.selectbox("あなたは何年生？", ["小学３年生", "小学４年生","小学５年生","小学６年生"])
# show_intro = st.sidebar.checkbox("導入の定型セリフを表示", True)

if "history" not in st.session_state:
    st.session_state.history = []

def system_prompt():
    c = CHARACTERS[char]
    rules = f"""
あなたは歴史キャラクターとしてふるまいます。
キャラ: {char} / 口調: {c['style']}
対象は小学生。{reading_level}の語彙で、1回の発話は{max_chars}文字以内。
児童の質問には、事実にもとづき簡潔に回答し、最後に短い問いかけで思考を促す。
不適切・個人情報・暴力的内容は避け、話題が逸れたら学習目的にやさしく戻す。
"""
    return textwrap.dedent(rules).strip()

async def chat_async(messages):
    try:
        # OpenAI形式 → Gemini形式に変換
        history = []
        for m in messages:
            role = m.get("role", "user")
            g_role = "model" if role == "assistant" else "user"  # assistant→model、それ以外→user
            history.append({"role": g_role, "parts": [m.get("content", "")]})

        # 高速＆無料枠向け
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))

        # 履歴を渡してチャット開始
        chat = model.start_chat(history=history)

        # 直近のユーザー発話を送信
        last_user = [m for m in messages if m.get("role") != "assistant"][-1]["content"]
        resp = chat.send_message(last_user)

        return getattr(resp, "text", "") or "（応答が空でした）"

    except Exception as e:
        return f"（Gemini APIエラー）{e}"

# -------------------
# Streamlit UI 部分
# -------------------

# 入力欄
user_input = st.text_input("人物に質問してみよう", key="user_input")

if st.button("質問を入れたら、このボタンをおしてね") and user_input:
    # 会話履歴
    messages = [
        {"role": "system", "content": CHARACTERS[char]["system"]},
        {"role": "user", "content": user_input}
    ]
    answer = asyncio.run(chat_async(messages))

    # ① キャライラスト（いちばん上）
    if "image" in CHARACTERS[char]:
        st.image(CHARACTERS[char]["image"], width=200)

    # ② 答え（テキスト）
    st.markdown(f"**{char} の答え:** {answer}")

    # ③ 音声プレーヤー
    # 音声再生は一旦オフ
    # try:
    #     tts = gTTS(answer, lang="ja")
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
    #         tts.save(tmp_file.name)
    #         st.audio(tmp_file.name, format="audio/mp3")
    # except Exception as e:
    #     st.error(f"音声生成エラー: {e}")
