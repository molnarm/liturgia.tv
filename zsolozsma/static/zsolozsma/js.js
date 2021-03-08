function toggleThemes() {
    setTheme(!isLightTheme(), true);
}

function isLightTheme() {
    return document.getElementById('css-light').rel == 'stylesheet';
}

function setTheme(light, triggerEvent) {
    document.getElementById('css-light').rel = light ? 'stylesheet' : 'stylesheet alternate';
    document.getElementById('css-dark').rel = light ? 'stylesheet alternate' : 'stylesheet';
    document.cookie = "theme=" + (light ? 'light' : 'dark') + "; max-age=" + 30 * 86400 + "; path=/; samesite=lax";

    if (triggerEvent)
        triggerThemeChange(light);
}

function triggerThemeChange(light) {
    if (localStorageAvailable())
        window.localStorage.setItem("theme", light);
}
if (localStorageAvailable()) {
    window.addEventListener('storage', function(event) {
        if (event.key == 'theme')
            setTheme(event.newValue == 'true', false);
    });
    triggerThemeChange(isLightTheme());
}
// https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API
function localStorageAvailable() {
    var storage;
    try {
        storage = window['localStorage'];
        var x = '__storage_test__';
        storage.setItem(x, x);
        storage.removeItem(x);
        return true;
    } catch (e) {
        return e instanceof DOMException && (
                // everything except Firefox
                e.code === 22 ||
                // Firefox
                e.code === 1014 ||
                // test name field too, because code might not be present
                // everything except Firefox
                e.name === 'QuotaExceededError' ||
                // Firefox
                e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
            // acknowledge QuotaExceededError only if there's something already stored
            (storage && storage.length !== 0);
    }
}

function futureBroadcast() {
    setTimeout(function() { window.location.href = window.location.origin + window.location.pathname + '?mutasd' }, window.zsolozsmaStartTime - Date.now());

    if (notificationsSupported()) {
        document.getElementById('notification-trigger').parentElement.style.display = 'block';
    }
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
    } else {
        usingNotifications(function() {
            usingServiceWorkers(function(worker) {
                setNotifications(worker, eventName);
                trigger.innerText = 'Mégse értesítsen, ha kezdődik!';
            });
        });
    }
}

function notificationsSupported() {
    if (!("Notification" in window)) {
        return false;
    }
    if (!('serviceWorker' in navigator)) {
        return false;
    }
    return true;
}

function setNotifications(worker, eventName) {
    zsolozsmaNotifications = [
        setTimeout(function() { setNotification(worker, eventName, 'Hamarosan kezdődik a közvetítés!') }, window.zsolozsmaStartTime - 60000 - Date.now()),
        setTimeout(function() { setNotification(worker, eventName, 'Kezdődik a közvetítés!') }, window.zsolozsmaStartTime - Date.now())
    ];
}

function setNotification(worker, eventName, message) {
    worker.showNotification(eventName, { body: message, icon: '/static/zsolozsma/notification.png', data: { 'url': window.location.origin + window.location.pathname } });
}

function usingNotifications(callback) {
    if (Notification.permission === "granted") {
        callback();
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission(function(permission) {
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
    } else {
        navigator.serviceWorker.register('/service.js')
            .then(function(registration) {
                zsolozsmaWorker = registration;
                callback(zsolozsmaWorker);
            })
            .catch(function(error) { alert("Nem sikerült értesítéseket létrehozni!") });
    }
}

var splitInstance;
var is_16_9;

function setupBroadcastLayout() {
    is_16_9 = document.querySelector('.video-16-9');

    if (is_16_9) {
        window.onresize = sizeChanged;
        sizeChanged();
    }

    if (!document.querySelector('.with-video.with-text'))
        return;

    const mediaQuery = window.matchMedia('(min-width: 1280px)');
    mediaQuery.addEventListener('change', layoutChanged);
    layoutChanged(mediaQuery);
}

function layoutChanged(mediaQuery) {
    if (splitInstance)
        splitInstance.destroy();

    splitInstance = Split(['.video', '.text'], {
        direction: mediaQuery.matches ? 'horizontal' : 'vertical',
        minSize: [0, 0],
        onDrag: is_16_9 ? sizeChanged : undefined
    });
}

function sizeChanged() {
    const wrapper = document.querySelector('.broadcast')
    const video = document.querySelector('.video');

    const maxW = video.offsetWidth;
    const maxH = document.querySelector('.with-video.with-text') ? video.offsetHeight : wrapper.offsetHeight;

    if (maxW > 16 / 9 * maxH) {
        setVideoSize(video, maxH, maxH * 16 / 9);
    } else {
        setVideoSize(video, maxW * 9 / 16, maxW);
    }
};

function setVideoSize(video, h, w) {
    const iframe = video.querySelector('.video-wrapper');
    iframe.style.height = h + 'px';
    iframe.style.width = w + 'px';
}