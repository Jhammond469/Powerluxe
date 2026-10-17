#!/usr/bin/env python3
"""Build solar.html and aircon.html from landing.html (2026-10-17).

The service pages must keep exactly the format of Jakov's /landing page (the marketing
course's structure), so instead of hand-copying it, this script takes landing.html and
swaps only the service-specific blocks. Re-run it after any change to landing.html:

    python3 tools/build-service-pages.py
"""
import re
from pathlib import Path

PREVIEW = True  # noindex until launch
ROOT = Path(__file__).resolve().parent.parent
BASE = (ROOT / 'landing.html').read_text()

# ── small inline icons (60x60, line style to match the site's icon set) ──────────
def icon(body):
    return (f'<svg viewBox="0 0 60 60" width="56" height="56" fill="none" stroke="currentColor" '
            f'stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')

ICONS = {
    'sun': icon('<circle cx="30" cy="30" r="10"/><path d="M30 8v6M30 46v6M8 30h6M46 30h6M14.4 14.4l4.3 4.3M41.3 41.3l4.3 4.3M14.4 45.6l4.3-4.3M41.3 18.7l4.3-4.3"/>'),
    'panel': icon('<path d="M8 40l8-26h36l-8 26z"/><path d="M12 27h36M30 14l-4 26M22 14l-5 26M38 14l-3 26"/><path d="M28 40v10M20 50h16"/>'),
    'inverter': icon('<rect x="14" y="8" width="32" height="44" rx="4"/><path d="M32 18l-6 11h8l-6 11"/>'),
    'battery': icon('<rect x="10" y="18" width="36" height="24" rx="4"/><path d="M46 26h4v8h-4"/><path d="M28 22l-5 8h8l-5 8"/>'),
    'board': icon('<rect x="10" y="8" width="40" height="44" rx="3"/><path d="M18 18v8M26 18v8M34 18v8M42 18v8M18 36h24"/>'),
    'shield': icon('<path d="M30 6L10 15v14c0 11 8.5 20.5 20 23 11.5-2.5 20-12 20-23V15L30 6z"/><path d="M21 30l6 6 12-13"/>'),
    'snow': icon('<path d="M30 6v48M9.2 18l41.6 24M9.2 42l41.6-24"/><path d="M24 10l6 5 6-5M24 50l6-5 6 5M8 25l8-1-3-7M52 35l-8 1 3 7M8 35l8 1-3 7M52 25l-8-1 3-7"/>'),
    'split': icon('<rect x="6" y="12" width="48" height="18" rx="5"/><path d="M12 24h36"/><path d="M18 36c-2 4 2 6 0 10M30 36c-2 4 2 6 0 10M42 36c-2 4 2 6 0 10"/>'),
    'tools': icon('<path d="M38 8a10 10 0 0 0-9 14L10 41a4.2 4.2 0 0 0 6 6l19-19a10 10 0 0 0 14-9l-6 3-5-5 3-6z"/>'),
    'thermo': icon('<path d="M26 34V12a5 5 0 0 1 10 0v22a9 9 0 1 1-10 0z"/><path d="M31 22v18"/>'),
    'home': icon('<path d="M8 28L30 10l22 18"/><path d="M14 24v26h32V24"/><path d="M25 50V36h10v14"/>'),
    'map': icon('<path d="M30 52s16-14.5 16-27a16 16 0 0 0-32 0c0 12.5 16 27 16 27z"/><circle cx="30" cy="25" r="6"/>'),
}

CHECK = ('<span class="check-icon"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="white" '
         'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>')

# ── the logo lockup, shared by both scenes (sits top-left of the 800x450 slot) ──
LETTERS = [(241, 298), (320, 401), (422, 530), (555, 605), (634, 698), (725, 774), (802, 864), (891, 967), (996, 1046)]

def lockup(label):
    clips = ''.join(f'<clipPath id="mhL{i}"><rect x="{a-6}" y="0" width="{b-a+12}" height="216"/></clipPath>'
                    for i, (a, b) in enumerate(LETTERS))
    letters = ''.join(f'<g class="mh-ltr" style="--i:{i}"><image href="images/logo-nav.png" width="1056" height="216" clip-path="url(#mhL{i})"/></g>'
                      for i in range(len(LETTERS)))
    return f'''
        <svg x="32" y="34" width="280" height="57" viewBox="0 0 1056 216" overflow="visible" aria-hidden="true">
          <defs>
            <clipPath id="mhShieldClip"><rect x="0" y="0" width="222" height="216"/></clipPath>
            {clips}
            <mask id="mhLogoMask" style="mask-type:alpha"><image href="images/logo-nav.png" width="1056" height="216"/></mask>
            <linearGradient id="mhSweepGrad" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
          </defs>
          <g class="mh-shield" style="filter:drop-shadow(0 0 18px rgba(0,162,226,.55))"><image href="images/logo-nav.png" width="1056" height="216" clip-path="url(#mhShieldClip)"/></g>
          {letters}
          <g mask="url(#mhLogoMask)"><rect class="mh-sweep" x="0" y="0" width="260" height="216" fill="url(#mhSweepGrad)"/></g>
        </svg>
        <text class="mh-label" x="34" y="128" font-size="21">{label}</text>
        <line class="mh-rule" pathLength="1" x1="35" y1="146" x2="135" y2="146"/>'''

