import http.server
import socketserver
import urllib.request
import urllib.error
import json
import urllib.parse
import webbrowser
import threading
import time
import os
import random
import string

PORT = 8080
WORDS = []

def load_words():
    global WORDS
    if os.path.exists('words.txt'):
        print("Loading words from words.txt...")
        with open('words.txt', 'r') as f:
            WORDS = [w.strip().lower() for w in f.readlines() if 3 <= len(w.strip()) <= 16]
    else:
        print("Downloading rare word dictionary...")
        try:
            # Fetch the top 10000 english words
            req = urllib.request.Request('https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt')
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('utf-8')
                # Filter for cool rare lengths (3 to 5 letters)
                WORDS = [w.strip() for w in content.split('\n') if 3 <= len(w.strip()) <= 5]
            
            # Save it so we don't have to download it next time
            with open('words.txt', 'w') as f:
                f.write('\n'.join(WORDS))
            print("Saved words to words.txt!")
        except Exception as e:
            print("Failed to download dictionary, using fallback words.", e)
            WORDS = ["aether", "void", "nexus", "rune", "flux", "nova", "apex", "echo", "zeal", "dusk", "rift", "halo", "omen", "myth"]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quadra | Elite Forger</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg-color: #050507; 
            --panel-bg: rgba(15, 15, 20, 0.7); 
            --panel-border: rgba(255, 42, 85, 0.2); 
            --primary: #ff2a55; 
            --primary-glow: rgba(255, 42, 85, 0.6); 
            --secondary: #1a1c23; 
            --text-main: #f0f0f0; 
            --text-muted: #6a6d78; 
            --success: #00ff88; 
            --success-glow: rgba(0, 255, 136, 0.4);
            --warning: #ffb82a; 
            --danger: #ff2a55; 
            --font-main: 'Outfit', sans-serif; 
            --font-mono: 'JetBrains Mono', monospace;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: var(--font-main); 
            background-color: var(--bg-color); 
            color: var(--text-main); 
            min-height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            overflow-x: hidden; 
            padding: 2rem; 
            background-image: 
                linear-gradient(rgba(255, 42, 85, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 42, 85, 0.03) 1px, transparent 1px);
            background-size: 30px 30px;
        }
        
        /* Cyber grid animation */
        .cyber-grid {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            z-index: -2;
            background: 
                linear-gradient(transparent 0%, rgba(255, 42, 85, 0.05) 50%, transparent 100%);
            background-size: 100% 4px;
            animation: scanline 8s linear infinite;
            pointer-events: none;
        }
        
        @keyframes scanline {
            0% { transform: translateY(-100vh); }
            100% { transform: translateY(100vh); }
        }

        .background-effects { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; overflow: hidden; }
        .glow-orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.3; animation: float 15s infinite alternate ease-in-out; }
        .orb-1 { width: 40vw; height: 40vw; background: var(--primary); top: -10vw; left: -10vw; }
        .orb-2 { width: 30vw; height: 30vw; background: #2a00ff; bottom: -5vw; right: -5vw; animation-delay: -5s; }
        @keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(3vw, 3vh) scale(1.1); } }
        
        .container { width: 100%; max-width: 750px; display: flex; flex-direction: column; gap: 1.5rem; z-index: 1; perspective: 1000px; }
        
        .glass-panel { 
            background: var(--panel-bg); 
            backdrop-filter: blur(24px); 
            border: 1px solid var(--panel-border); 
            border-radius: 16px; 
            padding: 2rem; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.6), inset 0 0 20px rgba(255, 42, 85, 0.05); 
            transition: transform 0.3s ease, border-color 0.3s;
        }
        .glass-panel:hover { border-color: rgba(255, 42, 85, 0.4); }
        
        header { text-align: center; padding: 2rem; position: relative; }
        header::after {
            content: ''; position: absolute; bottom: 0; left: 20%; right: 20%; height: 1px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
        }
        
        .logo { 
            font-size: 4.5rem; font-weight: 900; letter-spacing: 10px; 
            background: linear-gradient(135deg, #ffffff 0%, var(--primary) 100%); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
            margin-bottom: 0.5rem; text-shadow: 0 0 30px var(--primary-glow);
        }
        .subtitle { color: var(--text-muted); font-weight: 500; font-size: 1.2rem; letter-spacing: 4px; text-transform: uppercase; }
        
        .controls { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .input-group { display: flex; flex-direction: column; gap: 0.5rem; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
        .input-group.full { grid-column: span 2; }
        .input-group label { font-weight: 500; font-size: 0.9rem; color: #8a8d98; text-transform: uppercase; letter-spacing: 1px; }
        .input-group input, .input-group select { 
            background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; 
            padding: 0.8rem 1rem; color: white; font-family: var(--font-mono); font-size: 1.1rem; 
            transition: all 0.3s; outline: none;
        }
        .input-group input:focus, .input-group select:focus { border-color: var(--primary); box-shadow: 0 0 15px var(--primary-glow); }
        
        .button-group { grid-column: span 2; display: flex; justify-content: center; margin-top: 0.5rem; }
        .btn { 
            padding: 1.2rem 4rem; border: none; border-radius: 8px; font-family: inherit; font-weight: 900; 
            font-size: 1.2rem; letter-spacing: 4px; cursor: pointer; transition: all 0.3s ease; width: 100%; 
            position: relative; overflow: hidden; text-transform: uppercase;
        }
        .btn-primary { 
            background: linear-gradient(45deg, #ff0033, var(--primary)); color: white; 
            box-shadow: 0 10px 30px var(--primary-glow); border: 1px solid #ff476e;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 15px 50px var(--primary-glow); filter: brightness(1.2); }
        .btn-danger { background: rgba(255, 42, 85, 0.1); color: var(--danger); border: 1px solid var(--danger); }
        .btn-danger:hover { background: rgba(255, 42, 85, 0.2); }
        .hidden { display: none !important; }
        
        .status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        .status-badge { padding: 0.4rem 1.2rem; border-radius: 4px; font-size: 0.8rem; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; border: 1px solid transparent; }
        .status-badge.idle { background: rgba(255,255,255,0.05); color: #aaa; border-color: rgba(255,255,255,0.1); }
        .status-badge.running { background: rgba(42, 255, 128, 0.1); color: var(--success); border-color: var(--success); box-shadow: 0 0 10px var(--success-glow); }
        
        .progress-stats { display: flex; justify-content: space-between; margin-bottom: 0.8rem; font-size: 0.95rem; color: var(--text-muted); font-family: var(--font-mono); }
        .progress-bar-bg { width: 100%; height: 6px; background: rgba(0,0,0,0.5); border-radius: 3px; overflow: hidden;}
        .progress-bar-fill { height: 100%; width: 0%; background: var(--primary); box-shadow: 0 0 15px var(--primary); transition: width 0.2s; }
        
        .active-username { 
            text-align: center; font-size: 3.5rem; font-weight: 900; letter-spacing: 12px; 
            min-height: 5rem; display: flex; align-items: center; justify-content: center; 
            background: rgba(0,0,0,0.4); border-radius: 12px; margin-top: 1.5rem;
            font-family: var(--font-mono); border: 1px solid rgba(255,255,255,0.05);
            transition: all 0.2s;
        }
        .active-username.success { color: var(--success); text-shadow: 0 0 30px var(--success-glow); border-color: var(--success); transform: scale(1.02); }
        .active-username.taken { color: #3a3d48; text-decoration: line-through; }
        
        .results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1rem; max-height: 250px; overflow-y: auto; padding-right: 5px;}
        .results-grid::-webkit-scrollbar { width: 6px; }
        .results-grid::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
        .results-grid::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 3px; }
        
        .result-card { 
            background: rgba(0, 255, 136, 0.05); border: 1px solid rgba(0, 255, 136, 0.3); 
            border-radius: 8px; padding: 1.2rem; text-align: center; font-weight: 700; 
            font-size: 1.2rem; color: var(--success); cursor: pointer; font-family: var(--font-mono);
            transition: all 0.2s;
        }
        .result-card:hover { transform: translateY(-3px); background: rgba(0, 255, 136, 0.15); box-shadow: 0 5px 15px var(--success-glow); }
        .empty-state { text-align: center; color: var(--text-muted); padding: 2rem 0; font-family: var(--font-mono); font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="cyber-grid"></div>
    <div class="background-effects">
        <div class="glow-orb orb-1"></div>
        <div class="glow-orb orb-2"></div>
    </div>
    <main class="container">
        <header class="glass-panel">
            <h1 class="logo">QUADRA</h1>
            <p class="subtitle">Elite Name Forger</p>
        </header>
        <section class="controls glass-panel">
            <div class="input-group full">
                <label>Search Mode</label>
                <select id="mode">
                    <option value="words">Rare Dictionary Words (3-5 letters)</option>
                    <option value="random">Random 4-Letter Generated</option>
                </select>
            </div>
            <div class="input-group">
                <label>Target Attempts</label>
                <input type="number" id="attempts" value="100">
            </div>
            <div class="input-group">
                <label>Delay (Seconds)</label>
                <input type="number" id="delay" value="1.5" step="0.1">
            </div>
            <div class="button-group">
                <button id="startBtn" class="btn btn-primary">INITIALIZE SEQUENCE</button>
                <button id="stopBtn" class="btn btn-danger hidden">ABORT SEQUENCE</button>
            </div>
        </section>
        <section class="status glass-panel">
            <div class="status-header">
                <h2 style="font-weight: 500; font-size: 1.2rem; letter-spacing: 2px;">LIVE TELEMETRY</h2>
                <span id="currentStatus" class="status-badge idle">STANDBY</span>
            </div>
            <div>
                <div class="progress-stats">
                    <span id="checkedCount">CHK: 0 / 100</span>
                    <span id="foundCount">FND: 0</span>
                </div>
                <div class="progress-bar-bg"><div id="progressBar" class="progress-bar-fill"></div></div>
            </div>
            <div id="activeUsername" class="active-username">_</div>
        </section>
        <section class="results glass-panel">
            <div class="results-header">
                <h2 style="font-weight: 500; font-size: 1.2rem; letter-spacing: 2px;">SECURED NAMES</h2>
            </div>
            <div id="resultsList" class="results-grid"></div>
            <div id="emptyState" class="empty-state">NO ASSETS ACQUIRED YET.</div>
        </section>
    </main>

    <script>
        let isRunning = false, totalChecked = 0, attemptsTarget = 100, delay = 2000, availableNames = [];
        const el = id => document.getElementById(id);
        
        async function searchLoop() {
            while (isRunning && totalChecked < attemptsTarget) {
                try {
                    const mode = el('mode').value;
                    
                    // 1. Ask backend for the next target based on mode
                    const targetRes = await fetch(`/api/next_target?mode=${mode}`);
                    const targetData = await targetRes.json();
                    const username = targetData.name;
                    
                    el('activeUsername').textContent = username;
                    el('activeUsername').className = 'active-username';

                    // 2. Ask backend to check it
                    const res = await fetch(`/api/check?name=${username}`);
                    const data = await res.json();
                    totalChecked++;

                    if (data.available) {
                        el('activeUsername').classList.add('success');
                        availableNames.push(username);
                        el('emptyState').style.display = 'none';
                        const card = document.createElement('div');
                        card.className = 'result-card';
                        card.textContent = username;
                        card.onclick = () => {
                            navigator.clipboard.writeText(username);
                            card.textContent = 'COPIED';
                            setTimeout(() => card.textContent = username, 1000);
                        };
                        el('resultsList').prepend(card);
                    } else if (data.status === 'Rate Limited') {
                        el('activeUsername').textContent = 'RATE LIMIT';
                        el('currentStatus').textContent = 'BLOCKED';
                        await new Promise(r => setTimeout(r, delay * 5));
                        continue;
                    } else {
                        el('activeUsername').classList.add('taken');
                    }
                } catch(e) { totalChecked++; }

                el('progressBar').style.width = Math.min((totalChecked/attemptsTarget)*100, 100) + '%';
                el('checkedCount').textContent = `CHK: ${totalChecked} / ${attemptsTarget}`;
                el('foundCount').textContent = `FND: ${availableNames.length}`;
                
                if (isRunning) await new Promise(r => setTimeout(r, delay));
            }
            if(isRunning) stopSearch('COMPLETED');
        }

        function startSearch() {
            if (isRunning) return;
            attemptsTarget = parseInt(el('attempts').value) || 100;
            delay = (parseFloat(el('delay').value) || 2.0) * 1000;
            totalChecked = 0; availableNames = [];
            el('resultsList').innerHTML = '';
            el('emptyState').style.display = 'block';
            el('progressBar').style.width = '0%';
            isRunning = true;
            el('startBtn').classList.add('hidden');
            el('stopBtn').classList.remove('hidden');
            el('currentStatus').className = 'status-badge running';
            el('currentStatus').textContent = 'ACTIVE';
            searchLoop();
        }

        function stopSearch(reason='ABORTED') {
            isRunning = false;
            el('startBtn').classList.remove('hidden');
            el('stopBtn').classList.add('hidden');
            el('currentStatus').className = 'status-badge idle';
            el('currentStatus').textContent = reason;
        }

        el('startBtn').onclick = startSearch;
        el('stopBtn').onclick = () => stopSearch();
    </script>
</body>
</html>"""

class QuadraHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress logging

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
            return
            
        if parsed.path == '/api/next_target':
            query = urllib.parse.parse_qs(parsed.query)
            mode = query.get('mode', ['random'])[0]
            
            if mode == 'words' and WORDS:
                name = random.choice(WORDS)
            else:
                VALID = string.ascii_lowercase + string.digits + "_"
                name = "".join(random.choice(VALID) for _ in range(4))
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"name": name}).encode())
            return
            
        if parsed.path == '/api/check':
            query = urllib.parse.parse_qs(parsed.query)
            username = query.get('name', [''])[0]
            
            if not username:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Missing name"}')
                return

            url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
            status_code, available, msg = 500, False, "Error"
            
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as res:
                    if res.getcode() == 200:
                        status_code = 200
                        msg = "Taken"
            except urllib.error.HTTPError as e:
                status_code = e.code
                if e.code == 404:
                    available = True
                    msg = "Available"
                elif e.code == 429:
                    msg = "Rate Limited"
            except Exception as e:
                msg = str(e)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "username": username,
                "available": available,
                "status": msg
            }).encode())
            return

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), QuadraHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    load_words()
    print(f"Starting Quadra Server on http://127.0.0.1:{PORT}")
    threading.Thread(target=start_server, daemon=True).start()
    
    # Automatically open the browser
    time.sleep(1)
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    
    print("Quadra is running! Close this window to stop it.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
