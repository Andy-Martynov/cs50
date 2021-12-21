function show_all(list) {
    // console.log('show all ', list.length);
    for(var  f=0; f<list.length; f++) {
        list[f].style.display='table-cell';
        if (list[f].getAttribute('t') == 'i') {
            list[f].style.display='inline';
        }
    }
}
function hide_all(list) {
    // console.log('hide all', list.length);
    for(var  f=0; f<list.length; f++) {
        list[f].style.display='none';
    }
}


function add() {
    uid = this.getAttribute('uid');
    name = document.querySelector(`#name_${uid}`).innerHTML;
    console.log('ADD', uid, name);
    const member = document.querySelectorAll(`[mid="${uid}"]`);
    const user = document.querySelectorAll(`[uid="${uid}"]`);
    show_all(member);
    hide_all(user);
    options = document.querySelectorAll("option");
    for (let i = 0; i < options.length; i++) {
        if (options[i].innerHTML == name) {
            options[i].selected = true;
        }
    }
}
function remove() {
    mid = this.getAttribute('mid');
    name = document.querySelector(`#name_${mid}`).innerHTML;
    console.log('REMOVE', mid, name);
    const member = document.querySelectorAll(`[mid="${mid}"]`);
    const user = document.querySelectorAll(`[uid="${mid}"]`);
    show_all(user);
    hide_all(member);
    options = document.querySelectorAll("option");
    for (let i = 0; i < options.length; i++) {
        if (options[i].innerHTML == name) {
            options[i].selected = false;
        }
    }
}
function gr_add() {
    gid = this.getAttribute('gid');
    console.log('gr_ADD', gid);

    gms = document.querySelectorAll(".gm");
    for (let i = 0; i < gms.length; i++) {
        if (gms[i].getAttribute('gid') == gid) {
            uid=gms[i].innerHTML;
            name = document.querySelector(`#name_${uid}`).innerHTML;
            const member = document.querySelectorAll(`[mid="${uid}"]`);
            const user = document.querySelectorAll(`[uid="${uid}"]`);
            show_all(member);
            hide_all(user);
            options = document.querySelectorAll("option");
            for (let i = 0; i < options.length; i++) {
                if (options[i].innerHTML == name) {
                    options[i].selected = true;
                }
            }
        }
    }
}
function gr_remove() {
    gid = this.getAttribute('gid');
    console.log('gr_REMOVE', gid);
    gms = document.querySelectorAll(".gm");
    for (let i = 0; i < gms.length; i++) {
        if (gms[i].getAttribute('gid') == gid) {
            uid=gms[i].innerHTML;
            name = document.querySelector(`#name_${uid}`).innerHTML;
            const member = document.querySelectorAll(`[mid="${uid}"]`);
            const user = document.querySelectorAll(`[uid="${uid}"]`);
            show_all(user);
            hide_all(member);
            options = document.querySelectorAll("option");
            for (let i = 0; i < options.length; i++) {
                if (options[i].innerHTML == name) {
                    options[i].selected = false;
                }
            }
        }
    }
}


document.addEventListener('DOMContentLoaded', function() {

	console.log('GROUP UPDATE');

    const btns_add = document.querySelectorAll(".add");
    for (let i = 0; i < btns_add.length; i++) {
        btns_add[i].addEventListener("click", add, false);
    }
    const btns_remove = document.querySelectorAll(".remove");
    for (let i = 0; i < btns_remove.length; i++) {
        btns_remove[i].addEventListener("click", remove, false);
    }
    const btns_gr_add = document.querySelectorAll(".gr_add");
    for (let i = 0; i < btns_gr_add.length; i++) {
        btns_gr_add[i].addEventListener("click", gr_add, false);
    }
    const btns_gr_remove = document.querySelectorAll(".gr_remove");
    for (let i = 0; i < btns_gr_remove.length; i++) {
        btns_gr_remove[i].addEventListener("click", gr_remove, false);
    }

});