def slot(page, scene_svg, caption_main, caption_alt):
    # Starts paused (.offscreen); js/motion-hero.js plays it once it scrolls into view.
    return f'''<div class="motion-slot review-scene {page["slug"]}-slot offscreen fade-in" data-intro="7200" data-period="7000">
                <svg viewBox="0 0 800 450" role="img" aria-label="{page["aria"]}">{lockup(page["label"])}
                    {scene_svg}
                </svg>
                <div class="motion-caption"><span class="main">{caption_main}</span><span class="alt">{caption_alt}</span></div>
            </div>'''


def video_box(page):
    """The hero video slot: Jakov's video, or a placeholder until it's filmed."""
    if page['VIDEO_SRC']:
        poster = f' poster="{page["VIDEO_POSTER"]}"' if page.get('VIDEO_POSTER') else ''
        return f'''<div class="hero-video-wrapper">
                    <video controls playsinline preload="metadata"{poster}>
                        <source src="{page["VIDEO_SRC"]}" type="video/mp4">
                    </video>
                </div>'''
    return f'''<!-- Jakov's {page["slug"]} video goes here. When it arrives: compress to 720p (see CLAUDE.md),
                     save as {page["video"]}, set VIDEO_SRC (+ VIDEO_POSTER) in tools/build-service-pages.py, re-run. -->
                <div class="hero-video-wrapper video-pending">
                    <img src="images/logo-nav.png" alt="" width="1056" height="216">
                    <span>Video coming soon</span>
                </div>'''


# ── SOLAR scene (from motion-hero-sample/solar-v2.html, which Josh signed off) ──
SOLAR_SCENE = '''<defs>
                          <radialGradient id="sPoolGlow"><stop offset="0" stop-color="#00A2E2" stop-opacity=".55"/><stop offset="1" stop-color="#00A2E2" stop-opacity="0"/></radialGradient>
                          <linearGradient id="sCone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe0a0" stop-opacity=".75"/><stop offset="1" stop-color="#ffe0a0" stop-opacity="0"/></linearGradient>
                          <radialGradient id="sHalo"><stop offset="0" stop-color="#ffd27a" stop-opacity=".35"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>
                        </defs>
                        <g transform="translate(272 44) scale(.82)">
                          <g class="s-stars"><circle cx="250" cy="40" r="1.6"/><circle cx="330" cy="88" r="1.2"/><circle cx="410" cy="30" r="1.8"/><circle cx="470" cy="110" r="1.2"/><circle cx="540" cy="60" r="1.6"/><circle cx="600" cy="130" r="1.2"/><circle cx="170" cy="130" r="1.3"/><circle cx="60" cy="40" r="1.5"/><circle cx="380" cy="140" r="1.1"/></g>
                          <path class="s-moon" d="M556 52 a28 28 0 1 0 22 46 a22 22 0 1 1 -22 -46z" fill="#e9ecf5"/>
                          <g class="mh-sun">
                            <circle cx="95" cy="85" r="70" fill="url(#sHalo)"/>
                            <g class="mh-rays"><line x1="95" y1="35" x2="95" y2="22"/><line x1="95" y1="135" x2="95" y2="148"/><line x1="45" y1="85" x2="32" y2="85"/><line x1="145" y1="85" x2="158" y2="85"/><line x1="60" y1="50" x2="51" y2="41"/><line x1="130" y1="120" x2="139" y2="129"/><line x1="60" y1="120" x2="51" y2="129"/><line x1="130" y1="50" x2="139" y2="41"/></g>
                            <circle class="core" cx="95" cy="85" r="30"/>
                          </g>
                          <g class="s-beams">
                            <line class="s-beam" pathLength="1" x1="118" y1="104" x2="300" y2="196"/>
                            <line class="s-beam" pathLength="1" x1="112" y1="112" x2="246" y2="232"/>
                            <line class="s-beam" pathLength="1" x1="104" y1="118" x2="200" y2="262"/>
                          </g>
                          <line class="mh-line mh-faint mh-draw d1" pathLength="1" x1="90" y1="440" x2="620" y2="440"/>
                          <polyline class="mh-line mh-house mh-draw d1" pathLength="1" points="200,440 200,280 530,280 530,440"/>
                          <polyline class="mh-line mh-house mh-draw d2" pathLength="1" points="176,288 365,170 554,288"/>
                          <rect class="mh-line mh-house mh-draw d3" pathLength="1" x="240" y="320" width="66" height="54" rx="3"/>
                          <rect class="mh-line mh-house mh-draw d3" pathLength="1" x="424" y="320" width="66" height="54" rx="3"/>
                          <rect class="mh-line mh-house mh-draw d3" pathLength="1" x="340" y="364" width="50" height="76" rx="3"/>
                          <rect class="s-win w1" x="242" y="322" width="62" height="50" rx="2"/>
                          <rect class="s-win w2" x="426" y="322" width="62" height="50" rx="2"/>
                          <rect class="s-win w3" x="342" y="366" width="46" height="72" rx="2"/>
                          <g class="s-uplight"><path d="M318 296 L300 352 L336 352 Z" fill="url(#sCone)"/><circle cx="318" cy="294" r="3.2" fill="#ffe0a0"/></g>
                          <g class="s-uplight u2"><path d="M412 296 L394 352 L430 352 Z" fill="url(#sCone)"/><circle cx="412" cy="294" r="3.2" fill="#ffe0a0"/></g>
                          <ellipse class="s-pool-glow" cx="584" cy="460" rx="70" ry="30" fill="url(#sPoolGlow)"/>
                          <rect class="s-pool-water" x="540" y="447" width="88" height="26" rx="13"/>
                          <rect class="mh-line mh-cyan mh-draw d4" pathLength="1" x="540" y="447" width="88" height="26" rx="13"/>
                          <path class="s-ripple" d="M554 457 q6 -3 12 0 t12 0"/>
                          <path class="s-ripple r2" d="M588 464 q6 -3 12 0 t12 0"/>
                          <g class="s-panels"><g transform="translate(212 262) rotate(-31.9)">
                            <rect class="s-cell" style="animation-delay:3.3s" x="0" y="4" width="37" height="18" rx="2"/>
                            <rect class="s-cell shine" style="animation-delay:3.4s,3.7s" x="40" y="4" width="37" height="18" rx="2"/>
                            <rect class="s-cell" style="animation-delay:3.5s" x="80" y="4" width="37" height="18" rx="2"/>
                            <rect class="s-cell shine" style="animation-delay:3.6s,4.1s" x="120" y="4" width="37" height="18" rx="2"/>
                            <rect class="s-cell shine" style="animation-delay:3.4s,3.9s" x="0" y="25" width="37" height="18" rx="2"/>
                            <rect class="s-cell" style="animation-delay:3.5s" x="40" y="25" width="37" height="18" rx="2"/>
                            <rect class="s-cell shine" style="animation-delay:3.6s,4.3s" x="80" y="25" width="37" height="18" rx="2"/>
                            <rect class="s-cell" style="animation-delay:3.7s" x="120" y="25" width="37" height="18" rx="2"/>
                          </g></g>
                          <rect class="mh-line mh-cyan mh-draw d4" pathLength="1" x="128" y="318" width="50" height="58" rx="5"/>
                          <circle class="s-led" cx="166" cy="331" r="4"/>
                          <svg x="134" y="323" width="20" height="20" viewBox="0 0 216 216"><image href="images/logo-nav.png" width="1056" height="216"/></svg>
                          <line class="mh-line mh-cyan mh-draw d4" pathLength="1" x1="138" y1="352" x2="168" y2="352"/>
                          <line class="mh-line mh-cyan mh-draw d4" pathLength="1" x1="138" y1="362" x2="160" y2="362"/>
                          <rect class="mh-line mh-cyan mh-draw d4" pathLength="1" x="128" y="388" width="50" height="52" rx="5"/>
                          <rect class="s-bar b4" x="136" y="396" width="34" height="7" rx="2"/>
                          <rect class="s-bar b3" x="136" y="406" width="34" height="7" rx="2"/>
                          <rect class="s-bar b2" x="136" y="416" width="34" height="7" rx="2"/>
                          <rect class="s-bar b1" x="136" y="426" width="34" height="7" rx="2"/>
                          <path class="mh-wire" d="M234 298 L153 298 L153 318"/>
                          <path class="mh-wire" d="M153 376 L153 388"/>
                          <path class="mh-wire" d="M178 347 L200 347"/>
                          <g class="s-pv-flow"><path class="mh-current" pathLength="1" d="M234 298 L153 298 L153 318"/></g>
                          <g class="s-day-flow"><path class="mh-current" pathLength="1" d="M153 376 L153 388"/></g>
                          <path class="mh-current" pathLength="1" d="M178 347 L200 347"/>
                          <g class="s-night-flow"><path class="mh-current" pathLength="1" d="M153 388 L153 376"/></g>
                        </g>'''

