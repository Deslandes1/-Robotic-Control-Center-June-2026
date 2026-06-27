import streamlit as st
import os
import tempfile
import time
import base64

# ---------- Voice generation ----------
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

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Robotic Control Center | GlobalInternet.py",
    layout="wide",
    page_icon="🤖"
)

# ========== CUSTOM CSS ==========
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
        width: 100% !important;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 30px rgba(0,212,255,0.3); }
    .stTextInput>div>div>input {
        background-color: #141018 !important;
        color: #ffffff !important;
        border: 1px solid #2a3a5a !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== ROBOT DEFINITIONS ==========
ROBOTS = {
    "Red Titan": {"color": "#ff3333", "accent": "#ff6666", "description": "Heavy combat model with reinforced armor."},
    "Blue Sentinel": {"color": "#3388ff", "accent": "#66aaff", "description": "Scout and reconnaissance unit."},
    "Green Viper": {"color": "#33cc66", "accent": "#66ff99", "description": "Stealth and agility specialist."},
    "Gold Phoenix": {"color": "#ffaa00", "accent": "#ffcc44", "description": "Command and leadership unit."},
    "Silver Ghost": {"color": "#cccccc", "accent": "#eeeeee", "description": "Advanced prototype with unknown capabilities."}
}

# ========== 3D VIEWER HTML ==========
def get_robot_viewer_html(robot_name, command=None):
    color_map = {
        "Red Titan": 0xff3333,
        "Blue Sentinel": 0x3388ff,
        "Green Viper": 0x33cc66,
        "Gold Phoenix": 0xffaa00,
        "Silver Ghost": 0xcccccc
    }
    robot_color = color_map.get(robot_name, 0x3388ff)
    
    # Map command to animation name (YBot has: idle, walk, run, jump, wave)
    anim = "idle"
    if command:
        cmd_lower = command.lower()
        if "walk" in cmd_lower:
            anim = "walk"
        elif "run" in cmd_lower:
            anim = "run"
        elif "jump" in cmd_lower or "backflip" in cmd_lower:
            anim = "jump"
        elif "wave" in cmd_lower:
            anim = "wave"
    
    # We'll use a simple HTML with script tags (no importmap) for better compatibility
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; overflow: hidden; background: #0a0a0f; font-family: Arial; }
            #container { width: 100vw; height: 100vh; }
            #loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #8899bb; font-size: 18px; }
            #info { position: absolute; bottom: 20px; left: 20px; color: #8899bb; font-size: 14px; pointer-events: none; }
        </style>
    </head>
    <body>
        <div id="loading">🤖 Loading robot...</div>
        <div id="container"></div>
        <div id="info">Robot: ROBOT_NAME | Command: COMMAND</div>
        
        <script type="importmap">
        {
            "imports": {
                "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
                "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
            }
        }
        </script>
        
        <script type="module">
            import * as THREE from 'three';
            import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
            import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
            
            const container = document.getElementById('container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0f);
            
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
            camera.position.set(2, 1.5, 3);
            camera.lookAt(0, 0.5, 0);
            
            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            container.appendChild(renderer.domElement);
            
            const controls = new OrbitControls(camera, renderer.domElement);
            controls.target.set(0, 0.5, 0);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 1.5;
            controls.maxDistance = 8;
            controls.update();
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404060);
            scene.add(ambientLight);
            
            const mainLight = new THREE.DirectionalLight(0xffffff, 1.5);
            mainLight.position.set(3, 5, 4);
            mainLight.castShadow = true;
            scene.add(mainLight);
            
            const fillLight = new THREE.DirectionalLight(0x4488ff, 0.5);
            fillLight.position.set(-2, 1, 3);
            scene.add(fillLight);
            
            const rimLight = new THREE.DirectionalLight(0xffffff, 0.8);
            rimLight.position.set(0, 2, -4);
            scene.add(rimLight);
            
            const gridHelper = new THREE.GridHelper(4, 10, 0x445566, 0x223344);
            gridHelper.position.y = -0.01;
            scene.add(gridHelper);
            
            // Load YBot model
            const loader = new GLTFLoader();
            let mixer = null;
            let model = null;
            let animActions = {};
            let currentAction = null;
            let loading = document.getElementById('loading');
            
            const modelUrl = 'https://threejs.org/examples/models/gltf/YBot.glb';
            loader.load(modelUrl, (gltf) => {
                model = gltf.scene;
                model.scale.set(0.8, 0.8, 0.8);
                model.position.set(0, 0, 0);
                // Colorize
                model.traverse((child) => {
                    if (child.isMesh && child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach(mat => { if (mat.color) mat.color.setHex(ROBOT_COLOR); });
                        } else {
                            if (child.material.color) child.material.color.setHex(ROBOT_COLOR);
                        }
                    }
                });
                scene.add(model);
                loading.style.display = 'none';
                
                // Animations
                mixer = new THREE.AnimationMixer(model);
                if (gltf.animations && gltf.animations.length > 0) {
                    gltf.animations.forEach((clip) => {
                        const action = mixer.clipAction(clip);
                        const name = clip.name.toLowerCase();
                        animActions[name] = action;
                    });
                    if (animActions['idle']) {
                        currentAction = animActions['idle'];
                        currentAction.play();
                    }
                }
                const animName = 'ANIM';
                if (animName !== 'idle' && animActions[animName]) {
                    if (currentAction) currentAction.fadeOut(0.5);
                    currentAction = animActions[animName];
                    currentAction.reset().fadeIn(0.5).play();
                }
            }, undefined, (error) => {
                console.warn('Model load failed, using fallback:', error);
                loading.textContent = '⚠️ Model not available, showing fallback';
                createFallbackRobot();
            });
            
            function createFallbackRobot() {
                // Create a simple humanoid from primitives
                const group = new THREE.Group();
                const color = ROBOT_COLOR;
                
                // Body
                const bodyGeo = new THREE.BoxGeometry(0.8, 0.9, 0.5);
                const bodyMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.4, metalness: 0.6 });
                const body = new THREE.Mesh(bodyGeo, bodyMat);
                body.position.y = 0.45;
                body.castShadow = true;
                group.add(body);
                
                // Head (sphere)
                const headMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, roughness: 0.3, metalness: 0.2 });
                const head = new THREE.Mesh(new THREE.SphereGeometry(0.25, 16, 16), headMat);
                head.position.set(0, 0.95, 0);
                head.castShadow = true;
                group.add(head);
                
                // Left arm
                const armMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.4, metalness: 0.6 });
                const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.6, 8), armMat);
                arm.position.set(-0.5, 0.6, 0);
                arm.rotation.z = 0.2;
                arm.castShadow = true;
                group.add(arm);
                
                // Right arm
                const arm2 = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.6, 8), armMat);
                arm2.position.set(0.5, 0.6, 0);
                arm2.rotation.z = -0.2;
                arm2.castShadow = true;
                group.add(arm2);
                
                // Legs
                const legMat = new THREE.MeshStandardMaterial({ color: 0x444444, roughness: 0.5, metalness: 0.3 });
                const leg1 = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.6, 8), legMat);
                leg1.position.set(-0.2, 0.0, 0);
                leg1.castShadow = true;
                group.add(leg1);
                
                const leg2 = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.6, 8), legMat);
                leg2.position.set(0.2, 0.0, 0);
                leg2.castShadow = true;
                group.add(leg2);
                
                scene.add(group);
                loading.style.display = 'none';
            }
            
            // Animation loop
            let clock = new THREE.Clock();
            function animate() {
                requestAnimationFrame(animate);
                const delta = clock.getDelta();
                if (mixer) mixer.update(delta);
                controls.update();
                renderer.render(scene, camera);
            }
            animate();
            
            // Resize
            window.addEventListener('resize', () => {
                const w = container.clientWidth;
                const h = container.clientHeight;
                renderer.setSize(w, h);
                camera.aspect = w / h;
                camera.updateProjectionMatrix();
            });
        </script>
    </body>
    </html>
    """
    # Replace placeholders
    html = html_template.replace('ROBOT_NAME', robot_name)
    html = html.replace('COMMAND', command if command else 'Idle')
    html = html.replace('ROBOT_COLOR', str(robot_color))
    html = html.replace('ANIM', anim)
    return html

# ========== SESSION STATE ==========
if 'robot_selected' not in st.session_state:
    st.session_state.robot_selected = "Red Titan"
if 'command' not in st.session_state:
    st.session_state.command = ""
if 'speak_text' not in st.session_state:
    st.session_state.speak_text = ""
if 'last_action' not in st.session_state:
    st.session_state.last_action = "idle"
if 'history' not in st.session_state:
    st.session_state.history = []

# ========== HEADER ==========
st.markdown("""
<div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #2a3a5a; margin-bottom: 30px;">
    <h1 style="color: #00d4ff; font-size: 2.8rem; margin: 0; text-shadow: 0 0 30px rgba(0,212,255,0.2);">🤖 Robotic Control Center</h1>
    <p style="color: #8899bb; font-size: 1.1rem;">Select a robot, command it, and watch it perform – built by GlobalInternet.py</p>
    <span style="display: inline-block; background: #00ff64; color: #0a0a0f; padding: 4px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; animation: pulse 2s infinite;">● LIVE SIMULATION</span>
