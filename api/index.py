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
        #info {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #00ffff;
            font-size: 1.8rem;
            text-align: center;
            text-shadow: 0 0 20px #00ffff, 0 0 40px #0088ff;
            background: rgba(0,0,0,0.75);
            padding: 2rem 3rem;
            border: 2px solid #00ffff;
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(0,255,255,0.3);
            z-index: 10;
            white-space: pre-line;
            line-height: 1.6;
            pointer-events: none;
            animation: fadeIn 0.3s ease;
        }
        #info.show { display: block; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            to   { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
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
            cols = Math.floor(canvas.width / 20);
            drops = Array(cols).fill(1);
        }
        window.addEventListener('resize', resize);
        resize();

        const chars = 'ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';

        function draw() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ffff';
            ctx.font = '20px monospace';

            for (let i = 0; i < drops.length; i++) {
                const char = chars[Math.floor(Math.random() * chars.length)];
                const x = i * 20;
                const y = drops[i] * 20;
                ctx.fillStyle = 'rgba(0, 255, 255, 0.25)';
                ctx.fillText(char, x, y);
                ctx.fillStyle = '#00ffff';
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#00ffff';
                ctx.fillText(char, x, y - 20);
                ctx.fillText(chars[Math.floor(Math.random() * chars.length)], x, y - 20);
                ctx.shadowBlur = 0;
                if (y > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(draw, 50);

        const infoBox = document.getElementById('info');
        canvas.addEventListener('click', () => {
            infoBox.classList.add('show');
            clearTimeout(window.infoTimeout);
            window.infoTimeout = setTimeout(() => infoBox.classList.remove('show'), 8000);
        });
        infoBox.addEventListener('click', () => {
            infoBox.classList.remove('show');
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