SOLAR_CSS = '''
        /* Solar scene — state A = day, state B (.state-b) = night */
        .solar-slot::before { content: ''; position: absolute; left: 43.5%; top: 24.7%; width: 62%; aspect-ratio: 1; transform: translate(-50%, -50%); pointer-events: none; background: radial-gradient(circle, rgba(255,210,122,.17) 0, rgba(255,210,122,0) 62%); opacity: 0; animation: mhFade 2s 2s forwards; transition: opacity 2s; }
        .solar-slot.cycling::before { animation: none; opacity: 1; }
        .solar-slot.state-b::before { opacity: 0; }
        .solar-slot.cycling .mh-sun { animation: none; opacity: 1; transform: none; transition: transform 2.2s cubic-bezier(.5,0,.3,1), opacity 1.6s; }
        .solar-slot.state-b .mh-sun { transform: translateY(330px); opacity: 0; }
        .s-beam { stroke: #ffd27a; stroke-width: 1.6; stroke-dasharray: .03 .05; opacity: 0; animation: mhFade .6s 3.1s forwards, mhFlow 1.6s 3.1s linear infinite; }
        .s-cell { fill: rgba(0,162,226,0); stroke: var(--blue); stroke-width: 1.4; animation: sCharge .5s forwards; }
        .s-cell.shine { animation: sCharge .5s forwards, sShine 4s linear infinite; }
        .s-led { fill: #1c2440; animation: sLed .3s 4.3s forwards, sBlink 2s 4.6s infinite; }
        .s-bar { fill: rgba(0,162,226,.12); }
        .s-bar.b1 { animation: sBatt1 6s 4.5s infinite; } .s-bar.b2 { animation: sBatt2 6s 4.5s infinite; }
        .s-bar.b3 { animation: sBatt3 6s 4.5s infinite; } .s-bar.b4 { animation: sBatt4 6s 4.5s infinite; }
        .s-win { fill: rgba(255,214,130,0); filter: drop-shadow(0 0 10px rgba(255,200,110,.55)); animation: sLights 1s forwards; }
        .s-win.w1 { animation-delay: 4.8s; } .s-win.w2 { animation-delay: 5.05s; } .s-win.w3 { animation-delay: 5.3s; }
        .s-beams, .s-pv-flow, .s-day-flow { transition: opacity 1.2s; }
        .solar-slot.state-b .s-beams, .solar-slot.state-b .s-pv-flow, .solar-slot.state-b .s-day-flow { opacity: 0; }
        .s-panels { transition: opacity 2s; } .solar-slot.state-b .s-panels { opacity: .45; }
        .s-stars circle { fill: #fff; opacity: 0; transition: opacity 2s; }
        .solar-slot.state-b .s-stars circle { opacity: .8; } .solar-slot.state-b .s-stars circle:nth-child(3n) { opacity: .45; }
        .s-moon { opacity: 0; transform: translateY(30px); transform-box: fill-box; transition: opacity 2s .6s, transform 2.4s .6s; }
        .solar-slot.state-b .s-moon { opacity: 1; transform: none; }
        .s-night-flow { opacity: 0; transition: opacity 1s .8s; } .solar-slot.state-b .s-night-flow { opacity: 1; }
        .s-pool-water { fill: rgba(0,162,226,0); transition: fill 1.6s 1s; } .solar-slot.state-b .s-pool-water { fill: rgba(0,162,226,.55); }
        .s-pool-glow { opacity: 0; transition: opacity 1.6s 1s; } .solar-slot.state-b .s-pool-glow { opacity: 1; }
        .s-ripple { stroke: rgba(210,245,255,.85); stroke-width: 1.6; fill: none; stroke-linecap: round; opacity: 0; transition: opacity 1.2s 1.4s; animation: mhWave 3.2s ease-in-out infinite; }
        .s-ripple.r2 { animation-delay: 1.6s; } .solar-slot.state-b .s-ripple { opacity: 1; }
        .s-uplight { opacity: 0; transition: opacity 1.2s; } .solar-slot.state-b .s-uplight { opacity: 1; }
        .solar-slot.state-b .s-uplight.u2 { transition-delay: .35s; }
        .solar-slot.state-b .s-bar.b4 { animation: sDrain4 7s forwards; } .solar-slot.state-b .s-bar.b3 { animation: sDrain3 7s forwards; }
        .solar-slot.state-b .s-bar.b2, .solar-slot.state-b .s-bar.b1 { animation: none; fill: var(--blue); }
        @keyframes sCharge { to { fill: rgba(0,162,226,.26); } }
        @keyframes sShine { 0%, 82%, 100% { fill: rgba(0,162,226,.26); } 88% { fill: rgba(140,220,255,.75); } }
        @keyframes sLed { to { fill: #3ce0a0; } }
        @keyframes sBlink { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
        @keyframes sLights { to { fill: rgba(255,214,130,.95); } }
        @keyframes sBatt1 { 0% { fill: rgba(0,162,226,.12); } 8%, 100% { fill: var(--blue); } }
        @keyframes sBatt2 { 0%, 20% { fill: rgba(0,162,226,.12); } 28%, 100% { fill: var(--blue); } }
        @keyframes sBatt3 { 0%, 40% { fill: rgba(0,162,226,.12); } 48%, 100% { fill: var(--blue); } }
        @keyframes sBatt4 { 0%, 60% { fill: rgba(0,162,226,.12); } 68%, 92% { fill: var(--blue); } 100% { fill: rgba(0,162,226,.12); } }
        @keyframes sDrain4 { 0%, 30% { fill: var(--blue); } 45%, 100% { fill: rgba(0,162,226,.12); } }
        @keyframes sDrain3 { 0%, 70% { fill: var(--blue); } 85%, 100% { fill: rgba(0,162,226,.12); } }
        @media (prefers-reduced-motion: reduce) {
            .solar-slot::before, .s-beam { opacity: 1; }
            .s-cell { fill: rgba(0,162,226,.26); } .s-win { fill: rgba(255,214,130,.95); } .s-bar { fill: var(--blue); } .s-led { fill: #3ce0a0; }
        }'''