</div>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### 🤖 Robot Selection")
    robot_names = list(ROBOTS.keys())
    selected = st.selectbox("Select Robot", robot_names, index=robot_names.index(st.session_state.robot_selected))
    if selected != st.session_state.robot_selected:
        st.session_state.robot_selected = selected
        st.session_state.last_action = "idle"
        st.rerun()
    
    robot_info = ROBOTS[st.session_state.robot_selected]
    st.markdown(f"""
    <div class="robot-card">
        <div class="robot-name" style="color: {robot_info['color']};">{st.session_state.robot_selected}</div>
        <div class="robot-type">{robot_info['description']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎮 Commands")
    action_input = st.text_input("Action (e.g., walk, run, jump, wave, backflip)", key="action_input", placeholder="e.g., backflip")
    if st.button("▶️ Execute Action", use_container_width=True):
        if action_input.strip():
            st.session_state.command = action_input.strip()
            st.session_state.last_action = action_input.strip().lower()
            st.rerun()
        else:
            st.warning("Please enter an action.")
    
    st.markdown("---")
    st.markdown("### 🗣️ Speech")
    speak_input = st.text_input("Speak (text)", key="speak_input", placeholder="e.g., Hello, I am your robot.")
    if st.button("🔊 Make Robot Speak", use_container_width=True):
        if speak_input.strip():
            st.session_state.speak_text = speak_input.strip()
            st.rerun()
        else:
            st.warning("Please enter text to speak.")
    
    st.markdown("---")
    st.markdown("### 📞 Contact")
    st.markdown("""
    <div style="background: rgba(20,30,50,0.8); border: 1px solid #2a3a5a; border-radius: 8px; padding: 12px; font-size: 0.85rem; color: #8899bb;">
        <strong style="color: #00d4ff;">Email:</strong> deslandes78@gmail.com<br>
        <strong style="color: #00d4ff;">Phone:</strong> (509) 4738-5663<br>
        <strong style="color: #00d4ff;">Website:</strong> <a href="https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/" style="color: #00d4ff;" target="_blank">globalinternet-py.com</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔧 Status")
    st.markdown(f"**Current Robot:** {st.session_state.robot_selected}")
    st.markdown(f"**Last Action:** {st.session_state.last_action}")

# ========== MAIN CONTENT ==========
col_view, col_info = st.columns([3, 1])

with col_view:
    st.markdown("### 🖥️ Robot View")
    viewer_html = get_robot_viewer_html(st.session_state.robot_selected, st.session_state.command)
    st.components.v1.html(viewer_html, height=650, scrolling=False)

with col_info:
    st.markdown("### 📊 Command History")
    if st.session_state.command and st.session_state.command not in [h[0] for h in st.session_state.history]:
        st.session_state.history.append((st.session_state.command, "Executed"))
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[-20:]
    
    if st.session_state.history:
        for cmd, status in reversed(st.session_state.history[-10:]):
            st.markdown(f"""
            <div style="background: rgba(0,212,255,0.05); border-left: 3px solid #00d4ff; padding: 5px 10px; margin: 5px 0; border-radius: 4px;">
                <span style="color: #00d4ff;">▶️</span> <span style="color: #ffffff;">{cmd}</span><br>
                <span style="color: #8899bb; font-size: 0.8rem;">{status}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No commands yet.")

# ---------- Speak ----------
if st.session_state.speak_text:
    with st.spinner("🗣️ Generating speech..."):
        audio_bytes = generate_audio(st.session_state.speak_text, "en")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.history.append((f"Speak: {st.session_state.speak_text}", "Speech played"))
            st.success("✅ Speech played.")
        else:
            st.error("❌ Speech generation failed.")
    st.session_state.speak_text = ""

# ========== FOOTER ==========
st.markdown("""
<div class="footer">
    <p>© 2026 GlobalInternet.py Online Software Company</p>
    <p>Built by <strong>Gesner Deslandes</strong> | (509) 4738-5663 | deslandes78@gmail.com</p>
    <p style="font-size:0.8rem; color:#445566;">🤖 Simulated robot control – ready for real-world hardware integration.</p>
</div>
""", unsafe_allow_html=True)
