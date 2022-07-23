let menu = document.getElementsByClassName('option');

for (let i = 0; i < menu.length; i++) {
    menu[i].onclick = function() {
        let url = window.location.href.replace(/[A-Za-z]/g, '');
        url = 'http' + url;
        url += menu[i].dataset.url;
        window.location.href = url; 
    }
    menu[i].onmouseover = function() {
        menu[i].style.fontSize = 25 + 'px';
        document.body.style.cursor = 'pointer';
    }
    menu[i].onmouseout = function() {
        menu[i].style.fontSize = 20 + 'px';
        document.body.style.cursor = 'auto';
    }
}