# ── AIRCON scene — same house and lockup; state A = summer (cooling), B = winter (heating) ──
AIRCON_SCENE = '''<defs>
                          <radialGradient id="aHalo"><stop offset="0" stop-color="#ffd27a" stop-opacity=".35"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>
                        </defs>
                        <g transform="translate(272 44) scale(.82)">
                          <g class="mh-sun">
                            <circle cx="560" cy="80" r="70" fill="url(#aHalo)"/>
                            <g class="mh-rays"><line x1="560" y1="30" x2="560" y2="17"/><line x1="560" y1="130" x2="560" y2="143"/><line x1="510" y1="80" x2="497" y2="80"/><line x1="610" y1="80" x2="623" y2="80"/><line x1="525" y1="45" x2="516" y2="36"/><line x1="595" y1="115" x2="604" y2="124"/><line x1="525" y1="115" x2="516" y2="124"/><line x1="595" y1="45" x2="604" y2="36"/></g>
                            <circle class="core" cx="560" cy="80" r="30"/>
                          </g>
                          <path class="a-cloud" d="M470 120 h86 a20 20 0 0 0 -6 -39 a28 28 0 0 0 -52 -6 a22 22 0 0 0 -28 45z"/>
                          <g class="a-wind">
                            <path class="a-gust" pathLength="1" d="M20 150 q60 -14 120 0 t120 0"/>
                            <path class="a-gust g2" pathLength="1" d="M60 196 q50 -12 100 0 t100 0"/>
                            <path class="a-gust g3" pathLength="1" d="M10 236 q40 -10 80 0 t80 0"/>
                          </g>
                          <g class="a-heat">
                            <path d="M410 240 q-6 -10 0 -20 t0 -20"/><path d="M450 250 q-6 -10 0 -20 t0 -20"/><path d="M490 262 q-6 -10 0 -20 t0 -20"/>
                          </g>
                          <text class="a-temp-out" x="560" y="182" text-anchor="middle"><tspan class="hot">34°</tspan><tspan class="cold" x="560">9°</tspan></text>
                          <line class="mh-line mh-faint mh-draw d1" pathLength="1" x1="90" y1="440" x2="620" y2="440"/>
                          <polyline class="mh-line mh-house mh-draw d1" pathLength="1" points="200,440 200,280 530,280 530,440"/>
                          <polyline class="mh-line mh-house mh-draw d2" pathLength="1" points="176,288 365,170 554,288"/>
                          <!-- living room, seen through a big window -->
                          <rect class="a-room" x="230" y="308" width="156" height="92" rx="2"/>
                          <rect class="mh-line mh-house mh-draw d3" pathLength="1" x="228" y="306" width="160" height="96" rx="3"/>
                          <rect class="mh-line mh-house mh-draw d3" pathLength="1" x="404" y="320" width="46" height="54" rx="3"/>
                          <rect class="mh-line mh-house mh-draw d3" pathLength="1" x="466" y="364" width="46" height="76" rx="3"/>
                          <!-- indoor split unit -->
                          <rect class="a-unit" x="248" y="316" width="96" height="22" rx="6"/>
                          <line class="mh-line mh-cyan mh-draw d4" pathLength="1" x1="256" y1="331" x2="336" y2="331"/>
                          <circle class="a-led" cx="334" cy="322" r="2.6"/>
                          <g class="a-air">
                            <path pathLength="1" d="M266 340 q-8 14 0 28 t0 26"/>
                            <path pathLength="1" d="M296 340 q-8 14 0 28 t0 26" style="animation-delay:4.1s,4.1s"/>
                            <path pathLength="1" d="M326 340 q-8 14 0 28 t0 26" style="animation-delay:4.2s,4.2s"/>
                          </g>
                          <text class="a-temp-in" x="378" y="394" text-anchor="end"><tspan data-count-from="29" data-count-to="22" data-suffix="°" data-count-delay="4200">29°</tspan></text>
                          <!-- outdoor unit on the side wall, with his shield on it -->
                          <rect class="mh-line mh-cyan mh-draw d4" pathLength="1" x="104" y="368" width="78" height="64" rx="5"/>
                          <line class="mh-line mh-cyan mh-draw d4" pathLength="1" x1="114" y1="432" x2="114" y2="440"/>
                          <line class="mh-line mh-cyan mh-draw d4" pathLength="1" x1="172" y1="432" x2="172" y2="440"/>
                          <circle class="mh-line mh-cyan mh-draw d4" pathLength="1" cx="134" cy="401" r="22"/>
                          <g class="a-fan"><path d="M134 401 q-4 -12 0 -18 q8 4 0 18z M134 401 q12 -2 16 4 q-6 7 -16 -4z M134 401 q-8 10 -16 8 q-1 -9 16 -8z"/></g>
                          <path class="mh-line mh-cyan mh-draw d4" pathLength="1" d="M162 398h12M162 406h12M162 414h12M162 422h12"/>
                          <svg x="160" y="374" width="16" height="16" viewBox="0 0 216 216"><image href="images/logo-nav.png" width="1056" height="216"/></svg>
                          <!-- refrigerant line: outdoor unit → indoor unit -->
                          <path class="mh-wire" d="M166 368 L166 326 L248 326"/>
                          <path class="mh-current a-pipe" pathLength="1" d="M166 368 L166 326 L248 326"/>
                          <rect class="mh-line mh-cyan mh-draw d4" pathLength="1" x="540" y="447" width="88" height="26" rx="13"/>
                          <rect class="mh-pool-water" x="540" y="447" width="88" height="26" rx="13"/>
                          <path class="mh-ripple" d="M554 457 q6 -3 12 0 t12 0"/>
                          <path class="mh-ripple r2" d="M588 464 q6 -3 12 0 t12 0"/>
                        </g>'''

