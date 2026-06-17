from flask import Flask, render_template_string

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
            color: rgba(255, 60, 60, 0.6);
            font-size: 0.9rem;
            letter-spacing: 1px;
            z-index: 5;
            pointer-events: none;
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50%      { opacity: 1; }
        }
        #info {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #ff3333;
            font-size: 1.2rem;
            text-align: center;
            text-shadow: 0 0 15px #ff0000, 0 0 30px #aa0000;
            background: rgba(0,0,0,0.8);
            padding: 1.2rem 2rem;
            border: 1px solid #ff3333;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(255,0,0,0.2);
            z-index: 10;
            white-space: pre-line;
            line-height: 1.5;
            pointer-events: none;
            animation: fadeIn 0.3s ease;
        }
        #info.show { display: block; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
            to   { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    <div id="prompt">click on the screen to learn about me!</div>
    <div id="info">
        Hey, I'm dream/loaded
        I'm learning more about
        C++, C#, HTML
        ...ye, that's about all
    </div>
    <script>
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

                // tail dot
                ctx.fillStyle = 'rgba(255, 50, 50, 0.2)';
                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fill();

                // head dot - brighter
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

        const infoBox = document.getElementById('info');
        const prompt = document.getElementById('prompt');

        canvas.addEventListener('click', () => {
            infoBox.classList.add('show');
            prompt.style.display = 'none';
            clearTimeout(window.infoTimeout);
            window.infoTimeout = setTimeout(() => {
                infoBox.classList.remove('show');
                prompt.style.display = 'block';
            }, 8000);
        });
        infoBox.addEventListener('click', () => {
            infoBox.classList.remove('show');
            prompt.style.display = 'block';
            clearTimeout(window.infoTimeout);
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run()
