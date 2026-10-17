// Motion hero — shared by solar.html and aircon.html (2026-10-17).
// The scene sits beside the reviews, below the fold, so it starts paused (.offscreen)
// and only plays its intro once scrolled into view. After the intro it alternates
// between two states (day/night, summer/winter) by toggling .state-b.
(() => {
    const slot = document.querySelector('.motion-slot');
    if (!slot) return;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    let started = false, visible = false;

    // Count-up/down numbers during the intro (e.g. the thermostat settling at 22°)
    function runCounters() {
        slot.querySelectorAll('[data-count-from]').forEach(el => {
            const from = +el.dataset.countFrom, to = +el.dataset.countTo, suffix = el.dataset.suffix || '';
            if (reduced) { el.textContent = to + suffix; return; }
            setTimeout(() => {
                const t0 = performance.now();
                const tick = now => {
                    const k = Math.min(1, (now - t0) / 1800);
                    el.textContent = Math.round(from + (to - from) * k) + suffix;
                    if (k < 1) requestAnimationFrame(tick);
                };
                requestAnimationFrame(tick);
            }, +el.dataset.countDelay || 0);
        });
    }

    function start() {
        started = true;
        runCounters();
        if (reduced) return;
        setTimeout(() => {
            slot.classList.add('cycling');
            setInterval(() => {
                if (visible && !document.hidden) slot.classList.toggle('state-b');
            }, +slot.dataset.period || 7000);
        }, +slot.dataset.intro || 6500);
    }

    // Play while at least a third of it is on screen, pause otherwise
    new IntersectionObserver(([e]) => {
        visible = e.isIntersecting;
        slot.classList.toggle('offscreen', !visible);
        if (visible && !started) start();
    }, { threshold: 0.35 }).observe(slot);
})();
