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
        usingNotifications(function () {
            usingServiceWorkers(function (worker) {
                setNotifications(worker, eventName);
                trigger.innerText = 'Mégse értesítsen, ha kezdődik!';
            });
        });
    }
}
function setNotifications(worker, eventName) {
    zsolozsmaNotifications = [
        setTimeout(function () { setNotification(worker, eventName, 'Hamarosan kezdődik a közvetítés!') }, window.zsolozsmaStartTime - 60000 - Date.now()),
        setTimeout(function () { setNotification(worker, eventName, 'Kezdődik a közvetítés!') }, window.zsolozsmaStartTime - Date.now())
    ];
}
function setNotification(worker, eventName, message) {
    worker.showNotification(eventName, { body: message, icon: '/static/zsolozsma/notification.png' });
}
function usingNotifications(callback) {
    if (!("Notification" in window)) {
        alert("A böngésző nem támogatja az értesítéseket!");
    }
    else if (Notification.permission === "granted") {
        callback();
    }
    else if (Notification.permission !== "denied") {
        Notification.requestPermission(function (permission) {
            if (permission === "granted") {
                callback();
            }
        });
    }
}
var zsolozsmaWorker;
function usingServiceWorkers(callback) {
    if (zsolozsmaWorker) {
        callback(zsolozsmaWorker);
    }
    else if (!('serviceWorker' in navigator)) {
        alert("A böngésző nem támogatja az értesítéseket!");
    }
    else {
        navigator.serviceWorker.register('/service.js')
            .then(function (registration) {
                zsolozsmaWorker = registration;
                callback(zsolozsmaWorker);
            })
            .catch(function (error) { alert("Nem sikerült értesítéseket létrehozni!") });
    }
}