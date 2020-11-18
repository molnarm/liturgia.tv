function toggleThemes() {
    toggleTheme(document.getElementById('css-dark'))
    toggleTheme(document.getElementById('css-light'))
}
function toggleTheme(element) {
    if (element.rel == 'stylesheet') element.rel = 'stylesheet alternate';
    else element.rel = 'stylesheet';
}
function refreshAtStart() {
    setTimeout(function () { location.reload() }, window.zsolozsmaStartTime - Date.now());
}

var zsolozsmaNotifications;
function toggleNotifications(eventName) {
    var trigger = document.getElementById('notification-trigger');
    if (zsolozsmaNotifications) {
        for (var i = 0; i < zsolozsmaNotifications.length; i++) {
            clearTimeout(zsolozsmaNotifications[i]);
        }
        zsolozsmaNotifications = undefined;
        trigger.innerText = 'Értesítsen, ha kezdődik!';
    }
    else {
        if (!("Notification" in window)) {
            alert("A böngésző nem támogatja az értesítéseket!");
        }
        else if (Notification.permission === "granted") {
            setNotifications(eventName);
            trigger.innerText = 'Mégse értesítsen, ha kezdődik!';
        }
        else if (Notification.permission !== "denied") {
            Notification.requestPermission(function (permission) {
                if (permission === "granted") {
                    setNotifications(eventName);
                    trigger.innerText = 'Mégse értesítsen, ha kezdődik!';
                }
            });
        }

    }
}
function setNotifications(eventName) {
    zsolozsmaNotifications = [
        setTimeout(function () { createNotification(eventName, 'Hamarosan kezdődik a közvetítés!') }, window.zsolozsmaStartTime - 60000 - Date.now()),
        setTimeout(function () { createNotification(eventName, 'Kezdődik a közvetítés!') }, window.zsolozsmaStartTime - Date.now())
    ];
}
function createNotification(title, message) {
    return new Notification(title, {
        body: message,
        icon: '/static/zsolozsma/favicon.png'
    });
}