<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jasir Abdul Hameed — Web Dev → AI/ML</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#08152B;
    --panel:#0B1F3A;
    --line:#1B4B8F;
    --accent:#4FA3FF;
    --text:#E8F1FF;
    --dim:#5C82AD;
    --pivot:#FF6B4A;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  body{
    background:var(--bg);
    color:var(--text);
    font-family:'JetBrains Mono',monospace;
    overflow-x:hidden;
  }
  .display{font-family:'Space Grotesk',sans-serif;}

  /* grid backdrop */
  .grid-bg{
    position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image:
      linear-gradient(var(--line) 1px, transparent 1px),
      linear-gradient(90deg, var(--line) 1px, transparent 1px);
    background-size:48px 48px;
    opacity:.16;
  }

  /* corner marks, fixed frame */
  .frame-mark{position:fixed; width:22px; height:22px; border-color:var(--accent); border-style:solid; z-index:5; opacity:.8;}
  .fm-tl{top:20px; left:20px; border-width:2px 0 0 2px;}
  .fm-tr{top:20px; right:20px; border-width:2px 2px 0 0;}
  .fm-bl{bottom:20px; left:20px; border-width:0 0 2px 2px;}
  .fm-br{bottom:20px; right:20px; border-width:0 2px 2px 0;}

  section{position:relative; z-index:1; padding:120px 8vw;}

  /* HERO */
  #hero{
    min-height:100vh; display:flex; align-items:center;
    padding:0 8vw;
  }
  .hero-inner{display:flex; align-items:center; justify-content:space-between; width:100%; gap:40px; flex-wrap:wrap;}
  .hero-text{max-width:560px;}
  .eyebrow{
    color:var(--accent); font-size:12px; letter-spacing:3px;
    display:flex; align-items:center; gap:10px; margin-bottom:24px;
    opacity:0; transform:translateY(10px); animation:rise .7s ease forwards .1s;
  }
  .eyebrow::before{content:''; width:24px; height:1px; background:var(--accent);}
  h1{
    font-size:clamp(38px,5.5vw,64px); line-height:1.05; font-weight:700;
    letter-spacing:-1px;
    opacity:0; transform:translateY(14px); animation:rise .8s ease forwards .25s;
  }
  h1 span{color:var(--accent);}
  .hero-sub{
    margin-top:22px; color:var(--dim); font-size:15px; line-height:1.7; max-width:460px;
    opacity:0; transform:translateY(14px); animation:rise .8s ease forwards .4s;
  }
  .hero-links{
    margin-top:32px; display:flex; gap:14px; flex-wrap:wrap;
    opacity:0; transform:translateY(14px); animation:rise .8s ease forwards .55s;
  }
  .btn{
    font-family:'JetBrains Mono',monospace; font-size:13px; letter-spacing:.5px;
    padding:12px 20px; border:1px solid var(--line); color:var(--text);
    text-decoration:none; transition:all .25s ease; background:transparent;
  }
  .btn:hover{border-color:var(--accent); color:var(--accent); background:rgba(79,163,255,.06);}
  .btn.primary{border-color:var(--accent); color:var(--bg); background:var(--accent);}
  .btn.primary:hover{background:transparent; color:var(--accent);}

  #canvas-wrap{width:min(46vw,480px); height:min(46vw,480px); min-width:280px; min-height:280px; opacity:0; animation:rise 1s ease forwards .3s;}
  #canvas-wrap canvas{cursor:grab;}
  #canvas-wrap canvas:active{cursor:grabbing;}
  .canvas-caption{text-align:center; font-size:10px; color:var(--dim); letter-spacing:2px; margin-top:8px;}

  @keyframes rise{to{opacity:1; transform:translateY(0);}}

  /* SECTION HEADER SYSTEM */
  .sec-head{display:flex; align-items:baseline; gap:18px; margin-bottom:48px;}
  .sec-num{color:var(--accent); font-size:13px; font-weight:700;}
  .sec-title{font-size:22px; letter-spacing:1px; font-family:'Space Grotesk',sans-serif; font-weight:500;}
  .sec-rule{flex:1; height:1px; background:var(--line);}

  .reveal{opacity:0; transform:translateY(24px); transition:opacity .7s ease, transform .7s ease;}
  .reveal.in{opacity:1; transform:translateY(0);}

  /* PIVOT SECTION */
  #pivot{background:linear-gradient(180deg, transparent, rgba(255,107,74,.04), transparent);}
  .pivot-list{list-style:none; max-width:640px;}
  .pivot-list li{
    display:flex; gap:16px; padding:18px 0; border-bottom:1px solid var(--line);
    font-size:15px; color:var(--dim); align-items:flex-start;
  }
  .pivot-list li b{color:var(--text); font-weight:500;}
  .chk{color:var(--pivot); font-size:13px; margin-top:2px;}
  .pivot-note{margin-top:28px; color:var(--dim); font-size:14px; line-height:1.8; max-width:600px;}
  .pivot-note em{color:var(--pivot); font-style:normal;}

  /* WORK */
  .work-card{
    display:grid; grid-template-columns:1.1fr .9fr; gap:40px; align-items:center;
    border:1px solid var(--line); padding:36px; margin-bottom:28px; background:var(--panel);
    transition:border-color .3s ease;
  }
  .work-card:hover{border-color:var(--accent);}
  .work-card img{width:100%; display:block; border:1px solid var(--line);}
  .work-title{font-family:'Space Grotesk',sans-serif; font-size:22px; font-weight:500; margin-bottom:10px;}
  .work-desc{color:var(--dim); font-size:14px; line-height:1.75; margin:14px 0;}
  .chips{display:flex; gap:8px; flex-wrap:wrap; margin-bottom:6px;}
  .chip{font-size:11px; padding:5px 10px; border:1px solid var(--line); color:var(--accent);}
  .work-links{display:flex; gap:16px; margin-top:16px;}
  .work-links a{color:var(--accent); text-decoration:none; font-size:13px;}
  .work-links a:hover{text-decoration:underline;}
  @media(max-width:820px){.work-card{grid-template-columns:1fr;}}

  .solo-card{border:1px solid var(--line); padding:30px; background:var(--panel);}

  /* STACK */
  .stack-group{margin-bottom:36px;}
  .stack-label{font-size:11px; letter-spacing:2px; color:var(--dim); margin-bottom:14px;}
  .stack-chips{display:flex; flex-wrap:wrap; gap:10px;}
  .stack-chip{
    padding:9px 16px; border:1px solid var(--line); font-size:13px;
    transition:all .25s ease;
  }
  .stack-chip.core{border-color:var(--accent); color:var(--text);}
  .stack-chip.learning{color:var(--dim); border-style:dashed;}
  .stack-chip:hover{transform:translateY(-2px); border-color:var(--accent); color:var(--accent);}

  /* FOOTER */
  #contact{text-align:center; padding-bottom:100px;}
  #contact .sec-head{justify-content:center;}
  .contact-links{display:flex; gap:18px; justify-content:center; margin-top:20px;}
  footer{text-align:center; padding:30px; color:var(--dim); font-size:11px; letter-spacing:1px;}

  @media (prefers-reduced-motion: reduce){
    *{animation:none !important; transition:none !important;}
  }
