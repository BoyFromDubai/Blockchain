let blocks_ids = document.getElementsByClassName('block-index');

console.log(1);
console.log(blocks_ids);
console.log(blocks_ids.length);

for (let i = 0; i < blocks_ids.length; i++) {
    blocks_ids[i].onclick = function() {
        window.open(window.location.href + 'block=' + blocks_ids[i].dataset.index);
    }
    
}


