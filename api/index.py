from flask import Flask, render_template_string, send_from_directory
import os

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dream/loaded</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: black;
            overflow: hidden;
            height: 100vh;
            font-family: 'Courier New', monospace;
            cursor: crosshair;
        }
        canvas { display: block; position: fixed; top: 0; left: 0; width: 100%; height: 100%; }
        #prompt {
            position: fixed;
            bottom: 3rem;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 60, 60, 0.7);
            font-size: 1.3rem;
            letter-spacing: 1px;
            z-index: 5;
            pointer-events: none;
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 1; }
        }
        #info {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #ff3333;
            font-size: 1.6rem;
            text-align: center;
            text-shadow: 0 0 15px #ff0000, 0 0 30px #aa0000;
            background: rgba(0,0,0,0.85);
            padding: 2rem 2.5rem;
            border: 2px solid #ff3333;
            border-radius: 10px;
            box-shadow: 0 0 25px rgba(255,0,0,0.25);
            z-index: 10;
            animation: fadeIn 0.3s ease;
            max-width: 90vw;
        }
        #info.show { display: block; }
        
        /* Profile Picture Styling */
        #pfp {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 2px solid #ff3333;
            box-shadow: 0 0 15px #ff0000;
            margin: 0 auto 1.5rem auto;
            display: block;
            object-fit: cover;
        }

        .text-content {
            white-space: pre-line;
            line-height: 1.6;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
            to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
        #volume-control {
            position: fixed;
            top: 1rem;
            left: 1rem;
            z-index: 20;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(0,0,0,0.7);
            padding: 0.5rem 1rem;
            border: 1px solid rgba(255,50,50,0.3);
            border-radius: 8px;
        }
        #volume-control label {
            color: #ff4444;
            font-size: 0.8rem;
            font-family: 'Courier New', monospace;
            letter-spacing: 1px;
        }
        #volume-control input[type="range"] {
            width: 80px;
            height: 4px;
            -webkit-appearance: none;
            appearance: none;
            background: #ff3333;
            border-radius: 2px;
            outline: none;
            cursor: pointer;
        }
        #volume-control input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff3333;
            cursor: pointer;
            box-shadow: 0 0 6px #ff0000;
        }
        #volume-control input[type="range"]::-moz-range-thumb {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff3333;
            cursor: pointer;
            border: none;
        }
        #vol-label {
            color: #ff6666;
            font-size: 0.8rem;
            min-width: 35px;
            text-align: center;
        }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    <div id="prompt">click on the screen to learn about me!</div>
    
    <div id="info">
        <img id="pfp" src="/pfp.webp" alt="pfp">
        <div class="text-content">Hey, I'm dream/loaded
            I'm learning more about
            C++, C#, HTML
            ...ye, that's about all</div>
    </div>

    <audio id="bg-music" loop preload="auto">
        <source src="https://files.catbox.moe/2sreco.mp3" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>

    <div id="volume-control">
        <label>♪ VOL</label>
        <input type="range" id="volume-slider" min="0" max="100" value="50">
        <span id="vol-label">50%</span>
    </div>

    <script>
        // ── Matrix Rain Effect ──
        const canvas = document.getElementById('matrix');
        const ctx = canvas.getContext('2d');
        let cols, drops;

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            cols = Math.floor(canvas.width / 18);
            drops = Array(cols).fill(1);
        }
        window.addEventListener('resize', resize);
        resize();

        function draw() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.07)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            for (let i = 0; i < drops.length; i++) {
                const x = i * 18;
                const y = drops[i] * 18;
                ctx.fillStyle = 'rgba(255, 50, 50, 0.2)';
                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = '#ff3333';
                ctx.shadowBlur = 12;
                ctx.shadowColor = '#ff0000';
                ctx.beginPath();
                ctx.arc(x, y - 18, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;

                if (y > canvas.height + 20 && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(draw, 40);

        // ── Audio & UI ──
        const infoBox = document.getElementById('info');
        const prompt = document.getElementById('prompt');
        const audio = document.getElementById('bg-music');
        const slider = document.getElementById('volume-slider');
        const volLabel = document.getElementById('vol-label');

        audio.volume = 0.5;

        function startAudio() {
            // Force reload if state is stuck
            if (audio.readyState === 0) {
                audio.load();
            }
            
            audio.play().then(() => {
                print("Audio playing successfully.");
            }).catch(err => {
                print("Playback blocked or failed. Trying reload...", err);
                // Fallback attempt
                setTimeout(() => {
                    audio.play().catch(e => console.log("Final playback block:", e));
                }, 100);
            });
        }

        // Volume control
        slider.addEventListener('input', () => {
            const vol = slider.value / 100;
            audio.volume = vol;
            volLabel.textContent = Math.round(vol * 100) + '%';
        });

        // Click to play + show info
        canvas.addEventListener('click', () => {
            startAudio();
            infoBox.classList.add('show');
            prompt.style.display = 'none';
        });

        // Clicking info closes it
        infoBox.addEventListener('click', (e) => {
            e.stopPropagation();
            infoBox.classList.remove('show');
            prompt.style.display = 'block';
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

# Route to serve the profile picture from the local root folder
@app.route('/pfp.webp')
def serve_pfp():
    return send_from_directory(os.getcwd(), 'pfp.webp')

if __name__ == '__main__':
    app.run(debug=True)
