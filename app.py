import streamlit as st
import os
import tempfile
import time
import base64
import json

try:
    from gtts import gTTS
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

def generate_audio(text, lang_code="en"):
    if not VOICE_AVAILABLE or not text.strip():
        return None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(tmp_path)
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)
        return audio_bytes
    except Exception:
        return None

st.set_page_config(
    page_title="Robotic Control Center | GlobalInternet.py",
    layout="wide",
    page_icon="🤖"
)

st.markdown("""
<style>
    .stApp { background: #0a0a0f; color: #ffffff; }
    [data-testid="stSidebar"] { background: #0d0d12; border-right: 1px solid #2a2a3a; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCaption { color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6, p, li, .stMarkdown, .stCaption, label { color: #ffffff !important; }
    .robot-card {
        background: rgba(20,30,50,0.7);
        border: 1px solid #2a3a5a;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        backdrop-filter: blur(5px);
    }
    .robot-card .robot-name { font-size: 1.4rem; font-weight: 600; color: #00d4ff; }
    .robot-card .robot-type { font-size: 0.9rem; color: #8899bb; }
    .footer { text-align: center; padding: 20px 0; border-top: 1px solid #2a3a5a; margin-top: 30px; color: #667799; font-size: 0.9rem; }
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff, #0088ff) !important;
        color: #0a0a0f !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 30px rgba(0,212,255,0.3); }
    .stTextInput>div>div>input {
        background-color: #141018 !important;
        color: #ffffff !important;
        border: 1px solid #2a3a5a !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
    }
    .profile-img {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #00d4ff;
        display: block;
        margin: 0 auto 8px auto;
    }
    .profile-name {
        color: #ffffff;
        text-align: center;
        margin-top: 8px;
        margin-bottom: 0;
        font-size: 1.2rem;
    }
    .profile-title {
        color: #8899bb;
        text-align: center;
        font-size: 0.9rem;
        margin-top: 0;
    }
    .status-panel {
        background: rgba(20,30,50,0.5);
        border: 1px solid #2a3a5a;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        text-align: center;
    }
    .status-panel .label {
        color: #8899bb;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .status-panel .value {
        color: #00d4ff;
        font-size: 1.2rem;
        font-weight: 600;
    }
    .log-box {
        background: #050508;
        border: 1px solid #1a2a4a;
        border-radius: 8px;
        padding: 12px;
        height: 200px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 0.85rem;
        color: #00ff64;
    }
</style>
""", unsafe_allow_html=True)

# ---- 5 Robot Models ----
ROBOTS = {
    "Red Titan": {"color": "#ff3333", "accent": "#ff6666", "description": "Heavy combat model with reinforced armor."},
    "Blue Sentinel": {"color": "#3388ff", "accent": "#66aaff", "description": "Scout and reconnaissance unit."},
    "Green Viper": {"color": "#33cc66", "accent": "#66ff99", "description": "Stealth and agility specialist."},
    "Gold Phoenix": {"color": "#ffaa00", "accent": "#ffcc44", "description": "Command and leadership unit."},
    "Silver Ghost": {"color": "#cccccc", "accent": "#eeeeee", "description": "Advanced prototype with unknown capabilities."}
}

# ---- 10 Katas ----
KATAS = {
    "Taikyoku Shodan": {"kimono": "#f0f0f0", "belt": "#ffffff", "headband": "#ff0000", "belt_rank": "White"},
    "Heian Shodan": {"kimono": "#f0f0f0", "belt": "#ffff00", "headband": "#0000ff", "belt_rank": "Yellow"},
    "Heian Nidan": {"kimono": "#f0f0f0", "belt": "#ffa500", "headband": "#00ff00", "belt_rank": "Orange"},
    "Heian Sandan": {"kimono": "#f0f0f0", "belt": "#00ff00", "headband": "#ffff00", "belt_rank": "Green"},
    "Heian Yondan": {"kimono": "#f0f0f0", "belt": "#800080", "headband": "#ffa500", "belt_rank": "Purple"},
    "Heian Godan": {"kimono": "#f0f0f0", "belt": "#8b4513", "headband": "#800080", "belt_rank": "Brown"},
    "Tekki Shodan": {"kimono": "#0000ff", "belt": "#8b4513", "headband": "#ff0000", "belt_rank": "Brown"},
    "Bassai Dai": {"kimono": "#0000ff", "belt": "#000000", "headband": "#ffffff", "belt_rank": "Black"},
    "Kanku Dai": {"kimono": "#000000", "belt": "#000000", "headband": "#ffd700", "belt_rank": "Black"},
    "Gojushiho": {"kimono": "#000000", "belt": "#000000", "headband": "#c0c0c0", "belt_rank": "Black"}
}

