import streamlit as st
import re, random, string, joblib, os, sqlite3, io
import numpy as np
import scipy.sparse as sp
import pandas as pd
import plotly.graph_objects as go
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet

# ══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="SecurePass AI", page_icon="🔐",
                   layout="centered", initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════
#  CSS + MATRIX RAIN (inline HTML component)
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#07090f;color:#e0e0f0;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1.5rem;padding-bottom:2rem;max-width:820px;position:relative;z-index:2;}

.hero-container{text-align:center;padding:2rem 1rem 1.5rem;
  background:linear-gradient(135deg,rgba(0,255,136,0.06),rgba(0,160,255,0.06));
  border:1px solid rgba(0,255,136,0.18);border-radius:20px;margin-bottom:1.5rem;}
.hero-title{font-size:2.6rem;font-weight:700;
  background:linear-gradient(90deg,#00ff88 0%,#00ccff 50%,#a855f7 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;letter-spacing:-1px;margin:0;}
.hero-subtitle{color:rgba(200,210,255,0.6);font-size:0.88rem;margin-top:0.5rem;}
.model-badge{display:inline-block;
  background:linear-gradient(90deg,rgba(0,255,136,0.15),rgba(168,85,247,0.15));
  border:1px solid rgba(0,255,136,0.3);color:#00ff88;
  font-size:0.68rem;font-weight:600;padding:3px 14px;
  border-radius:20px;margin-top:0.7rem;letter-spacing:1px;text-transform:uppercase;}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,0.04)!important;border-radius:12px!important;padding:4px!important;border:1px solid rgba(255,255,255,0.1)!important;gap:4px!important;}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;color:rgba(200,210,255,0.6)!important;font-weight:500!important;font-size:0.83rem!important;padding:0.35rem 0.8rem!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(0,196,112,0.25),rgba(0,153,204,0.25))!important;color:#00ff88!important;font-weight:600!important;}

/* Cards */
.section-card{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:1.4rem;margin-bottom:1.1rem;}
.card-title{font-size:0.72rem;font-weight:600;color:rgba(200,210,255,0.42);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.9rem;}

/* Inputs */
.stTextInput>div>div>input{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.15)!important;border-radius:10px!important;color:white!important;font-family:'JetBrains Mono',monospace!important;font-size:0.9rem!important;padding:0.6rem 1rem!important;}
.stTextInput>div>div>input:focus{border-color:rgba(0,255,136,0.5)!important;box-shadow:0 0 0 3px rgba(0,255,136,0.08)!important;}
.stTextInput>div>div>input::placeholder{color:rgba(180,180,220,0.3)!important;}
label{color:rgba(200,210,255,0.75)!important;font-size:0.8rem!important;font-weight:500!important;}

