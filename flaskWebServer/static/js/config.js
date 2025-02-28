function addRoom() {
    const roomCalendars = document.getElementById('roomCalendars');
    const newRoom = document.createElement('div');
    newRoom.className = 'mb-3 d-flex align-items-center room-entry';
    newRoom.innerHTML = `
        <input type="text" name="room" class="form-control me-2" style="width: 20%;" value="" placeholder="Room Name">
        <input type="text" name="email" class="form-control me-2" style="width: 80%;" value="" placeholder="Room Email">
        <button type="button" class="btn btn-danger" onclick="removeRoom(this)">-</button>
    `;
    roomCalendars.insertBefore(newRoom, roomCalendars.lastElementChild);
}

function removeRoom(button) {
    button.closest('.room-entry').remove();
}

function toggleVisibility(fieldId) {
    const field = document.getElementById(fieldId);
    const currentType = field.type;
    // Toggle between password and text input
    field.type = currentType === "password" ? "text" : "password";
}

function saveConfig() {
    const formData = new FormData(document.getElementById('configForm'));
    
    // Verzamel de ROOM_CALENDARS gegevens als een array van objecten
    const roomEntries = [];
    document.querySelectorAll('#roomCalendars .room-entry').forEach(entry => {
        const room = entry.querySelector('input[name="room"]').value;
        const email = entry.querySelector('input[name="email"]').value;
        
        roomEntries.push({
            room: room,
            email: email
        });
    });

    // Stel de configuratie samen
    const configData = {
        timezone: formData.get('timezone'),
        CLIENT_ID: formData.get('CLIENT_ID'),
        CLIENT_SECRET: formData.get('CLIENT_SECRET'),
        TENANT_ID: formData.get('TENANT_ID'),
        ROOM_CALENDARS: roomEntries
    };

    //checkboxes uitlezen
    configData.show_title = document.getElementById('show_title').checked;
    configData.show_subject = document.getElementById('show_subject').checked;
    configData.skiptime = document.getElementById('skiptime').checked;

    // Verstuur de data naar de server
    fetch('/save-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(configData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // Hier kun je bijvoorbeeld een bericht tonen dat de configuratie succesvol is opgeslagen
        alert('Config saved successfully!');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving the configuration.');
    });
}



