(function() {
    // Analytics Tracker
    const TRACKING_URL = '/api/events/track/';
    let eventsQueue = [];
    let maxScrollDepth = 0;
    
    // Calculate initial max scroll
    function updateScrollDepth() {
        const scrollPercent = Math.round(
            (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
        );
        if (scrollPercent > maxScrollDepth) {
            maxScrollDepth = scrollPercent;
        }
    }

    window.addEventListener('scroll', updateScrollDepth);
    
    // Track clicks
    document.addEventListener('click', function(e) {
        const target = e.target.closest('a, button');
        if (target) {
            let elementId = target.id || target.className || target.tagName;
            let data = {};
            if (target.tagName === 'A') {
                data.href = target.href;
                data.text = target.innerText.substring(0, 50);
            }
            eventsQueue.push({
                type: 'click',
                element_id: elementId,
                data: data
            });
        }
    });

    // Track forms
    document.addEventListener('submit', function(e) {
        const target = e.target;
        let elementId = target.id || target.className || target.action;
        eventsQueue.push({
            type: 'form',
            element_id: elementId,
            data: { action: target.action }
        });
    });

    // Send payload
    function sendPayload() {
        if (eventsQueue.length === 0 && maxScrollDepth === 0) return;
        
        const payload = {
            path: window.location.pathname,
            scroll_depth: maxScrollDepth,
            events: eventsQueue
        };

        // We use fetch with keepalive to ensure it sends even if page unloads
        fetch(TRACKING_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
            keepalive: true
        }).catch(err => console.error('Tracking error:', err));
        
        // Reset queues
        eventsQueue = [];
        // Note: we don't reset maxScrollDepth, it only goes up per page view
    }

    // Send data periodically and on page unload
    setInterval(sendPayload, 5000);
    window.addEventListener('beforeunload', sendPayload);
})();