AIRCON_CSS = '''
        /* Aircon scene — state A = summer (cooling), state B (.state-b) = winter (heating) */
        .aircon-slot { --air: #7fd6ff; }
        .aircon-slot.state-b { --air: #ffb46a; }
        .aircon-slot::before { content: ''; position: absolute; left: 89.6%; top: 24.7%; width: 62%; aspect-ratio: 1; transform: translate(-50%, -50%); pointer-events: none; background: radial-gradient(circle, rgba(255,210,122,.16) 0, rgba(255,210,122,0) 62%); opacity: 0; animation: mhFade 2s 2s forwards; transition: opacity 2s; }
        .aircon-slot.cycling::before { animation: none; opacity: 1; }
        .aircon-slot.state-b::before { opacity: 0; }
        .aircon-slot.cycling .mh-sun { animation: none; opacity: 1; transform: none; transition: transform 2.2s cubic-bezier(.5,0,.3,1), opacity 1.6s; }
        .aircon-slot.state-b .mh-sun { transform: translateY(60px) scale(.8); opacity: .25; }
        .a-cloud { fill: rgba(220,228,245,.14); stroke: rgba(255,255,255,.55); stroke-width: 2; opacity: 0; transform: translateX(-30px); transition: opacity 1.6s .4s, transform 2.4s .4s; }
        .aircon-slot.state-b .a-cloud { opacity: 1; transform: none; }
        .a-gust { fill: none; stroke: rgba(225,235,255,.55); stroke-width: 1.8; stroke-linecap: round; stroke-dasharray: .25 .75; opacity: 0; transition: opacity 1s; animation: aGust 2.6s linear infinite; }
        .a-gust.g2 { animation-delay: .9s; } .a-gust.g3 { animation-delay: 1.7s; }
        .aircon-slot.state-b .a-gust { opacity: 1; }
        .a-heat path { fill: none; stroke: rgba(255,190,110,.55); stroke-width: 2; stroke-linecap: round; animation: aHeat 2.4s ease-in-out infinite; }
        .a-heat path:nth-child(2) { animation-delay: .8s; } .a-heat path:nth-child(3) { animation-delay: 1.6s; }
        .a-heat { opacity: 0; animation: mhFade 1s 3.2s forwards; transition: opacity 1s; }
        .aircon-slot.cycling .a-heat { animation: none; opacity: 1; }
        .aircon-slot.state-b .a-heat { opacity: 0; }
        .a-temp-out { font-family: var(--font-head); font-weight: 800; font-size: 26px; fill: #ffd27a; opacity: 0; animation: mhFade .8s 3.4s forwards; }
        .a-temp-out tspan { transition: opacity .8s; } .a-temp-out .cold { opacity: 0; fill: #dfe7ff; }
        .aircon-slot.state-b .a-temp-out .hot { opacity: 0; } .aircon-slot.state-b .a-temp-out .cold { opacity: 1; }
        .a-room { fill: rgba(127,214,255,0); animation: aRoom 1.6s 4.4s forwards; transition: fill 1.6s; }
        .aircon-slot.cycling .a-room { animation: none; fill: rgba(127,214,255,.2); }
        .aircon-slot.state-b .a-room { fill: rgba(255,170,90,.22); }
        .a-unit { fill: #1e2747; stroke: rgba(255,255,255,.8); stroke-width: 2; opacity: 0; animation: mhFade .6s 2.4s forwards; }
        .a-led { fill: #1c2440; animation: aLed .3s 3.8s forwards; transition: fill .8s; }
        .aircon-slot.cycling .a-led { animation: none; fill: var(--air); }
        .a-air path { fill: none; stroke: var(--air); stroke-width: 2.4; stroke-linecap: round; stroke-dasharray: .12 .1; opacity: 0; animation: mhFade .6s 4s forwards, aAir 1.4s 4s linear infinite; transition: stroke 1.2s; }
        .a-temp-in { font-family: var(--font-head); font-weight: 800; font-size: 22px; fill: #fff; opacity: 0; animation: mhFade .6s 4.2s forwards; }
        .a-fan { fill: rgba(0,162,226,.75); transform-box: fill-box; transform-origin: center; opacity: 0; animation: mhFade .5s 2.6s forwards, mhSpin 1.1s 2.6s linear infinite; }
        .a-pipe { transition: stroke 1.2s; }
        .aircon-slot.state-b .a-pipe { stroke: #ffb46a; filter: drop-shadow(0 0 4px rgba(255,170,90,.9)); }
        @keyframes aGust { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
        @keyframes aHeat { 0% { transform: translateY(8px); opacity: 0; } 40% { opacity: 1; } 100% { transform: translateY(-14px); opacity: 0; } }
        @keyframes aRoom { to { fill: rgba(127,214,255,.2); } }
        @keyframes aLed { to { fill: #7fd6ff; } }
        @keyframes aAir { to { stroke-dashoffset: -.44; } }
        @media (prefers-reduced-motion: reduce) {
            .aircon-slot::before, .a-heat, .a-temp-out, .a-unit, .a-air path, .a-temp-in, .a-fan { opacity: 1; }
            .a-room { fill: rgba(127,214,255,.2); } .a-led { fill: #7fd6ff; }
        }'''

