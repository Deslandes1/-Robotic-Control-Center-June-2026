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
    .backstage {
        margin-top: 20px;
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

def get_robot_viewer_html(robot_name, command=None):
    color_map = {"Red Titan": 0xff3333, "Blue Sentinel": 0x3388ff, "Green Viper": 0x33cc66, "Gold Phoenix": 0xffaa00, "Silver Ghost": 0xcccccc}
    main_color = color_map.get(robot_name, 0x3388ff)
    accent = main_color + 0x444444 if main_color < 0xcccccc else 0xeeeeee

    cmd_lower = command.lower() if command else "idle"
    valid_commands = ['walk', 'run', 'jump', 'wave', 'backflip']
    anim_cmd = cmd_lower if cmd_lower in valid_commands else 'idle'

    # Simplified HTML with importmap (works reliably)
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; overflow: hidden; background: #0a0a0f; font-family: Arial; }
            #canvas-container { width: 100vw; height: 100vh; display: block; }
            #info { position: absolute; bottom: 20px; left: 20px; color: #8899bb; font-size: 14px; pointer-events: none; z-index: 10; }
        </style>
    </head>
    <body>
        <div id="canvas-container"></div>
        <div id="info">🤖 ROBOT_NAME | Command: COMMAND</div>
        
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
            
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0f);
            
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
            camera.position.set(3, 2, 4);
            camera.lookAt(0, 0.8, 0);
            
            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            container.appendChild(renderer.domElement);
            
            const controls = new OrbitControls(camera, renderer.domElement);
            controls.target.set(0, 0.8, 0);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 2;
            controls.maxDistance = 10;
            controls.update();
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404060);
            scene.add(ambientLight);
            const mainLight = new THREE.DirectionalLight(0xffffff, 1.5);
            mainLight.position.set(4, 6, 5);
            mainLight.castShadow = true;
            scene.add(mainLight);
            const fillLight = new THREE.DirectionalLight(0x4488ff, 0.5);
            fillLight.position.set(-3, 1, 4);
            scene.add(fillLight);
            const rimLight = new THREE.DirectionalLight(0xffffff, 0.8);
            rimLight.position.set(0, 2, -5);
            scene.add(rimLight);
            
            const gridHelper = new THREE.GridHelper(5, 10, 0x445566, 0x223344);
            gridHelper.position.y = -0.01;
            scene.add(gridHelper);
            
            // ---- Robot Construction ----
            const COLOR = MAIN_COLOR;
            const ACCENT = ACCENT_COLOR;
            
            const robot = new THREE.Group();
            
            // Torso
            const torsoGeo = new THREE.BoxGeometry(0.9, 1.0, 0.6);
            const torsoMat = new THREE.MeshStandardMaterial({ color: COLOR, roughness: 0.3, metalness: 0.7 });
            const torso = new THREE.Mesh(torsoGeo, torsoMat);
            torso.position.y = 0.9;
            torso.castShadow = true;
            robot.add(torso);
            
            // Chest detail
            const chestGeo = new THREE.BoxGeometry(0.6, 0.3, 0.1);
            const chestMat = new THREE.MeshStandardMaterial({ color: ACCENT, roughness: 0.4, metalness: 0.8 });
            const chest = new THREE.Mesh(chestGeo, chestMat);
            chest.position.set(0, 1.0, 0.35);
            robot.add(chest);
            
            // Head
            const headGroup = new THREE.Group();
            const headGeo = new THREE.BoxGeometry(0.5, 0.45, 0.45);
            const headMat = new THREE.MeshStandardMaterial({ color: 0xaaaaaa, roughness: 0.3, metalness: 0.5 });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.y = 0.15;
            head.castShadow = true;
            headGroup.add(head);
            
            // Visor
            const visorGeo = new THREE.BoxGeometry(0.35, 0.12, 0.05);
            const visorMat = new THREE.MeshStandardMaterial({ color: 0x00ddff, emissive: 0x00bbff, emissiveIntensity: 0.8 });
            const visor = new THREE.Mesh(visorGeo, visorMat);
            visor.position.set(0, 0.15, 0.25);
            headGroup.add(visor);
            
            // Antenna
            const antennaMat = new THREE.MeshStandardMaterial({ color: 0xffaa00, emissive: 0xff8800, emissiveIntensity: 0.3 });
            const antenna = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.2), antennaMat);
            antenna.position.set(0, 0.45, 0);
            headGroup.add(antenna);
            const antennaBall = new THREE.Mesh(new THREE.SphereGeometry(0.05), antennaMat);
            antennaBall.position.set(0, 0.55, 0);
            headGroup.add(antennaBall);
            
            headGroup.position.set(0, 1.4, 0);
            robot.add(headGroup);
            
            // Shoulders
            const shoulderMat = new THREE.MeshStandardMaterial({ color: COLOR, roughness: 0.4, metalness: 0.6 });
            const shoulderL = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 8), shoulderMat);
            shoulderL.position.set(-0.6, 1.2, 0);
            robot.add(shoulderL);
            const shoulderR = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 8), shoulderMat);
            shoulderR.position.set(0.6, 1.2, 0);
            robot.add(shoulderR);
            
            // Arms
            const armGroupL = new THREE.Group();
            const armGroupR = new THREE.Group();
            const upperArmMat = new THREE.MeshStandardMaterial({ color: COLOR, roughness: 0.3, metalness: 0.7 });
            const lowerArmMat = new THREE.MeshStandardMaterial({ color: ACCENT, roughness: 0.4, metalness: 0.6 });
            
            // Left arm
            const upperL = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.5, 0.2), upperArmMat);
            upperL.position.y = -0.25;
            armGroupL.add(upperL);
            const lowerL = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.5, 0.18), lowerArmMat);
            lowerL.position.y = -0.6;
            armGroupL.add(lowerL);
            const handMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.8, roughness: 0.2 });
            const handL = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.15, 0.15), handMat);
            handL.position.y = -0.85;
            armGroupL.add(handL);
            armGroupL.position.set(-0.6, 1.2, 0);
            robot.add(armGroupL);
            
            // Right arm
            const upperR = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.5, 0.2), upperArmMat);
            upperR.position.y = -0.25;
            armGroupR.add(upperR);
            const lowerR = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.5, 0.18), lowerArmMat);
            lowerR.position.y = -0.6;
            armGroupR.add(lowerR);
            const handR = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.15, 0.15), handMat);
            handR.position.y = -0.85;
            armGroupR.add(handR);
            armGroupR.position.set(0.6, 1.2, 0);
            robot.add(armGroupR);
            
            // Legs
            const legGroupL = new THREE.Group();
            const legGroupR = new THREE.Group();
            const upperLegMat = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.5, metalness: 0.4 });
            const lowerLegMat = new THREE.MeshStandardMaterial({ color: 0x777777, roughness: 0.5, metalness: 0.3 });
            
            // Left leg
            const upperLegL = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.45, 0.25), upperLegMat);
            upperLegL.position.y = -0.225;
            legGroupL.add(upperLegL);
            const lowerLegL = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.45, 0.22), lowerLegMat);
            lowerLegL.position.y = -0.55;
            legGroupL.add(lowerLegL);
            const footMat = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.6, metalness: 0.2 });
            const footL = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.1, 0.4), footMat);
            footL.position.set(0, -0.8, 0.05);
            legGroupL.add(footL);
            legGroupL.position.set(-0.3, 0.4, 0);
            robot.add(legGroupL);
            
            // Right leg
            const upperLegR = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.45, 0.25), upperLegMat);
            upperLegR.position.y = -0.225;
            legGroupR.add(upperLegR);
            const lowerLegR = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.45, 0.22), lowerLegMat);
            lowerLegR.position.y = -0.55;
            legGroupR.add(lowerLegR);
            const footR = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.1, 0.4), footMat);
            footR.position.set(0, -0.8, 0.05);
            legGroupR.add(footR);
            legGroupR.position.set(0.3, 0.4, 0);
            robot.add(legGroupR);
            
            scene.add(robot);
            
            // ---- Animation State ----
            const animCommand = 'ANIM_CMD';
            let animTime = 0;
            let isAnimating = false;
            let loopAnimation = false;
            let walkCycle = 0;
            let hasStarted = false;
            
            function resetRobot() {
                armGroupL.rotation.x = 0; armGroupL.rotation.z = 0;
                armGroupR.rotation.x = 0; armGroupR.rotation.z = 0;
                legGroupL.rotation.x = 0; legGroupL.rotation.z = 0;
                legGroupR.rotation.x = 0; legGroupR.rotation.z = 0;
                robot.position.y = 0; robot.rotation.x = 0; robot.rotation.z = 0;
                headGroup.rotation.x = 0; headGroup.rotation.y = 0;
                walkCycle = 0; controls.target.set(0, 0.8, 0);
            }
            
            function startCommand(cmd) {
                resetRobot();
                animTime = 0;
                isAnimating = true;
                loopAnimation = false;
                hasStarted = true;
                switch(cmd) {
                    case 'walk':
                        loopAnimation = true;
                        break;
                    case 'run':
                        loopAnimation = true;
                        break;
                    case 'jump':
                        loopAnimation = false;
                        break;
                    case 'wave':
                        loopAnimation = false;
                        break;
                    case 'backflip':
                        loopAnimation = false;
                        break;
                    default:
                        isAnimating = false;
                        hasStarted = false;
                        break;
                }
            }
            
            const valid = ['walk','run','jump','wave','backflip'];
            if (valid.includes(animCommand)) {
                startCommand(animCommand);
            } else {
                resetRobot();
            }
            
            // ---- Animation Loop ----
            const clock = new THREE.Clock();
            
            function animate() {
                requestAnimationFrame(animate);
                const delta = clock.getDelta();
                const time = clock.getElapsedTime();
                
                if (isAnimating && hasStarted) {
                    animTime += delta;
                    
                    if (loopAnimation) {
                        // Walk / Run – continuous
                        const speed = animCommand === 'walk' ? 1.0 : 2.0;
                        walkCycle += delta * speed * 2.5;
                        const swing = Math.sin(walkCycle) * 0.5;
                        legGroupL.rotation.x = swing;
                        legGroupR.rotation.x = -swing;
                        armGroupL.rotation.x = -swing * 0.8;
                        armGroupR.rotation.x = swing * 0.8;
                        robot.position.y = Math.abs(Math.sin(walkCycle)) * 0.05;
                    } else {
                        // One-shot animations
                        let duration = 1.2;
                        switch(animCommand) {
                            case 'jump': duration = 1.2; break;
                            case 'wave': duration = 2.0; break;
                            case 'backflip': duration = 1.5; break;
                        }
                        const progress = Math.min(animTime / duration, 1);
                        if (progress >= 1) {
                            isAnimating = false;
                            resetRobot();
                        } else {
                            const t = progress < 0.5 ? 2*progress*progress : 1 - Math.pow(-2*progress+2, 2)/2;
                            switch(animCommand) {
                                case 'jump':
                                    const jumpHeight = t < 0.5 ? t*2 : 2*(1-t);
                                    robot.position.y = jumpHeight * 0.6;
                                    controls.target.set(0, robot.position.y + 0.8, 0);
                                    armGroupL.rotation.x = -1.2 * (1 - Math.abs(progress-0.5)*2);
                                    armGroupR.rotation.x = -1.2 * (1 - Math.abs(progress-0.5)*2);
                                    legGroupL.rotation.x = 0.3 * (1 - Math.abs(progress-0.5)*2);
                                    legGroupR.rotation.x = 0.3 * (1 - Math.abs(progress-0.5)*2);
                                    break;
                                case 'wave':
                                    armGroupR.rotation.x = -1.2 + Math.sin(time * 6) * 0.5;
                                    armGroupR.rotation.z = 0.5;
                                    headGroup.rotation.y = 0.4;
                                    break;
                                case 'backflip':
                                    const angle = -t * Math.PI * 2;
                                    robot.rotation.x = angle;
                                    const jumpHeight = t < 0.5 ? t * 2 * 1.2 : 2 * (1 - t) * 1.2;
                                    robot.position.y = jumpHeight;
                                    controls.target.set(0, jumpHeight + 0.8, 0);
                                    armGroupL.rotation.x = -0.7;
                                    armGroupR.rotation.x = -0.7;
                                    legGroupL.rotation.x = 0.4;
                                    legGroupR.rotation.x = 0.4;
                                    break;
                            }
                        }
                    }
                }
                
                controls.update();
                renderer.render(scene, camera);
            }
            animate();
            
            // ---- Resize ----
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
    html = html_template.replace('ROBOT_NAME', robot_name)
    html = html.replace('COMMAND', command if command else 'Idle')
    html = html.replace('ANIM_CMD', anim_cmd)
    html = html.replace('MAIN_COLOR', str(main_color))
    html = html.replace('ACCENT_COLOR', str(accent))
    return html