</style>
</head>
<body>

<div class="grid-bg"></div>
<div class="frame-mark fm-tl"></div>
<div class="frame-mark fm-tr"></div>
<div class="frame-mark fm-bl"></div>
<div class="frame-mark fm-br"></div>

<section id="hero">
  <div class="hero-inner">
    <div class="hero-text">
      <div class="eyebrow">JASIR ABDUL HAMEED · KERALA, IN</div>
      <h1 class="display">Web dev,<br>rebuilding for <span>AI/ML.</span></h1>
      <p class="hero-sub">Full-stack developer (React · Node · Flutter) with strong Python, DSA, and math foundations — currently turning that into shipped ML systems, not just talking about the pivot.</p>
      <div class="hero-links">
        <a class="btn primary" href="#work">View work</a>
        <a class="btn" href="mailto:jasirlvl@gmail.com">Contact</a>
      </div>
    </div>
    <div>
      <div id="canvas-wrap"></div>
      <div class="canvas-caption">DRAG TO ROTATE · SCROLL TO WATCH THE PIVOT</div>
    </div>
  </div>
</section>

<section id="pivot">
  <div class="sec-head reveal">
    <span class="sec-num">01</span>
    <span class="sec-title display">Currently building toward</span>
    <span class="sec-rule"></span>
  </div>
  <ul class="pivot-list reveal">
    <li><span class="chk">▸</span><span><b>Andrew Ng's ML Specialization</b> — foundations, done properly</span></li>
    <li><span class="chk">▸</span><span><b>fast.ai</b> — practical deep learning, applied first</span></li>
    <li><span class="chk">▸</span><span><b>SQL + MLOps on AWS</b> — the part most self-taught devs skip</span></li>
  </ul>
  <p class="pivot-note reveal">Deepening Python without AI-assist — writing it, not prompting it. Next milestone: <em>one shipped project with a trained model behind it</em>, not just a UI on top of an API.</p>