# Shared page-level CSS (inline icons in the existing icon slots)
EXTRA_CSS = '''
        /* Reviews: motion scene beside a one-at-a-time review slider */
        .testimonials .reviews-grid { display: grid; grid-template-columns: 1.15fr 1fr; gap: 56px; align-items: center; }
        .reviews-col { min-width: 0; }
        .reviews-col .testimonials-swiper { margin-top: 28px; }
        .reviews-col .swiper-slide { height: auto; }
        .reviews-col .testimonial-card { height: 100%; }
        /* One long Google review would otherwise make every card huge */
        .reviews-col .testimonial-card p { display: -webkit-box; -webkit-line-clamp: 6; -webkit-box-orient: vertical; overflow: hidden; }
        .review-scene { aspect-ratio: 16 / 9; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,.08); box-shadow: 0 20px 60px rgba(0,0,0,.35); min-width: 0; }
        @media (max-width: 1024px) { .testimonials .reviews-grid { grid-template-columns: 1fr; gap: 40px; } }

        /* Hero video placeholder until Jakov films it */
        .video-pending { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; border: 1px dashed rgba(255,255,255,.25); background: rgba(20,20,34,.7); }
        .video-pending img { width: 44%; height: auto; opacity: .9; }
        .video-pending span { color: rgba(255,255,255,.6); font-size: .9rem; letter-spacing: .08em; text-transform: uppercase; }
        /* Inline service icons (the base set has no solar/aircon icons) */
        .service-icon svg { width: 56px; height: 56px; color: var(--blue); }
        .feature-icon svg { color: #fff; }'''

