import os
import math
import numpy as np
from PIL import Image, ImageDraw

def create_hero_gif(source_path, output_path, target_width=1086, num_frames=48, duration_ms=80):
    """
    Generates a high-quality seamless animated GIF from the wide cinematic hero banner.
    - Preserves aspect ratio 3:1 (1086x362).
    - Protects face and title typography from distortion.
    - Adds subtle neural brain glow pulse, wireframe globe pulse, drifting stars,
      holographic scanline, and a blinking terminal cursor on the laptop.
    """
    print(f"Loading source for hero banner: {source_path}")
    orig = Image.open(source_path).convert("RGB")
    orig_w, orig_h = orig.size
    aspect = orig_w / orig_h
    target_height = int(round(target_width / aspect))
    if target_height % 2 != 0:
        target_height += 1
        
    print(f"Resizing hero to {target_width}x{target_height} (aspect {aspect:.3f})...")
    base_img = orig.resize((target_width, target_height), Image.Resampling.LANCZOS)
    W, H = target_width, target_height
    base_arr = np.array(base_img, dtype=np.float32)
    
    # Grid coordinates
    Y, X = np.ogrid[:H, :W]
    
    # 1. Protective mask for Jasir's face
    dist_face = np.sqrt(((X - 795) / 80.0) ** 2 + ((Y - 125) / 95.0) ** 2)
    face_protection = np.clip(dist_face - 0.7, 0.0, 1.0)[:, :, np.newaxis]
    
    # 2. Protective mask for main title "Jasir Abdul Hameed"
    text_mask = ((X >= 110) & (X <= 570) & (Y >= 100) & (Y <= 180)).astype(np.float32)[:, :, np.newaxis]
    
    # 3. Holographic Brain mask & intensity map
    brain_region = ((X >= 615) & (X <= 760) & (Y >= 20) & (Y <= 145)).astype(np.float32)
    brain_cyan = np.clip((base_arr[:, :, 2] * 0.7 + base_arr[:, :, 1] * 0.3) - base_arr[:, :, 0] * 0.5, 0, 255)
    brain_glow_map = ((brain_cyan / 255.0) * brain_region)[:, :, np.newaxis]
    
    # 4. Holographic Globe mask & intensity map
    globe_region = ((X >= 580) & (X <= 730) & (Y >= 145) & (Y <= 295)).astype(np.float32)
    globe_cyan = np.clip((base_arr[:, :, 2] * 0.6 + base_arr[:, :, 1] * 0.4) - base_arr[:, :, 0] * 0.4, 0, 255)
    globe_glow_map = ((globe_cyan / 255.0) * globe_region)[:, :, np.newaxis]

    # 5. Deterministic drifting star particles in the sky
    np.random.seed(42)
    particles = []
    for i in range(40):
        if i < 30:
            px = float(np.random.uniform(25, 580))
            py = float(np.random.uniform(15, 230))
        else:
            px = float(np.random.uniform(960, 1065))
            py = float(np.random.uniform(15, 160))
        speed_y = float(np.random.uniform(15.0, 35.0))
        drift_x = float(np.random.uniform(3.0, 10.0))
        radius = float(np.random.uniform(1.0, 1.8))
        color_choice = np.random.choice(["cyan", "blue", "white"], p=[0.5, 0.3, 0.2])
        if color_choice == "cyan":
            color = np.array([40, 225, 255], dtype=np.float32)
        elif color_choice == "blue":
            color = np.array([80, 170, 255], dtype=np.float32)
        else:
            color = np.array([230, 245, 255], dtype=np.float32)
        phase = float(np.random.uniform(0, 2 * math.pi))
        particles.append({
            "x0": px, "y0": py, "speed_y": speed_y, "drift_x": drift_x,
            "radius": radius, "color": color, "phase": phase
        })

    cursor_x = 59
    cursor_y = 354

    frames = []
    print(f"Generating {num_frames} frames for hero banner...")
    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames) # seamless loop parameter [0, 1)
        angle = 2.0 * math.pi * t
        
        frame_arr = base_arr.copy()
        
        # Brain Hologram Breathing Glow
        brain_factor = 0.5 + 0.5 * math.sin(angle)
        frame_arr += brain_glow_map * (brain_factor * 55.0) * np.array([0.1, 0.6, 1.0], dtype=np.float32)
        
        # Globe Wireframe Glow Pulse
        globe_factor = 0.5 + 0.5 * math.sin(angle + math.pi * 0.5)
        frame_arr += globe_glow_map * (globe_factor * 40.0) * np.array([0.15, 0.5, 0.95], dtype=np.float32)
        
        # Ambient Light Sweep across city skyline
        sweep_center = (t * (W + 300)) - 150
        sweep_dist = np.abs(X - sweep_center)
        sweep_glow = np.exp(-0.5 * (sweep_dist / 60.0) ** 2) * ((Y > 220) & (X < 720)).astype(np.float32)
        sweep_glow = sweep_glow[:, :, np.newaxis] * face_protection
        frame_arr += sweep_glow * 18.0 * np.array([0.1, 0.5, 0.9], dtype=np.float32)
        
        # Telemetry Scanline
        scan_y = int(round(t * H)) % H
        y_diff = np.abs(Y - scan_y)
        scan_line = np.exp(-0.5 * (y_diff / 1.5) ** 2)[:, :, np.newaxis] * face_protection * (1.0 - text_mask * 0.8)
        frame_arr += scan_line * 16.0 * np.array([0.2, 0.8, 1.0], dtype=np.float32)
        
        frame_arr = np.clip(frame_arr, 0, 255)
        frame_img = Image.fromarray(frame_arr.astype(np.uint8), mode="RGB")
        draw = ImageDraw.Draw(frame_img)
        
        # Drifting star particles
        for p in particles:
            curr_y = (p["y0"] - t * p["speed_y"])
            if p["x0"] < 700:
                curr_y = 15.0 + ((curr_y - 15.0) % 215.0)
            else:
                curr_y = 15.0 + ((curr_y - 15.0) % 145.0)
                
            curr_x = p["x0"] + math.sin(angle + p["phase"]) * p["drift_x"]
            twinkle = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(2.0 * angle + p["phase"]))
            r = p["radius"]
            c = tuple(np.clip(p["color"] * twinkle, 0, 255).astype(int))
            draw.ellipse([curr_x - r, curr_y - r, curr_x + r, curr_y + r], fill=c)
            
        # Laptop terminal cursor
        blink_cycle = (t * 3.0) % 1.0
        if blink_cycle < 0.55:
            draw.rectangle([cursor_x, cursor_y, cursor_x + 3, cursor_y + 6], fill=(56, 189, 248))
            
        frames.append(frame_img)

    print("Quantizing hero banner frames to shared optimal palette...")
    sample_img = Image.new("RGB", (W, H * 4))
    sample_img.paste(frames[0], (0, 0))
    sample_img.paste(frames[num_frames // 4], (0, H))
    sample_img.paste(frames[num_frames // 2], (0, H * 2))
    sample_img.paste(frames[(num_frames * 3) // 4], (0, H * 3))
    palette_img = sample_img.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    
    quantized_frames = [f.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
        
    print(f"Saving {output_path}...")
    quantized_frames[0].save(
        output_path,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True
    )
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Hero banner GIF ready: {file_size_mb:.2f} MB, {W}x{H}, {num_frames} frames")
    return file_size_mb


def create_profile_gif(source_path, output_path, target_width=320, num_frames=36, duration_ms=80):
    """
    Generates a high-quality animated portrait GIF for the SYSTEM.IDENTITY card.
    - Native 320x400 (Retina 2x for 165px display).
    - Ambient radial glow on GitHub dark theme (#0d1117).
    - Energy traveling around orbiting neon rings.
    - Brain hologram pulse and perimeter motes.
    """
    print(f"Loading source for profile card: {source_path}")
    orig = Image.open(source_path).convert("RGBA")
    orig_w, orig_h = orig.size
    aspect = orig_h / orig_w
    target_height = int(round(target_width * aspect))
    if target_height % 2 != 0:
        target_height += 1
        
    print(f"Resizing portrait to {target_width}x{target_height} (aspect {aspect:.3f})...")
    portrait_resized = orig.resize((target_width, target_height), Image.Resampling.LANCZOS)
    W, H = target_width, target_height
    
    Y, X = np.ogrid[:H, :W]
    cx, cy = W * 0.5, H * 0.52
    dist_center = np.sqrt(((X - cx) / (W * 0.55)) ** 2 + ((Y - cy) / (H * 0.55)) ** 2)
    radial_falloff = np.clip(1.0 - dist_center, 0.0, 1.0)
    
    bg_base = np.zeros((H, W, 3), dtype=np.float32)
    bg_base[:, :] = [13, 17, 23]
    bg_glow = bg_base + (radial_falloff[:, :, np.newaxis] ** 1.8) * np.array([18, 48, 85], dtype=np.float32)
    
    port_arr = np.array(portrait_resized, dtype=np.float32)
    port_rgb = port_arr[:, :, :3]
    port_alpha = (port_arr[:, :, 3] / 255.0)[:, :, np.newaxis]
    
    ring_region = ((Y >= 235) & (Y <= 385)).astype(np.float32)[:, :, np.newaxis]
    cyan_intensity = np.clip(port_rgb[:, :, 2] * 0.6 + port_rgb[:, :, 1] * 0.4 - port_rgb[:, :, 0] * 0.5, 0, 255)
    magenta_intensity = np.clip(port_rgb[:, :, 0] * 0.5 + port_rgb[:, :, 2] * 0.5 - port_rgb[:, :, 1] * 0.7, 0, 255)
    ring_glow_map = ((cyan_intensity + magenta_intensity) / 255.0)[:, :, np.newaxis] * ring_region
    
    brain_card = ((X >= 225) & (X <= 315) & (Y >= 75) & (Y <= 175)).astype(np.float32)[:, :, np.newaxis]
    brain_card_glow = (port_rgb[:, :, 2] / 255.0)[:, :, np.newaxis] * brain_card
    
    np.random.seed(99)
    particles = []
    for i in range(24):
        px = float(np.random.uniform(10, W - 10))
        py = float(np.random.uniform(20, H - 20))
        speed_y = float(np.random.uniform(15.0, 30.0))
        drift_x = float(np.random.uniform(2.0, 6.0))
        radius = float(np.random.uniform(0.8, 1.5))
        color = np.array([45, 215, 255], dtype=np.float32)
        phase = float(np.random.uniform(0, 2 * math.pi))
        particles.append({
            "x0": px, "y0": py, "speed_y": speed_y, "drift_x": drift_x,
            "radius": radius, "color": color, "phase": phase
        })

    frames = []
    print(f"Generating {num_frames} frames for profile card...")
    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames)
        angle = 2.0 * math.pi * t
        
        bg_pulse = 0.5 + 0.5 * math.sin(angle)
        curr_bg = bg_glow + (radial_falloff[:, :, np.newaxis] ** 2) * (bg_pulse * 15.0) * np.array([0.1, 0.4, 0.8], dtype=np.float32)
        
        curr_port = port_rgb.copy()
        ring_pulse = 0.5 + 0.5 * np.sin(angle + (X / float(W)) * 2.0 * np.pi)[:, :, np.newaxis]
        curr_port += ring_glow_map * (ring_pulse * 38.0) * np.array([0.3, 0.8, 1.0], dtype=np.float32)
        
        brain_pulse = 0.5 + 0.5 * math.sin(angle + math.pi * 0.4)
        curr_port += brain_card_glow * (brain_pulse * 32.0) * np.array([0.2, 0.7, 1.0], dtype=np.float32)
        
        comp = np.clip(curr_bg * (1.0 - port_alpha) + curr_port * port_alpha, 0, 255)
        frame_img = Image.fromarray(comp.astype(np.uint8), mode="RGB")
        draw = ImageDraw.Draw(frame_img)
        
        for p in particles:
            curr_y = 15.0 + (((p["y0"] - t * p["speed_y"]) - 15.0) % (H - 30.0))
            curr_x = p["x0"] + math.sin(angle + p["phase"]) * p["drift_x"]
            if math.sqrt(((curr_x - 155)/45.0)**2 + ((curr_y - 105)/55.0)**2) < 0.9:
                continue
            twinkle = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(2.0 * angle + p["phase"]))
            r = p["radius"]
            c = tuple(np.clip(p["color"] * twinkle, 0, 255).astype(int))
            draw.ellipse([curr_x - r, curr_y - r, curr_x + r, curr_y + r], fill=c)
            
        frames.append(frame_img)

    print("Quantizing profile card frames to shared palette...")
    sample_img = Image.new("RGB", (W, H * 3))
    sample_img.paste(frames[0], (0, 0))
    sample_img.paste(frames[num_frames // 3], (0, H))
    sample_img.paste(frames[(num_frames * 2) // 3], (0, H * 2))
    palette_img = sample_img.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    
    quantized_frames = [f.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
        
    print(f"Saving {output_path}...")
    quantized_frames[0].save(
        output_path,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True
    )
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Profile card GIF ready: {file_size_mb:.2f} MB, {W}x{H}, {num_frames} frames")
    return file_size_mb

if __name__ == "__main__":
    hero_mb = create_hero_gif("assets/profile-card.png", "assets/hero-banner.gif", target_width=1086, num_frames=48, duration_ms=80)
    profile_mb = create_profile_gif("assets/hero-banner.png", "assets/profile-card.gif", target_width=320, num_frames=36, duration_ms=80)
    print(f"Complete! Hero GIF = {hero_mb:.2f} MB | Profile GIF = {profile_mb:.2f} MB")