# ========== SESSION STATE ==========
if 'robot_selected' not in st.session_state: st.session_state.robot_selected = "Red Titan"
if 'command' not in st.session_state: st.session_state.command = ""
if 'speak_text' not in st.session_state: st.session_state.speak_text = ""
if 'last_action' not in st.session_state: st.session_state.last_action = "idle"
if 'history' not in st.session_state: st.session_state.history = []
if 'last_spoken_text' not in st.session_state: st.session_state.last_spoken_text = ""
if 'last_spoken_audio' not in st.session_state: st.session_state.last_spoken_audio = None
if 'last_spoken_timestamp' not in st.session_state: st.session_state.last_spoken_timestamp = 0

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
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="https://raw.githubusercontent.com/Deslandes1/-Robotic-Control-Center-June-2026/main/Gesner%20Deslandes.png" 
             class="profile-img">
        <h3 class="profile-name">Gesner Deslandes</h3>
        <p class="profile-title">Engineer-in-Chief, GlobalInternet.py</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🤖 Robot Selection")
    robot_names = list(ROBOTS.keys())
    selected = st.selectbox("Select Robot", options=robot_names, index=robot_names.index(st.session_state.robot_selected), key="robot_select")
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
    st.markdown("*Walk and Run loop continuously. Jump, Wave, Backflip play once.*")
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
            audio_bytes = generate_audio(speak_input.strip(), "en")
            if audio_bytes:
                st.session_state.last_spoken_text = speak_input.strip()
                st.session_state.last_spoken_audio = audio_bytes
                st.session_state.last_spoken_timestamp = time.time()
                st.rerun()
            else:
                st.error("❌ Speech generation failed.")
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
    st.markdown(f"""
    <div class="status-panel">
        <div class="label">Current Robot</div>
        <div class="value">{st.session_state.robot_selected}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="status-panel">
        <div class="label">Last Action</div>
        <div class="value">{st.session_state.last_action if st.session_state.last_action != "idle" else "—"}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.last_spoken_audio and st.session_state.last_spoken_timestamp > 0:
        st.audio(st.session_state.last_spoken_audio, format="audio/mp3", autoplay=True)
        st.caption(f"🔊 Speaking: {st.session_state.last_spoken_text[:50]}...")
        if st.button("🔁 Replay Voice"): st.rerun()
    
    with st.expander("📜 Backstage – Command History", expanded=False):
        if st.session_state.history:
            for cmd, status in reversed(st.session_state.history[-10:]):
                st.markdown(f"""
                <div style="background: rgba(0,212,255,0.05); border-left: 3px solid #00d4ff; padding: 5px 10px; margin: 5px 0; border-radius: 4px;">
                    <span style="color: #00d4ff;">▶️</span> <span style="color: #ffffff;">{cmd}</span><br>
                    <span style="color: #8899bb; font-size: 0.8rem;">{status}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No commands yet. Send a command from the sidebar.")

# ---------- Speak ----------
if st.session_state.last_spoken_text and st.session_state.last_spoken_audio:
    if not any("Speak:" in h[0] and st.session_state.last_spoken_text in h[0] for h in st.session_state.history):
        st.session_state.history.append((f"Speak: {st.session_state.last_spoken_text}", "Speech played"))
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[-20:]

# ========== FOOTER ==========
st.markdown("""
<div class="footer">
    <p>© 2026 GlobalInternet.py Online Software Company</p>
    <p>Built by <strong>Gesner Deslandes</strong> | (509) 4738-5663 | deslandes78@gmail.com</p>
    <p style="font-size:0.8rem; color:#445566;">🤖 Simulated robot control – ready for real-world hardware integration.</p>
</div>
""", unsafe_allow_html=True)