# ── per-page content ─────────────────────────────────────────────────────────────
PAGES = [
    dict(
        slug='solar', file='solar.html', video='images/solar-video.mp4', VIDEO_SRC='', VIDEO_POSTER='',
        title='Powerluxe Electrical | Solar Installation — Get Your Free Quote',
        desc='Solar panels, inverters and batteries installed by licensed electricians (Solar Licence S2194786) across South East Queensland. Get a fast, free solar quote from Powerluxe Electrical.',
        h1='Solar Power, Installed by Licensed Electricians',
        label='SOLAR POWER',
        aria='Animated Powerluxe logo, then the sun powering a house through rooftop solar panels and charging a battery that keeps the lights on at night',
        scene=SOLAR_SCENE, css=SOLAR_CSS,
        cap_main='<b>By day</b>The sun runs your home and charges the battery.',
        cap_alt='<b>After dark</b>The battery keeps the lights on.',
        form_h3='Get Your Free Solar Quote',
        features=[
            ('sun', 'Licensed Solar Installer', 'Solar Licence S2194786 — your system is designed and installed by licensed electricians.'),
            ('panel', 'Quality Panels &amp; Inverters', 'Industry-certified components chosen for long-term performance, not the cheapest price.'),
            ('shield', 'Safe, Compliant Installs', 'Every system installed, tested and signed off to Australian standards.'),
            ('map', 'Local SEQ Team', 'A local business servicing 100kms+ across South East Queensland.'),
        ],
        checklist=['Solar Licence S2194786', 'Licensed Electrical Contractor — Licence 92262', 'Arctic Licence L168505',
                   'ABN 43 676 192 484 Registered', 'Certified &amp; Insured Electricians', 'Clean, Tidy &amp; On-Time Installs'],
        services_label='Solar Services', services_h2='Complete Solar Solutions',
        services=[
            ('panel', 'Solar Panel Installation', 'Rooftop solar systems designed around your roof, your usage and your budget, installed by licensed electricians.'),
            ('inverter', 'Inverter Installation &amp; Upgrades', 'New and replacement inverters to get your system performing at its best again.'),
            ('battery', 'Battery Storage', 'Store the power you make during the day and use it at night, so less goes back to the grid for next to nothing.'),
            ('board', 'Switchboard Upgrades', 'Safe, compliant switchboard upgrades so your home is ready for solar and a battery.'),
        ],
        about_h2='Locally Trusted Solar &amp; Electrical Experts',
        about_p=['Powerluxe is a locally trusted electrical company, and our solar systems are designed and installed by licensed electricians who take care of every detail, from the panels on the roof to the switchboard.',
                 "At Powerluxe, we're committed to bringing the luxury of power to you — through premium service, attention to detail, and solar you can rely on."],
        bottom_label='Complete Solar Support',
        bottom_h2='Lower Power<br>Bills with<br>Solar Built for Your<br>Home',
        bottom_p='Our licensed electricians design and install solar systems that suit the way your household actually uses power — then make sure every part is safe and compliant.',
        bottom_list=['Solar Panel Installation', 'Inverter Installation', 'Battery Storage', 'Switchboard Upgrades', 'System Health Checks'],
        banner='Ready to Switch to Solar?',
    ),
    dict(
        slug='aircon', file='aircon.html', video='images/aircon-video.mp4', VIDEO_SRC='', VIDEO_POSTER='',
        title='Powerluxe Electrical | Air Conditioning Installation — Get Your Free Quote',
        desc='Split system air conditioning installed by licensed electricians with an ARCtick refrigerant licence (L168505) across South East Queensland. Get a fast, free aircon quote from Powerluxe Electrical.',
        h1='Air Conditioning, Installed by Licensed Electricians',
        label='AIR CONDITIONING',
        aria='Animated Powerluxe logo, then a split system air conditioner cooling a house in summer and heating it in winter',
        scene=AIRCON_SCENE, css=AIRCON_CSS,
        cap_main='<b>Summer</b>34° outside. A cool 22° inside.',
        cap_alt='<b>Winter</b>9° outside. A cosy 22° inside.',
        form_h3='Get Your Free Aircon Quote',
        features=[
            ('snow', 'ARCtick Licensed', 'Refrigerant handling licence L168505 — the licence every aircon installer must legally hold.'),
            ('board', 'Electrician &amp; Aircon in One', 'We do the electrical and the aircon install ourselves, so there is no second trade to book.'),
            ('shield', 'Safe, Compliant Installs', 'Every system installed, tested and signed off to Australian standards.'),
            ('map', 'Local SEQ Team', 'A local business servicing 100kms+ across South East Queensland.'),
        ],
        checklist=['Arctic (ARCtick) Licence L168505', 'Licensed Electrical Contractor — Licence 92262', 'Solar Licence S2194786',
                   'ABN 43 676 192 484 Registered', 'Certified &amp; Insured Electricians', 'Clean, Tidy &amp; On-Time Installs'],
        services_label='Air Conditioning Services', services_h2='Complete Air Conditioning Solutions',
        services=[
            ('split', 'Split System Installation', 'Reverse-cycle split systems sized to the room, for cool summers and warm winters.'),
            ('board', 'Dedicated Circuits &amp; Power', 'New circuits and switchboard upgrades so your aircon runs safely without tripping.'),
            ('thermo', 'Replacements &amp; Upgrades', 'Swap an old, noisy or inefficient unit for a modern system that costs less to run.'),
            ('tools', 'Servicing &amp; Repairs', 'Keep your system clean, efficient and running when you need it most.'),
        ],
        about_h2='Locally Trusted Air Conditioning &amp; Electrical Experts',
        about_p=['Powerluxe is a locally trusted electrical company holding both an electrical contractor licence and an ARCtick refrigerant licence — so your aircon is installed and wired by one licensed team.',
                 "At Powerluxe, we're committed to bringing the luxury of power to you — through premium service, attention to detail, and comfort you can rely on."],
        bottom_label='Complete Air Conditioning Support',
        bottom_h2='Year-Round<br>Comfort<br>Installed Right for Your<br>Home',
        bottom_p='Our licensed electricians install air conditioning that suits your home and your budget, with the electrical work done properly by the same team.',
        bottom_list=['Split System Installation', 'Dedicated Aircon Circuits', 'Switchboard Upgrades', 'Replacements &amp; Upgrades', 'Servicing &amp; Repairs'],
        banner='Ready for Year-Round Comfort?',
    ),
]