def get_kata_sequence(kata_name):
    base = [["bow", 2.0], ["walk", 3.0], ["jump", 1.2], ["wave", 2.0], ["backflip", 1.5], ["walk", 3.0], ["bow", 2.0]]
    variations = {
        "Taikyoku Shodan": [["idle", 1.0]] + base,
        "Heian Shodan": base + [["idle", 1.0]],
        "Heian Nidan": [["walk", 2.0], ["run", 2.0]] + base[2:],
        "Heian Sandan": base[:3] + [["run", 2.0]] + base[3:],
        "Heian Yondan": base[:4] + [["idle", 1.0]] + base[4:],
        "Heian Godan": base[:2] + [["jump", 1.2], ["walk", 2.0]] + base[3:],
        "Tekki Shodan": [["bow", 2.0], ["idle", 2.0]] + base[2:],
        "Bassai Dai": base + [["idle", 2.0]],
        "Kanku Dai": [["walk", 4.0], ["jump", 1.2], ["wave", 2.0], ["backflip", 1.5], ["walk", 4.0]],
        "Gojushiho": [["bow", 3.0], ["walk", 3.0], ["run", 3.0], ["jump", 1.2], ["backflip", 1.5], ["wave", 2.0], ["bow", 2.0]]
    }
    return variations.get(kata_name, base)