</section>

<section id="work">
  <div class="sec-head reveal">
    <span class="sec-num">02</span>
    <span class="sec-title display">Featured work</span>
    <span class="sec-rule"></span>
  </div>

  <div class="work-card reveal">
    <div>
      <div class="work-title display">FitWithJu</div>
      <div class="chips">
        <span class="chip">Node</span><span class="chip">Express</span><span class="chip">MongoDB</span><span class="chip">HTML/CSS/JS</span>
      </div>
      <p class="work-desc">Full-stack gym platform — trainer profiles, pricing, fitness calculator, contact system. Refactored from one monolithic HTML file into a proper client/server structure, deployed frontend on Netlify and backend on Render with MongoDB Atlas. Proves I can carry a project from messy first draft through data modeling, API design, and a real deployment pipeline.</p>
      <div class="work-links">
        <a href="https://fitwithu0.netlify.app" target="_blank">→ live site</a>
        <a href="https://github.com/jasirjru/FitWithJu" target="_blank">→ source</a>
      </div>
    </div>
    <img src="assets/fitwithu-preview.png" alt="FitWithJu preview">
  </div>

  <div class="solo-card reveal">
    <div class="work-title display">Customer support chatbot</div>
    <div class="chips">
      <span class="chip">Node.js</span><span class="chip">Express</span><span class="chip">OpenAI API</span>
    </div>
    <p class="work-desc">Service wrapping the OpenAI API for support conversations — conversation routing and context handling, not a bare API call. First real AI-integration project, and the clearest evidence of the pivot in progress.</p>
  </div>
</section>

<section id="stack">
  <div class="sec-head reveal">
    <span class="sec-num">03</span>
    <span class="sec-title display">Stack</span>
    <span class="sec-rule"></span>
  </div>
  <div class="stack-group reveal">
    <div class="stack-label">CORE</div>
    <div class="stack-chips">
      <span class="stack-chip core">Python</span>
      <span class="stack-chip core">JavaScript</span>
      <span class="stack-chip core">Node.js</span>
      <span class="stack-chip core">Express</span>
      <span class="stack-chip core">MongoDB</span>
      <span class="stack-chip core">Flutter</span>
      <span class="stack-chip core">Dart</span>
      <span class="stack-chip core">Git</span>
    </div>
  </div>
  <div class="stack-group reveal">
    <div class="stack-label">LEARNING NOW</div>
    <div class="stack-chips">
      <span class="stack-chip learning">TensorFlow</span>
      <span class="stack-chip learning">AWS</span>
      <span class="stack-chip learning">SQL</span>
    </div>
  </div>
