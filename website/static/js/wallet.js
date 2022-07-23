openPage('utxo');
function openPage(link) {
    pages = document.getElementsByClassName('content');
    console.log(pages);

    for (let i = 0; i < pages.length; i++) { 
        console.log(pages[i]);
        pages[i].style.display = 'none'; 
    }
    cur_page = document.getElementById(link);    
    console.log(cur_page);
    console.log(link);
    cur_page.style.display = 'block';
}

let i = 0;

function addVin() {
    let elem = document.getElementById('vin_' + i);
    let clone = elem.cloneNode(true);
    clone.id = 'vin_' + ++i;
    elem.parentNode.appendChild(clone);
}

let j = 0;

function addVout() {
    let elem = document.getElementById('vout_' + j);
    let clone = elem.cloneNode(true);
    clone.id = 'vout_' + ++j;
    elem.parentNode.appendChild(clone);
}