def get_robot_viewer_html(robot_name, command=None, kata_name=None):
    color_map = {"Red Titan": 0xff3333, "Blue Sentinel": 0x3388ff, "Green Viper": 0x33cc66, "Gold Phoenix": 0xffaa00, "Silver Ghost": 0xcccccc}
    main_color = color_map.get(robot_name, 0x3388ff)
    accent = main_color + 0x444444 if main_color < 0xcccccc else 0xeeeeee

    is_kata = kata_name is not None
    kata_info = KATAS.get(kata_name, None)
    if is_kata and kata_info:
        kimono_color = int(kata_info["kimono"].lstrip("#"), 16)
        belt_color = int(kata_info["belt"].lstrip("#"), 16)
        headband_color = int(kata_info["headband"].lstrip("#"), 16)
    else:
        kimono_color = main_color
        belt_color = main_color
        headband_color = main_color

    cmd_lower = command.lower() if command else "idle"
    valid_commands = ['walk', 'run', 'jump', 'wave', 'backflip']
    anim_cmd = cmd_lower if cmd_lower in valid_commands else 'idle'

    kata_sequence = get_kata_sequence(kata_name) if is_kata else []
    kata_sequence_json = json.dumps(kata_sequence)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; overflow: hidden; background: #0a0a0f; font-family: Arial; }
            #container { width: 100vw; height: 100vh; position: relative; }
            #info { position: absolute; bottom: 20px; left: 20px; color: #8899bb; font-size: 14px; pointer-events: none; z-index: 10; }
            #loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #8899bb; font-size: 18px; z-index: 5; }
        </style>
    </head>
    <body>
        <div id="container">
            <div id="loading">🤖 Loading robot...</div>
            <div id="info">🤖 ROBOT_NAME | Command: COMMAND</div>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        
        <script>
            setTimeout(function() {
                var l = document.getElementById('loading');
                if (l) l.style.display = 'none';
            }, 800);
            
            function checkThree() {
                if (typeof THREE !== 'undefined') {
                    initScene();
                } else {
                    setTimeout(checkThree, 100);
                }
            }
            checkThree();
            
            function initScene() {
                var container = document.getElementById('container');
                var loading = document.getElementById('loading');
                if (loading) loading.style.display = 'none';
                
                var scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0a0a0f);
                
                var camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
                camera.position.set(3, 2, 4);
                camera.lookAt(0, 0.8, 0);
                
                var renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                renderer.toneMapping = THREE.ACESFilmicToneMapping;
                renderer.toneMappingExposure = 1.2;
                container.appendChild(renderer.domElement);
                
                var controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.target.set(0, 0.8, 0);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.minDistance = 2;
                controls.maxDistance = 10;
                controls.update();
                
                var ambientLight = new THREE.AmbientLight(0x404060);
                scene.add(ambientLight);
                var mainLight = new THREE.DirectionalLight(0xffffff, 1.5);
                mainLight.position.set(4, 6, 5);
                mainLight.castShadow = true;
                scene.add(mainLight);
                var fillLight = new THREE.DirectionalLight(0x4488ff, 0.5);
                fillLight.position.set(-3, 1, 4);
                scene.add(fillLight);
                var rimLight = new THREE.DirectionalLight(0xffffff, 0.8);
                rimLight.position.set(0, 2, -5);
                scene.add(rimLight);
                
                var gridHelper = new THREE.GridHelper(5, 10, 0x445566, 0x223344);
                gridHelper.position.y = -0.01;
                scene.add(gridHelper);
                
                var COLOR = MAIN_COLOR;
                var ACCENT = ACCENT_COLOR;
                var KIMONO = KIMONO_COLOR;
                var BELT = BELT_COLOR;
                var HEADBAND = HEADBAND_COLOR;
                var IS_KATA = IS_KATA;
                
                var robot = new THREE.Group();
                
                var torsoGeo = new THREE.BoxGeometry(0.9, 1.0, 0.6);
                var torsoMat = new THREE.MeshStandardMaterial({ color: KIMONO, roughness: 0.3, metalness: 0.7 });
                var torso = new THREE.Mesh(torsoGeo, torsoMat);
                torso.position.y = 0.9;
                torso.castShadow = true;
                robot.add(torso);
                
                var chestGeo = new THREE.BoxGeometry(0.6, 0.3, 0.1);
                var chestMat = new THREE.MeshStandardMaterial({ color: ACCENT, roughness: 0.4, metalness: 0.8 });
                var chest = new THREE.Mesh(chestGeo, chestMat);
                chest.position.set(0, 1.0, 0.35);
                robot.add(chest);
                
                if (IS_KATA) {
                    var beltGeo = new THREE.CylinderGeometry(0.55, 0.55, 0.12, 16);
                    var beltMat = new THREE.MeshStandardMaterial({ color: BELT, roughness: 0.3, metalness: 0.2 });
                    var belt = new THREE.Mesh(beltGeo, beltMat);
                    belt.position.set(0, 0.45, 0);
                    belt.rotation.x = Math.PI/2;
                    robot.add(belt);
                }
                
                var headGroup = new THREE.Group();
                var headGeo = new THREE.BoxGeometry(0.5, 0.45, 0.45);
                var headMat = new THREE.MeshStandardMaterial({ color: 0xaaaaaa, roughness: 0.3, metalness: 0.5 });
                var head = new THREE.Mesh(headGeo, headMat);
                head.position.y = 0.15;
                head.castShadow = true;
                headGroup.add(head);
                
                var visorGeo = new THREE.BoxGeometry(0.35, 0.12, 0.05);
                var visorMat = new THREE.MeshStandardMaterial({ color: 0x00ddff, emissive: 0x00bbff, emissiveIntensity: 0.8 });
                var visor = new THREE.Mesh(visorGeo, visorMat);
                visor.position.set(0, 0.15, 0.25);
                headGroup.add(visor);
                
                if (IS_KATA) {
                    var headbandGeo = new THREE.TorusGeometry(0.28, 0.04, 8, 16);
                    var headbandMat = new THREE.MeshStandardMaterial({ color: HEADBAND, roughness: 0.4, metalness: 0.3 });
                    var headband = new THREE.Mesh(headbandGeo, headbandMat);
                    headband.position.set(0, 0.15, 0);
                    headband.rotation.x = Math.PI/2;
                    headGroup.add(headband);
                }
                
                var antennaMat = new THREE.MeshStandardMaterial({ color: 0xffaa00, emissive: 0xff8800, emissiveIntensity: 0.3 });
                var antenna = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.2), antennaMat);
                antenna.position.set(0, 0.45, 0);
                headGroup.add(antenna);
                var antennaBall = new THREE.Mesh(new THREE.SphereGeometry(0.05), antennaMat);
                antennaBall.position.set(0, 0.55, 0);
                headGroup.add(antennaBall);
                
                headGroup.position.set(0, 1.4, 0);
                robot.add(headGroup);
                
                var shoulderMat = new THREE.MeshStandardMaterial({ color: KIMONO, roughness: 0.4, metalness: 0.6 });
                var shoulderL = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 8), shoulderMat);
                shoulderL.position.set(-0.6, 1.2, 0);
                robot.add(shoulderL);
                var shoulderR = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 8), shoulderMat);
                shoulderR.position.set(0.6, 1.2, 0);
                robot.add(shoulderR);
                
                var armGroupL = new THREE.Group();
                var armGroupR = new THREE.Group();
                var upperArmMat = new THREE.MeshStandardMaterial({ color: KIMONO, roughness: 0.3, metalness: 0.7 });
                var lowerArmMat = new THREE.MeshStandardMaterial({ color: KIMONO, roughness: 0.4, metalness: 0.6 });
                
                var upperL = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.5, 0.2), upperArmMat);
                upperL.position.y = -0.25;
                armGroupL.add(upperL);
                var lowerL = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.5, 0.18), lowerArmMat);
                lowerL.position.y = -0.6;
                armGroupL.add(lowerL);
                var handMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.8, roughness: 0.2 });
                var handL = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.15, 0.15), handMat);
                handL.position.y = -0.85;
                armGroupL.add(handL);
                armGroupL.position.set(-0.6, 1.2, 0);
                robot.add(armGroupL);
                
                var upperR = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.5, 0.2), upperArmMat);
                upperR.position.y = -0.25;
                armGroupR.add(upperR);
                var lowerR = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.5, 0.18), lowerArmMat);
                lowerR.position.y = -0.6;
                armGroupR.add(lowerR);
                var handR = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.15, 0.15), handMat);
                handR.position.y = -0.85;
                armGroupR.add(handR);
                armGroupR.position.set(0.6, 1.2, 0);
                robot.add(armGroupR);
                
                var legGroupL = new THREE.Group();
                var legGroupR = new THREE.Group();
                var upperLegMat = new THREE.MeshStandardMaterial({ color: KIMONO, roughness: 0.5, metalness: 0.4 });
                var lowerLegMat = new THREE.MeshStandardMaterial({ color: KIMONO, roughness: 0.5, metalness: 0.3 });
                
                var upperLeg