def sub_once(pattern, repl, text):
    new, n = re.subn(pattern, lambda m: repl, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'pattern not found in landing.html: {pattern[:70]}')
    return new


def build(p):
    h = BASE
    h = sub_once(r'<title>.*?</title>', f'<title>{p["title"]}</title>', h)
    # PREVIEW: keep Google out while Jakov reviews and the videos are pending. Set False at launch.
    if PREVIEW:
        h = sub_once(r'(<meta name="viewport"[^>]*>)', '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <meta name="robots" content="noindex, nofollow">', h)
    h = sub_once(r'<meta name="description" content=".*?">', f'<meta name="description" content="{p["desc"]}">', h)
    h = sub_once(r'(<link rel="stylesheet" href="css/styles.css">)', '<link rel="stylesheet" href="css/styles.css">\n    <link rel="stylesheet" href="css/motion-hero.css">', h)
    h = sub_once(r'\n    </style>\n</head>', EXTRA_CSS + p['css'] + '\n    </style>\n</head>', h)

    h = sub_once(r'<h1>Expert Electrical Repairs For Every Home &amp; Business</h1>', f'<h1>{p["h1"]}</h1>', h)
    h = sub_once(r'<div class="hero-video-wrapper">.*?</video>\s*</div>', video_box(p), h)

    # Reviews: animation on the left, review slider (one at a time) on the right
    h = sub_once(r'<section class="testimonials">\s*<div class="container">',
                 '<section class="testimonials">\n        <div class="container reviews-grid">\n            '
                 + slot(p, p['scene'], p['cap_main'], p['cap_alt']) + '\n            <div class="reviews-col">', h)
    h = re.sub(r'(<div class="swiper testimonials-swiper">.*?<div class="swiper-pagination"></div>\s*</div>)',
               lambda m: m.group(1) + '\n            </div>', h, count=1, flags=re.S)
    h = sub_once(r"\n                breakpoints: \{\n                    768: \{ slidesPerView: 2 \},\n                    1024: \{ slidesPerView: 3 \},\n                \},", '', h)
    h = sub_once(r'<h3>Get Your Free Quote Today</h3>', f'<h3>{p["form_h3"]}</h3>', h)

    feats = ''.join(f'''
            <div class="feature-card fade-in">
                <div class="feature-icon">{ICONS[i]}</div>
                <h3>{t}</h3>
                <p>{d}</p>
            </div>''' for i, t, d in p['features'])
    h = sub_once(r'(<section class="features">\s*<div class="container features-grid">).*?(\n        </div>\n    </section>)',
                 '<section class="features">\n        <div class="container features-grid">' + feats + '\n        </div>\n    </section>', h)

    checks = ''.join(f'\n                <li class="fade-in">{CHECK}{c}</li>' for c in p['checklist'])
    h = sub_once(r'<ul class="checklist">.*?\n            </ul>', '<ul class="checklist">' + checks + '\n            </ul>', h)

    svcs = ''.join(f'''
                <div class="service-card fade-in">
                    <div class="service-icon">{ICONS[i]}</div>
                    <h3>{t}</h3>
                    <p>{d}</p>
                </div>''' for i, t, d in p['services'])
    h = sub_once(r'<span class="label">Our Services</span>\s*<h2>High-Quality Electrical Services</h2>',
                 f'<span class="label">{p["services_label"]}</span>\n                <h2>{p["services_h2"]}</h2>', h)
    h = sub_once(r'<div class="services-grid">.*?\n            </div>\n        </div>\n    </section>',
                 '<div class="services-grid">' + svcs + '\n            </div>\n        </div>\n    </section>', h)

    h = sub_once(r'<h2>Locally Trusted Electrical Experts</h2>\s*<p>.*?</p>\s*<p>.*?</p>',
                 f'<h2>{p["about_h2"]}</h2>\n                <p>{p["about_p"][0]}</p>\n                <p>{p["about_p"][1]}</p>', h)

    h = sub_once(r'<span class="label">Complete Electrical Support</span>\s*<h2>.*?</h2>',
                 f'<span class="label">{p["bottom_label"]}</span>\n                <h2>{p["bottom_h2"]}</h2>', h)
    h = sub_once(r'(<div class="bottom-cta-right fade-in">\s*)<p>.*?</p>\s*<ul class="services-list">.*?</ul>',
                 '<div class="bottom-cta-right fade-in">\n                <p>' + p['bottom_p'] + '</p>\n                <ul class="services-list">'
                 + ''.join(f'\n                    <li>{x}</li>' for x in p['bottom_list']) + '\n                </ul>', h)
    h = sub_once(r'<h2>Want Reliable Electrical Services\?</h2>', f'<h2>{p["banner"]}</h2>', h)

    h = sub_once(r'(<script src="https://link.msgsndr.com/js/form_embed.js"></script>)',
                 '<script src="js/motion-hero.js"></script>\n    <script src="https://link.msgsndr.com/js/form_embed.js"></script>', h)

    header = (f'<!-- GENERATED by tools/build-service-pages.py from landing.html — edit the script, not this file. -->\n')
    h = h.replace('<!DOCTYPE html>\n', '<!DOCTYPE html>\n' + header, 1)
    (ROOT / p['file']).write_text(h)
    print('wrote', p['file'])


for page in PAGES:
    build(page)
