// Mobile Debug Console - Shows errors on screen
(function() {
    const debugDiv = document.createElement('div');
    debugDiv.id = 'mobile-debug';
    debugDiv.style.cssText = `
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        max-height: 200px;
        overflow-y: auto;
        background: rgba(0,0,0,0.9);
        color: #0f0;
        font-family: monospace;
        font-size: 10px;
        padding: 10px;
        z-index: 99999;
        border-top: 2px solid red;
    `;
    document.body.appendChild(debugDiv);

    function log(type, ...args) {
        const msg = args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ');
        const line = document.createElement('div');
        line.style.color = type === 'error' ? '#f00' : type === 'warn' ? '#ff0' : '#0f0';
        line.textContent = `[${type.toUpperCase()}] ${msg}`;
        debugDiv.insertBefore(line, debugDiv.firstChild);
        if (debugDiv.children.length > 50) debugDiv.lastChild.remove();
    }

    window.addEventListener('error', (e) => {
        log('error', e.message, '@', e.filename, e.lineno);
    });

    console._error = console.error;
    console.error = function(...args) {
        log('error', ...args);
        console._error.apply(console, args);
    };

    console._log = console.log;
    console.log = function(...args) {
        log('log', ...args);
        console._log.apply(console, args);
    };

    console._warn = console.warn;
    console.warn = function(...args) {
        log('warn', ...args);
        console._warn.apply(console, args);
    };

    log('log', 'Debug console loaded ✅');
})();
