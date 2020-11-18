function toggleThemes() {
    toggleTheme(document.getElementById('css-dark'))
    toggleTheme(document.getElementById('css-light'))
}
function toggleTheme(element) {
    if (element.rel == 'stylesheet') element.rel = 'stylesheet alternate';
    else element.rel = 'stylesheet';
}
function start_at(starttime) {
    setInterval(function () { location.reload }, starttime - Date.now());
}