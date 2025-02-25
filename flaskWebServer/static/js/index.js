setInterval(function() {
    fetch(window.location.href, { cache: "no-store" }) // Voorkomt caching
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const newMeetings = doc.querySelector("#meetings");
            if (newMeetings) {
                document.querySelector("#meetings").innerHTML = newMeetings.innerHTML;
            }
        })
        .catch(error => console.error("Fout bij het ophalen van meetings:", error));
}, 300000); // 5 minuten in milliseconden

setInterval(function() {
    // Krijg de huidige tijd
    const now = new Date();
    
    // Controleer of het middernacht is (00:00:00)
    if (now.getHours() === 0 && now.getMinutes() === 0 && now.getSeconds() === 0) {
        window.location.reload(); // Laadt de pagina opnieuw
    } else {
        // Voorkom caching en haal de vergaderingen op
        fetch(window.location.href, { cache: "no-store" })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");
                const newMeetings = doc.querySelector("#meetings");
                if (newMeetings) {
                    document.querySelector("#meetings").innerHTML = newMeetings.innerHTML;
                }
            })
            .catch(error => console.error("Fout bij het ophalen van meetings:", error));
    }
}, 60000); // Elke 60 seconden controleren