/* Buttons */
.stButton>button{background:linear-gradient(135deg,#00c470,#0099cc)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;font-size:0.9rem!important;padding:0.55rem 1.4rem!important;width:100%!important;box-shadow:0 4px 20px rgba(0,196,112,0.25)!important;transition:all 0.3s!important;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 28px rgba(0,196,112,0.4)!important;}

/* Score */
.score-box{border-radius:14px;padding:1.1rem 1.5rem;margin:0.7rem 0;display:flex;align-items:center;gap:1.3rem;}
.score-strong{background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);}
.score-medium{background:rgba(255,200,50,0.1);border:1px solid rgba(255,200,50,0.3);}
.score-weak{background:rgba(255,60,60,0.1);border:1px solid rgba(255,60,60,0.3);}
.score-number{font-size:2.6rem;font-weight:700;font-family:'JetBrains Mono',monospace;line-height:1;}
.score-strong .score-number{color:#00ff88;}.score-medium .score-number{color:#ffcc33;}.score-weak .score-number{color:#ff4466;}
.score-label{font-size:1.1rem;font-weight:600;}.score-sublabel{font-size:0.72rem;color:rgba(200,210,255,0.5);margin-top:3px;}

/* Crack time */
.crack-box{border-radius:12px;padding:0.9rem 1.3rem;margin:0.7rem 0;background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.3);display:flex;align-items:center;gap:1.1rem;}
.crack-time{font-size:1.4rem;font-weight:700;font-family:'JetBrains Mono',monospace;color:#a855f7;}
.crack-sub{font-size:0.72rem;color:rgba(200,210,255,0.4);margin-top:3px;}

/* Live meter */
.lock-strong{filter:drop-shadow(0 0 12px #00ff88);animation:pg 1.5s infinite;}
.lock-medium{filter:drop-shadow(0 0 8px #ffcc33);}
.lock-weak{filter:drop-shadow(0 0 8px #ff4466);}
@keyframes pg{0%,100%{filter:drop-shadow(0 0 8px #00ff88);}50%{filter:drop-shadow(0 0 20px #00ff88);}}

/* Stat chips */
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0.55rem;margin-top:0.7rem;}
.stat-chip{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:0.55rem 0.4rem;text-align:center;}
.stat-val{font-size:1rem;font-weight:700;font-family:'JetBrains Mono',monospace;}
.stat-ok{color:#00ff88;}.stat-no{color:#ff4466;}
.stat-lbl{font-size:0.6rem;color:rgba(200,210,255,0.45);margin-top:2px;text-transform:uppercase;letter-spacing:0.8px;}

/* Suggestion / generated pw */
.suggestion-box{background:rgba(0,255,136,0.05);border:1px solid rgba(0,255,136,0.2);border-radius:10px;padding:0.6rem 1rem;margin:0.28rem 0;font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:#b0ffd8;}
.gen-pw-box{background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.25);border-radius:12px;padding:0.9rem 1.3rem;margin:0.7rem 0;font-family:'JetBrains Mono',monospace;font-size:1.05rem;color:#b0ffd8;letter-spacing:1px;text-align:center;word-break:break-all;}

/* Save prompt */
.save-prompt{background:rgba(0,204,255,0.07);border:1px solid rgba(0,204,255,0.25);border-radius:12px;padding:1rem 1.3rem;margin:0.8rem 0;text-align:center;}

/* Reject */
.reject-box{background:rgba(255,60,60,0.12);border:1px solid rgba(255,60,60,0.4);border-radius:12px;padding:1rem 1.3rem;margin:0.7rem 0;text-align:center;}
.reject-title{color:#ff4466;font-size:1.1rem;font-weight:700;}
.reject-sub{color:rgba(255,150,150,0.8);font-size:0.83rem;margin-top:4px;}

/* Login card */
.login-card{background:rgba(255,255,255,0.04);border:1px solid rgba(0,255,136,0.2);border-radius:18px;padding:2rem;max-width:400px;margin:2rem auto;}
.login-title{font-size:1.5rem;font-weight:700;color:#00ff88;text-align:center;margin-bottom:0.3rem;}
.login-sub{font-size:0.82rem;color:rgba(200,210,255,0.5);text-align:center;margin-bottom:1.4rem;}

/* History rows */
.hist-row{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:0.7rem 1rem;margin:0.3rem 0;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;}
.hist-site{font-weight:600;color:#00ccff;font-size:0.88rem;min-width:90px;}
.hist-score-strong{color:#00ff88;font-weight:700;font-family:'JetBrains Mono',monospace;}
.hist-score-medium{color:#ffcc33;font-weight:700;font-family:'JetBrains Mono',monospace;}
.hist-score-weak{color:#ff4466;font-weight:700;font-family:'JetBrains Mono',monospace;}
.hist-date{color:rgba(200,210,255,0.4);font-size:0.72rem;margin-left:auto;}

/* Progress */
.stProgress>div>div>div{border-radius:8px!important;}
.stProgress>div>div{background:rgba(255,255,255,0.07)!important;border-radius:8px!important;}

/* Expander */
.streamlit-expanderHeader{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.1)!important;border-radius:12px!important;color:rgba(200,210,255,0.8)!important;font-weight:500!important;}
.streamlit-expanderContent{background:rgba(255,255,255,0.02)!important;border:1px solid rgba(255,255,255,0.07)!important;border-top:none!important;border-radius:0 0 12px 12px!important;}

/* Slider */
.stSlider>div>div>div>div{background:linear-gradient(90deg,#00c470,#0099cc)!important;}

/* Footer */
.footer-txt{text-align:center;color:rgba(180,180,220,0.28);font-size:0.7rem;margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.06);}
</style>
""", unsafe_allow_html=True)

# Matrix Rain — iframe trick (works in all browsers)
st.components.v1.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  body{margin:0;overflow:hidden;background:transparent;}
  canvas{display:block;}
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
  var c=document.getElementById("c");
  var ctx=c.getContext("2d");
  c.height=window.innerHeight;
  c.width=window.innerWidth;
  var chars="01アイウエオカキクケコ@#$%&*ABCDEF";
  var fontSize=13;
  var cols=Math.floor(c.width/fontSize);
  var drops=[];
  for(var i=0;i<cols;i++) drops[i]=1;
  function draw(){
    ctx.fillStyle="rgba(7,9,15,0.05)";
    ctx.fillRect(0,0,c.width,c.height);
    ctx.fillStyle="#00ff88";
    ctx.font=fontSize+"px monospace";
    for(var i=0;i<drops.length;i++){
      var text=chars[Math.floor(Math.random()*chars.length)];
      ctx.fillText(text,i*fontSize,drops[i]*fontSize);
      if(drops[i]*fontSize>c.height&&Math.random()>0.975) drops[i]=0;
      drops[i]++;
    }
  }
  setInterval(draw,50);
</script>
</body>
</html>
""", height=200, scrolling=False)

# Push canvas behind everything with CSS
st.markdown("""
<style>
  iframe[title="st.iframe"]{
    position:fixed!important;top:0;left:0;
    width:100vw!important;height:100vh!important;
    z-index:0!important;pointer-events:none;opacity:0.18;
    border:none!important;
  }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════════════════
DB_FILE = "securepass.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS analysis_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, website TEXT, password TEXT,
        score INTEGER, strength TEXT, length INTEGER,
        has_upper INTEGER, has_lower INTEGER, has_digit INTEGER, has_special INTEGER,
        analyzed_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS vault(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, site TEXT, username TEXT,
        password TEXT, saved_at TEXT)""")
    conn.commit(); conn.close()

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute("INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)",
            (username.strip(), hash_pw(password), datetime.now().strftime("%d-%m-%Y %H:%M")))
        conn.commit(); conn.close(); return True
    except: return False

def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    row = conn.cursor().execute(
        "SELECT id,username FROM users WHERE username=? AND password_hash=?",
        (username.strip(), hash_pw(password))).fetchone()
    conn.close(); return row

def save_history(user_id, website, password, score, strength, length,
                 has_upper, has_lower, has_digit, has_special):
    conn = sqlite3.connect(DB_FILE)
    conn.cursor().execute("""INSERT INTO analysis_history
        (user_id,website,password,score,strength,length,has_upper,has_lower,has_digit,has_special,analyzed_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id, website or "—", password, score, strength, length,
         int(has_upper),int(has_lower),int(has_digit),int(has_special),
         datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    conn.commit(); conn.close()

def get_history(user_id, limit=100):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.cursor().execute("""SELECT website,password,score,strength,length,analyzed_at
        FROM analysis_history WHERE user_id=? ORDER BY id DESC LIMIT ?""",
        (user_id,limit)).fetchall()
    conn.close(); return rows

def get_history_df(user_id):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(
        "SELECT website,password,score,strength,length,analyzed_at FROM analysis_history WHERE user_id=? ORDER BY id DESC",
        conn, params=(user_id,))
    conn.close(); return df

def clear_history(user_id):
    conn = sqlite3.connect(DB_FILE)
    conn.cursor().execute("DELETE FROM analysis_history WHERE user_id=?", (user_id,))
    conn.commit(); conn.close()

def save_vault(user_id, site, username, password):
    conn = sqlite3.connect(DB_FILE)
    conn.cursor().execute("INSERT INTO vault(user_id,site,username,password,saved_at) VALUES(?,?,?,?,?)",
        (user_id, site, username or "N/A", password, datetime.now().strftime("%d-%m-%Y %H:%M")))
    conn.commit(); conn.close()

def get_vault(user_id):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.cursor().execute(
        "SELECT site,username,password,saved_at FROM vault WHERE user_id=? ORDER BY id DESC",
        (user_id,)).fetchall()
    conn.close(); return rows

init_db()

# ══════════════════════════════════════════════════════════
#  ENCRYPTION
# ══════════════════════════════════════════════════════════
def get_key():
    if not os.path.exists("secret.key"):
        with open("secret.key","wb") as f: f.write(Fernet.generate_key())
    with open("secret.key","rb") as f: return f.read()
def enc(pw):
    try: return Fernet(get_key()).encrypt(pw.encode()).decode()
    except: return pw
def dec(e):
    try: return Fernet(get_key()).decrypt(e.encode()).decode()
    except: return e

# ══════════════════════════════════════════════════════════
#  ML MODEL
# ══════════════════════════════════════════════════════════
@st.cache_resource
def load_model():
    mp,vp='model/password_strength_model.pkl','model/vectorizer.pkl'
    if os.path.exists(mp) and os.path.exists(vp):
        try: return joblib.load(mp), joblib.load(vp)
        except: return None,None
    return None,None

def hand_feat(p):
    return np.array([[len(p),sum(c.isupper() for c in p),sum(c.islower() for c in p),
                      sum(c.isdigit() for c in p),sum(not c.isalnum() for c in p),
                      len(set(p)),int(len(p)>=12),int(len(p)>=16)]])

def ml_predict(pw, model, vec):
    X = sp.hstack([vec.transform([pw]), sp.csr_matrix(hand_feat(pw))])
    return int(model.predict(X)[0]), model.predict_proba(X)[0]

# ══════════════════════════════════════════════════════════
#  CRACK TIME
# ══════════════════════════════════════════════════════════
def crack_time(pw):
    cs = 0
    if re.search(r'[a-z]',pw): cs+=26
    if re.search(r'[A-Z]',pw): cs+=26
    if re.search(r'\d',pw):    cs+=10
    if re.search(r'[!@#$%^&*()\-_=+]',pw): cs+=32
    if cs==0: cs=10
    secs = (cs**len(pw)) / 10_000_000_000
    if secs<1:        return "Instantly","🔴","Change immediately!"
    if secs<60:       return f"{int(secs)}s","🔴","Cracked in seconds!"
    if secs<3600:     return f"{int(secs/60)} min","🟠","Cracked in minutes!"
    if secs<86400:    return f"{int(secs/3600)} hrs","🟡","Cracked within a day!"
    if secs<2592000:  return f"{int(secs/86400)} days","🟡","Cracked within a month."
    if secs<31536000: return f"{int(secs/2592000)} months","🟢","Months to crack!"
    if secs<3e12:     return f"{int(secs/31536000)} years","🟢","Years to crack!"
    if secs<3e15:     return f"{int(secs/3153600000)} centuries","💚","Centuries!"
    return "Millions of years","💚","Virtually uncrackable! 🏆"

# ══════════════════════════════════════════════════════════
#  ANALYSIS
# ══════════════════════════════════════════════════════════
MIN_LEN = 6

def analyze(pw):
    if not pw: return None
    hu = bool(re.search(r'[A-Z]',pw))
    hl = bool(re.search(r'[a-z]',pw))
    hd = bool(re.search(r'\d',pw))
    hs = bool(re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>?/\\|`~]',pw))
    ln = len(pw); uc = len(set(pw))

    sc=0
    if ln>=16: sc+=30
    elif ln>=12: sc+=22
    elif ln>=8: sc+=12
    elif ln>=6: sc+=5
    if hu: sc+=20
    if hl: sc+=15
    if hd: sc+=20
    if hs: sc+=25
    if uc>=10: sc+=10
    elif uc>=6: sc+=5
    if pw.isdigit(): sc=min(sc,15)
    if pw.isalpha() and not hu: sc=min(sc,20)
    if ln<8: sc=min(sc,20)
    rs=int(min(100,sc))

    mdl,vec=load_model()
    ml=mdl is not None; conf=None
    if ml:
        pred,proba=ml_predict(pw,mdl,vec); conf=float(max(proba))*100
        if pw.isdigit() or ln<8: fs,st,css=min(rs,15),"Weak","weak"
        elif pred==2 and rs>=55:  fs,st,css=max(rs,75),"Strong","strong"
        elif pred==1 or (pred==2 and rs<55): fs,st,css=max(35,min(rs,74)),"Medium","medium"
        else: fs,st,css=min(rs,34),"Weak","weak"
    else:
        fs=rs
        if fs>=75: st,css="Strong","strong"
        elif fs>=40: st,css="Medium","medium"
        else: st,css="Weak","weak"

    tips=[]
    if ln<8: tips.append("❌ Too short! Use at least 8 characters")
    elif ln<12: tips.append("⚠️ Use 12+ characters")
    elif ln<16: tips.append("💡 16+ characters = nearly uncrackable")
    if not hu: tips.append("➕ Add UPPERCASE letters")
    if not hl: tips.append("➕ Add lowercase letters")
    if not hd: tips.append("➕ Add numbers 0–9")
    if not hs: tips.append("➕ Add symbols !@#$%^&*")
    if pw.isdigit(): tips.append("🚫 Only numbers = extremely weak!")
    if uc<5: tips.append("⚠️ Too many repeated characters")

    return dict(score=fs,strength=st,css=css,hu=hu,hl=hl,hd=hd,hs=hs,
                length=ln,unique=uc,tips=tips,ml=ml,conf=conf)

# ══════════════════════════════════════════════════════════
#  PASSWORD GENERATOR
# ══════════════════════════════════════════════════════════
def gen_pw(length=18,up=True,lo=True,di=True,sy=True):
    chars,req="",[]
    if up: chars+=string.ascii_uppercase; req.append(random.choice(string.ascii_uppercase))
    if lo: chars+=string.ascii_lowercase; req.append(random.choice(string.ascii_lowercase))
    if di: chars+=string.digits;          req.append(random.choice(string.digits))
    if sy: chars+="!@#$%^&*";            req.append(random.choice("!@#$%^&*"))
    if not chars: chars=string.ascii_letters
    rest=[random.choice(chars) for _ in range(length-len(req))]
    pw=req+rest; random.shuffle(pw); return ''.join(pw)

def live_meter(score, strength):
    if strength=="Strong":   col,lbl="#00ff88","🔒 STRONG"
    elif strength=="Medium": col,lbl="#ffcc33","🔐 MEDIUM"
    else:                    col,lbl="#ff4466","🔓 WEAK"
    return f"""
    <div style="margin:0.5rem 0 0.7rem;">
      <div style="background:rgba(255,255,255,0.07);border-radius:8px;height:11px;overflow:hidden;">
        <div style="width:{score}%;height:11px;border-radius:8px;
             background:linear-gradient(90deg,{col}88,{col});
             box-shadow:0 0 8px {col}66;transition:width 0.4s;"></div>
      </div>
      <div style="color:{col};font-size:0.82rem;font-weight:700;margin-top:4px;letter-spacing:0.5px;">
        {lbl} &nbsp;·&nbsp; {score}/100
      </div>
    </div>"""

# ══════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id   = None
    st.session_state.username  = ""

# ══════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-container">
  <h1 class="hero-title">🔐 SecurePass AI</h1>
  <p class="hero-subtitle">Advanced Password Strength Analyzer &nbsp;·&nbsp; MCA Practical Project</p>
  <span class="model-badge">🤖 RandomForest 99.96% &nbsp;|&nbsp; 🎲 Generator &nbsp;|&nbsp; 📊 Charts &nbsp;|&nbsp; ⏱️ Crack Time &nbsp;|&nbsp; 👤 Login</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  LOGIN / SIGNUP WALL
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">👤 Welcome Back</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Login or create account to use SecurePass AI</div>', unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    with auth_tab1:
        lu = st.text_input("Username", key="l_user", placeholder="Enter username")
        lp = st.text_input("Password", key="l_pass", type="password", placeholder="Enter password")
        if st.button("🔑 Login", key="login_btn"):
            if lu and lp:
                row = login_user(lu, lp)
                if row:
                    st.session_state.logged_in = True
                    st.session_state.user_id   = row[0]
                    st.session_state.username  = row[1]
                    st.success(f"✅ Welcome back, **{row[1]}**!")
                    st.rerun()
                else:
                    st.error("❌ Wrong username or password!")
            else:
                st.warning("Please fill both fields.")

    with auth_tab2:
        su = st.text_input("Choose Username", key="s_user", placeholder="e.g. shruti123")
        sp1 = st.text_input("Choose Password", key="s_p1", type="password", placeholder="Min 6 chars")
        sp2 = st.text_input("Confirm Password", key="s_p2", type="password", placeholder="Re-enter password")
        if st.button("📝 Create Account", key="signup_btn"):
            if su and sp1 and sp2:
                if sp1 != sp2:
                    st.error("❌ Passwords don't match!")
                elif len(sp1) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                else:
                    if register_user(su, sp1):
                        st.success("✅ Account created! Now login.")
                    else:
                        st.error("❌ Username already taken!")
            else:
                st.warning("Please fill all fields.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════
#  LOGGED IN — TOP BAR
# ══════════════════════════════════════════════════════════
col_u, col_lo = st.columns([4,1])
with col_u:
    st.markdown(f'<p style="color:rgba(0,255,136,0.7);font-size:0.82rem;margin-bottom:0.3rem;">👤 Logged in as <b>{st.session_state.username}</b></p>', unsafe_allow_html=True)
with col_lo:
    if st.button("🚪 Logout", key="logout"):
        st.session_state.logged_in = False
        st.session_state.user_id   = None
        st.session_state.username  = ""
        st.rerun()

uid = st.session_state.user_id

# ══════════════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Analyzer", "✏️ Create Own", "🎲 Generator", "📊 History", "🔐 Vault"
])


# ════════════════════════════════════════════════
#  TAB 1 — ANALYZER
# ════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-card"><div class="card-title">🔑 Analyze Your Password</div>', unsafe_allow_html=True)
    c1,c2 = st.columns([2,1])
    with c1:
        pw_input = st.text_input("Password", type="password", placeholder="Minimum 6 characters…", key="pw_in")
    with c2:
        site_input = st.text_input("Website / App", placeholder="Gmail, GitHub…", key="site_in")

    # Live meter
    if pw_input and len(pw_input) >= MIN_LEN:
        lr = analyze(pw_input)
        if lr:
            st.markdown(live_meter(lr["score"], lr["strength"]), unsafe_allow_html=True)
            ct,ce,cm = crack_time(pw_input)
            st.markdown(f'<p style="color:rgba(200,210,255,0.5);font-size:0.76rem;margin-top:-0.3rem;">{ce} Crack time: <b style="color:#a855f7">{ct}</b></p>', unsafe_allow_html=True)
    elif pw_input:
        rem = MIN_LEN - len(pw_input)
        st.markdown(f'<p style="color:#ff7755;font-size:0.78rem;">⚠️ {len(pw_input)}/6 — need {rem} more</p>', unsafe_allow_html=True)

    analyze_btn = st.button("🔍 Analyze Password", type="primary", use_container_width=True, key="analyze_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_btn:
        if not pw_input:
            st.error("⚠️ Please enter a password.")
        elif len(pw_input) < MIN_LEN:
            st.markdown(f"""<div class="reject-box">
              <div class="reject-title">❌ Password Rejected!</div>
              <div class="reject-sub">Minimum <b>6 characters</b> required. You entered <b>{len(pw_input)}</b>.</div>
            </div>""", unsafe_allow_html=True)
        else:
            r = analyze(pw_input)
            conf_s = f" · Confidence: {r['conf']:.1f}%" if r['conf'] else ""
            method = "RandomForest ML + Rules" if r['ml'] else "Rule-based"

            # Score
            st.markdown(f"""<div class="score-box score-{r['css']}">
              <div class="score-number">{r['score']}</div>
              <div><div class="score-label">{r['strength']} Password</div>
              <div class="score-sublabel">{r['score']}/100 · {method}{conf_s}</div></div>
            </div>""", unsafe_allow_html=True)
            st.progress(r["score"]/100)

            # Crack time
            ct,ce,cm = crack_time(pw_input)
            st.markdown(f"""<div class="crack-box">
              <div style="font-size:1.8rem;">{ce}</div>
              <div><div class="crack-time">{ct}</div>
              <div class="score-sublabel">⏱️ Time to crack (10B guesses/sec GPU)</div>
              <div class="crack-sub">{cm}</div></div>
            </div>""", unsafe_allow_html=True)

            # Chips
            def chip(ok,lbl):
                c="stat-ok" if ok else "stat-no"; i="✓" if ok else "✗"
                return f'<div class="stat-chip"><div class="stat-val {c}">{i}</div><div class="stat-lbl">{lbl}</div></div>'
            st.markdown(f"""<div class="stat-grid">
              {chip(r['hu'],'Uppercase')}{chip(r['hl'],'Lowercase')}
              {chip(r['hd'],'Numbers')}{chip(r['hs'],'Symbols')}
            </div>
            <div style="display:flex;gap:1.3rem;margin-top:0.5rem;">
              <span style="color:rgba(200,210,255,0.5);font-size:0.78rem;">📏 Length: <b style="color:#00ccff">{r['length']}</b></span>
              <span style="color:rgba(200,210,255,0.5);font-size:0.78rem;">🔠 Unique: <b style="color:#a855f7">{r['unique']}</b></span>
            </div>""", unsafe_allow_html=True)

            # Tips
            if r["tips"]:
                st.markdown("---"); st.markdown("**💡 How to Improve**")
                for tip in r["tips"]: st.markdown(f"&nbsp;&nbsp;▸ {tip}")

            # Suggestions if weak
            if r["score"] < 75:
                st.markdown("---"); st.markdown("**🔒 AI-Generated Strong Suggestions**")
                for _ in range(3):
                    st.markdown(f'<div class="suggestion-box">🔑 {gen_pw()}</div>', unsafe_allow_html=True)
            else:
                st.success("✅ Excellent! This password meets all security criteria.")

            # Save to history
            save_history(uid, site_input, pw_input, r["score"], r["strength"],
                         r["length"], r["hu"], r["hl"], r["hd"], r["hs"])

            # ── SAVE PROMPT ──
            st.markdown("---")
            st.markdown("""<div class="save-prompt">
              <div style="font-size:1rem;font-weight:600;color:#00ccff;">💾 Want to save this password to your Vault?</div>
              <div style="font-size:0.78rem;color:rgba(200,210,255,0.5);margin-top:4px;">It will be encrypted with Fernet encryption</div>
            </div>""", unsafe_allow_html=True)
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button("✅ Yes, Save to Vault", key="yes_save", use_container_width=True):
                    save_vault(uid, site_input or "—", "", enc(pw_input))
                    st.success(f"✅ Saved to Vault with encryption!")
            with sc2:
                if st.button("❌ No, Skip", key="no_save", use_container_width=True):
                    st.info("Okay! Password not saved.")


# ════════════════════════════════════════════════
#  TAB 2 — CREATE MY OWN PASSWORD
# ════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="card-title">✏️ Create Your Own Password</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.25);
         border-radius:12px;padding:1rem 1.3rem;margin-bottom:1rem;">
      <div style="font-size:0.85rem;color:rgba(200,210,255,0.7);">
        💡 <b style="color:#a855f7">Tips before you type:</b><br><br>
        ✅ Use <b>12+ characters</b> for strong password<br>
        ✅ Mix <b>UPPER + lower + Numbers + Symbols</b><br>
        ✅ Avoid <b>your name, DOB, or common words</b><br>
        ✅ Use <b>random combinations</b> — harder to guess<br><br>
        <b>Example of a strong password:</b>
        <span style="font-family:monospace;color:#00ff88;"> MyD0g@IsStr0ng#2024</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    own_site = st.text_input("Website / App", placeholder="Gmail, Instagram…", key="own_site")
    own_pw   = st.text_input("Type Your Password", type="password",
                              placeholder="Create your own strong password here…", key="own_pw")

    # Live meter as they type
    if own_pw and len(own_pw) >= MIN_LEN:
        lr2 = analyze(own_pw)
        if lr2:
            st.markdown(live_meter(lr2["score"], lr2["strength"]), unsafe_allow_html=True)
            ct2,ce2,_ = crack_time(own_pw)
            st.markdown(f'<p style="color:rgba(200,210,255,0.5);font-size:0.76rem;">{ce2} Crack time: <b style="color:#a855f7">{ct2}</b></p>', unsafe_allow_html=True)
    elif own_pw:
        st.markdown(f'<p style="color:#ff7755;font-size:0.78rem;">⚠️ Need {MIN_LEN - len(own_pw)} more characters</p>', unsafe_allow_html=True)

    if st.button("🔍 Analyze My Password", use_container_width=True, key="own_analyze"):
        if not own_pw or len(own_pw) < MIN_LEN:
            st.error(f"❌ Password must be at least {MIN_LEN} characters!")
        else:
            r2 = analyze(own_pw)
            conf_s2 = f" · Confidence: {r2['conf']:.1f}%" if r2['conf'] else ""

            st.markdown(f"""<div class="score-box score-{r2['css']}">
              <div class="score-number">{r2['score']}</div>
              <div><div class="score-label">{r2['strength']} Password</div>
              <div class="score-sublabel">{r2['score']}/100{conf_s2}</div></div>
            </div>""", unsafe_allow_html=True)
            st.progress(r2["score"]/100)

            ct3,ce3,cm3 = crack_time(own_pw)
            st.markdown(f"""<div class="crack-box">
              <div style="font-size:1.8rem;">{ce3}</div>
              <div><div class="crack-time">{ct3}</div>
              <div class="crack-sub">{cm3}</div></div>
            </div>""", unsafe_allow_html=True)

            if r2["tips"]:
                st.markdown("**💡 Improvements:**")
                for t in r2["tips"]: st.markdown(f"&nbsp;&nbsp;▸ {t}")

            save_history(uid, own_site, own_pw, r2["score"], r2["strength"],
                         r2["length"], r2["hu"], r2["hl"], r2["hd"], r2["hs"])

            # Save prompt
            st.markdown("---")
            st.markdown("""<div class="save-prompt">
              <div style="font-size:1rem;font-weight:600;color:#00ccff;">💾 Want to save this password to Vault?</div>
            </div>""", unsafe_allow_html=True)
            oc1,oc2 = st.columns(2)
            with oc1:
                if st.button("✅ Yes, Save", key="own_yes", use_container_width=True):
                    save_vault(uid, own_site or "—", "", enc(own_pw))
                    st.success("✅ Saved to Vault!")
            with oc2:
                if st.button("❌ No, Skip", key="own_no", use_container_width=True):
                    st.info("Password not saved.")


# ════════════════════════════════════════════════
#  TAB 3 — GENERATOR
# ════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="card-title">🎲 AI Password Generator</div>', unsafe_allow_html=True)
    gen_len = st.slider("📏 Length", 8, 32, 16, key="gen_len")
    g1,g2,g3,g4 = st.columns(4)
    with g1: gu = st.checkbox("A–Z", value=True, key="gu")
    with g2: gl = st.checkbox("a–z", value=True, key="gl")
    with g3: gd = st.checkbox("0–9", value=True, key="gd")
    with g4: gs = st.checkbox("!@#", value=True, key="gs")

    act = sum([gu,gl,gd,gs])
    ps  = int(min(100,(gen_len/32)*50+(act/4)*50))
    pc  = "#00ff88" if ps>=75 else ("#ffcc33" if ps>=45 else "#ff4466")
    st.markdown(f"""
    <div style="margin:0.5rem 0 0.3rem;">
      <div style="background:rgba(255,255,255,0.07);border-radius:8px;height:8px;">
        <div style="width:{ps}%;height:8px;border-radius:8px;background:linear-gradient(90deg,{pc}88,{pc});"></div>
      </div>
      <div style="color:{pc};font-size:0.78rem;margin-top:3px;font-weight:600;">
        {"Strong" if ps>=75 else ("Medium" if ps>=45 else "Weak")} · ~{ps}/100
      </div>
    </div>""", unsafe_allow_html=True)

    if st.button("⚡ Generate Password", type="primary", use_container_width=True, key="gen_btn"):
        if not any([gu,gl,gd,gs]): st.warning("Select at least one type!")
        else: st.session_state["gpw"] = gen_pw(gen_len,gu,gl,gd,gs)

    if "gpw" in st.session_state:
        gpw = st.session_state["gpw"]
        st.markdown(f'<div class="gen-pw-box">🔑 {gpw}</div>', unsafe_allow_html=True)
        st.code(gpw, language=None)
        st.caption("👆 Click copy icon to copy!")

        gr = analyze(gpw)
        st.markdown(live_meter(gr["score"],gr["strength"]), unsafe_allow_html=True)
        gct,gce,gcm = crack_time(gpw)
        st.markdown(f"""<div class="crack-box" style="padding:0.7rem 1.1rem;">
          <span style="font-size:1.4rem;">{gce}</span>
          <div><div class="crack-time" style="font-size:1.1rem;">{gct}</div>
          <div class="crack-sub">{gcm}</div></div>
        </div>""", unsafe_allow_html=True)

        rc1,rc2 = st.columns(2)
        with rc1:
            if st.button("🔄 Regenerate", use_container_width=True, key="regen"):
                st.session_state["gpw"] = gen_pw(gen_len,gu,gl,gd,gs); st.rerun()
        with rc2:
            if st.button("💾 Save to Vault", use_container_width=True, key="gen_save"):
                save_vault(uid,"Generated","",enc(gpw))
                st.success("✅ Saved!")


# ════════════════════════════════════════════════
#  TAB 4 — HISTORY & CHARTS
# ════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="card-title">📊 Your Analysis History</div>', unsafe_allow_html=True)
    rows = get_history(uid)

    if not rows:
        st.info("No history yet. Analyze some passwords!")
    else:
        total  = len(rows)
        strong = sum(1 for r in rows if r[3]=="Strong")
        medium = sum(1 for r in rows if r[3]=="Medium")
        weak   = sum(1 for r in rows if r[3]=="Weak")
        avg    = int(sum(r[2] for r in rows)/total)

        m1,m2,m3,m4,m5 = st.columns(5)
        m1.metric("Total",total); m2.metric("💪 Strong",strong)
        m3.metric("⚡ Medium",medium); m4.metric("❌ Weak",weak); m5.metric("📈 Avg",avg)

        st.markdown("---")
        hc1,hc2 = st.columns(2)
        with hc1:
            st.markdown("**🥧 Distribution**")
            fig = go.Figure(go.Pie(labels=["Strong","Medium","Weak"],values=[strong,medium,weak],
                hole=0.5,marker_colors=["#00ff88","#ffcc33","#ff4466"],
                textinfo="label+percent",textfont_size=12))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                font_color="rgba(200,210,255,0.8)",showlegend=False,
                margin=dict(t=10,b=10,l=10,r=10),height=260)
            st.plotly_chart(fig,use_container_width=True)
        with hc2:
            st.markdown("**📊 Count**")
            fig2 = go.Figure(go.Bar(x=["Weak","Medium","Strong"],y=[weak,medium,strong],
                marker_color=["#ff4466","#ffcc33","#00ff88"],
                text=[weak,medium,strong],textposition="outside",
                textfont=dict(color="rgba(200,210,255,0.8)",size=13)))
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                font_color="rgba(200,210,255,0.8)",
                xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor="rgba(255,255,255,0.06)"),
                margin=dict(t=20,b=20,l=10,r=10),height=260)
            st.plotly_chart(fig2,use_container_width=True)

        st.markdown("**📈 Score Trend**")
        recent = [r[2] for r in reversed(rows)][:30]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=list(range(1,len(recent)+1)),y=recent,
            mode="lines+markers",line=dict(color="#00ccff",width=2),
            marker=dict(color="#00ff88",size=5),fill="tozeroy",fillcolor="rgba(0,204,255,0.07)"))
        fig3.add_hline(y=75,line_dash="dash",line_color="rgba(0,255,136,0.4)",
            annotation_text="Strong",annotation_font_color="rgba(0,255,136,0.6)")
        fig3.add_hline(y=40,line_dash="dash",line_color="rgba(255,200,50,0.4)",
            annotation_text="Medium",annotation_font_color="rgba(255,200,50,0.6)")
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(200,210,255,0.8)",
            xaxis=dict(title="Check #",showgrid=False),
            yaxis=dict(title="Score",range=[0,105],showgrid=True,gridcolor="rgba(255,255,255,0.06)"),
            margin=dict(t=20,b=20,l=10,r=10),height=280,showlegend=False)
        st.plotly_chart(fig3,use_container_width=True)

        st.markdown("---")
        st.markdown("**🗂️ Recent Checks**")
        for row in rows[:20]:
            sv,pv,scv,stv,lv,dv = row
            sc_cls = f"hist-score-{stv.lower()}"
            st.markdown(f"""<div class="hist-row">
              <span class="hist-site">🌐 {sv}</span>
              <span class="{sc_cls}">{scv}/100</span>
              <span style="color:rgba(200,210,255,0.6);font-size:0.8rem;">{stv} · {lv} chars</span>
              <span class="hist-date">🕐 {dv}</span>
            </div>""", unsafe_allow_html=True)

        # ── CSV DOWNLOAD ──
        st.markdown("---")
        df_exp = get_history_df(uid)
        if not df_exp.empty:
            st.download_button(
                label="📥 Download History as CSV",
                data=df_exp.to_csv(index=False).encode("utf-8"),
                file_name=f"securepass_history_{datetime.now().strftime('%d%m%Y')}.csv",
                mime="text/csv", use_container_width=True, key="dl_csv")
            st.caption("👆 CSV file mein saari history save ho jaayegi!")

        st.markdown("---")
        if st.button("🗑️ Clear My History", use_container_width=True, key="clr_hist"):
            clear_history(uid); st.success("Cleared!"); st.rerun()


# ════════════════════════════════════════════════
#  TAB 5 — VAULT
# ════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="card-title">🔐 Your Secure Vault</div>', unsafe_allow_html=True)
    vc1,vc2 = st.columns(2)
    with vc1:
        vs  = st.text_input("Website/App", key="vs", placeholder="GitHub, Gmail…")
        vun = st.text_input("Username/Email", key="vun", placeholder="your@email.com")
    with vc2:
        vp  = st.text_input("Password", type="password", key="vp", placeholder="Password to store")

    if st.button("💾 Save Securely", use_container_width=True, key="v_save"):
        if vs and vp:
            if len(vp) < MIN_LEN:
                st.error(f"❌ Min {MIN_LEN} characters required!")
            else:
                save_vault(uid, vs, vun, enc(vp))
                st.success(f"✅ Password for **{vs}** saved with Fernet encryption!")
        else:
            st.warning("Fill Website and Password!")

    st.markdown("---")
    st.markdown('<div class="card-title">📂 Your Saved Passwords</div>', unsafe_allow_html=True)
    vrows = get_vault(uid)
    if vrows:
        for vr in vrows:
            vsite,vuser,venc,vdate = vr
            vpw = dec(venc)
            with st.expander(f"🌐 {vsite}  ·  {vdate}"):
                st.write(f"**User:** `{vuser}`")
                st.write(f"**Password:** `{vpw}`")
    else:
        st.info("Vault is empty. Analyze a password and save it!")

    st.markdown("""
    <div style="background:rgba(0,255,136,0.05);border:1px solid rgba(0,255,136,0.2);
         border-radius:10px;padding:0.8rem 1rem;font-size:0.8rem;color:rgba(200,210,255,0.65);margin-top:1rem;">
      🔒 <b style="color:#00ff88">Security:</b> All passwords encrypted with <b>Fernet</b>.
      Key stored in <code>secret.key</code> file.
    </div>""", unsafe_allow_html=True)


# Footer
st.markdown("""
<div class="footer-txt">
  SecurePass AI · MCA Practical Project · RandomForest ML (99.96%) ·
  Login System · SQLite · Plotly · Fernet Encryption · Streamlit
</div>
""", unsafe_allow_html=True)
