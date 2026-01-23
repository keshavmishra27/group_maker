anime({
    targets: '#ui',
    opacity: [0, 1],
    scale: [0.9, 1],
    duration: 1200,
    easing: 'easeOutExpo'
});

document.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("mouseenter", () => {
        anime({
            targets: btn,
            scale: 1.08,
            duration: 200,
            easing: 'easeOutQuad'
        });
    });

    btn.addEventListener("mouseleave", () => {
        anime({
            targets: btn,
            scale: 1.1,
            duration: 200,
            easing: 'easeOutQuad'
        });
    });
});