</section>

<section id="contact">
  <div class="sec-head reveal">
    <span class="sec-num">04</span>
    <span class="sec-title display">Contact</span>
    <span class="sec-rule"></span>
  </div>
  <div class="contact-links reveal">
    <a class="btn primary" href="https://www.linkedin.com/in/jasir-abdul-hameed-762388338/" target="_blank">LinkedIn</a>
    <a class="btn" href="mailto:jasirlvl@gmail.com">jasirlvl@gmail.com</a>
    <a class="btn" href="https://github.com/jasirjru" target="_blank">GitHub</a>
  </div>
</section>

<footer>REV 01 · BUILT WEB-FIRST, SHIPPING AI-FIRST</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
  // ---- Scroll reveal ----
  const revealEls = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {threshold:.15});
  revealEls.forEach(el=>io.observe(el));

  // ---- 3D signature: draggable wireframe icosahedron that shifts color on scroll ----
  const wrap = document.getElementById('canvas-wrap');
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.z = 5.2;

  const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
  function sizeRenderer(){
    const s = wrap.clientWidth || 320;
    renderer.setSize(s, s);
    camera.aspect = 1;
    camera.updateProjectionMatrix();
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  wrap.appendChild(renderer.domElement);
  sizeRenderer();
  window.addEventListener('resize', sizeRenderer);

  const geo = new THREE.IcosahedronGeometry(2, 1);
  const matBlue = new THREE.LineBasicMaterial({color:0x4FA3FF, transparent:true, opacity:0.85});
  const wireframe = new THREE.WireframeGeometry(geo);
  const mesh = new THREE.LineSegments(wireframe, matBlue);
  scene.add(mesh);

  // faint inner solid for depth
  const solidMat = new THREE.MeshBasicMaterial({color:0x0B1F3A, transparent:true, opacity:0.25});
  const solid = new THREE.Mesh(geo, solidMat);
  scene.add(solid);

  let targetRotX = 0.3, targetRotY = 0.4;
  let curRotX = 0.3, curRotY = 0.4;
  let dragging = false, lastX=0, lastY=0;
  let autoRotate = true;

  renderer.domElement.addEventListener('pointerdown', (e)=>{
    dragging = true; autoRotate = false; lastX = e.clientX; lastY = e.clientY;
  });
  window.addEventListener('pointerup', ()=> dragging = false);
  window.addEventListener('pointermove', (e)=>{
    if(!dragging) return;
    const dx = e.clientX - lastX, dy = e.clientY - lastY;
    targetRotY += dx * 0.005;
    targetRotX += dy * 0.005;
    lastX = e.clientX; lastY = e.clientY;
  });

  // color shift on scroll: blue -> pivot orange as user reaches #pivot section
  const pivotSection = document.getElementById('pivot');
  const colorA = new THREE.Color(0x4FA3FF);
  const colorB = new THREE.Color(0xFF6B4A);

  function updateColorByScroll(){
    const rect = pivotSection.getBoundingClientRect();
    const vh = window.innerHeight;
    let t = 1 - Math.min(Math.max((rect.top) / vh, 0), 1);
    t = Math.min(Math.max(t, 0), 1);
    const mixed = colorA.clone().lerp(colorB, t);
    matBlue.color = mixed;
  }
  window.addEventListener('scroll', updateColorByScroll);

  function animate(){
    requestAnimationFrame(animate);
    if(autoRotate && !prefersReduced){ targetRotY += 0.0022; }
    curRotX += (targetRotX - curRotX) * 0.08;
    curRotY += (targetRotY - curRotY) * 0.08;
    mesh.rotation.x = curRotX; mesh.rotation.y = curRotY;
    solid.rotation.x = curRotX; solid.rotation.y = curRotY;
    renderer.render(scene, camera);
  }
  updateColorByScroll();
  animate();
</script>

</body>
</html>
