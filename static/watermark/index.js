var index=0;
var opacity=0.5;
var interval=300;
let src="";

function set_index() {
    console.log('index:', this);
    index = this.getAttribute("index");
}

function set_opacity() {
    console.log('index:', this);
    opacity = this.value;
    watermark_sample = document.querySelector("#watermark_sample");
    watermark_sample.style.opacity = opacity;
}

function set_interval() {
    console.log('interval:', this.value);
    interval = parseInt(this.value);
}

function showImage() {
    // console.log('src', src);
    const images = document.querySelectorAll(".image");
    const marks = document.querySelectorAll(".mark");
    for (i = 0; i < marks.length; i++) {
        marks[i].remove()
    }

    const menu_view = document.querySelector("#view");
    menu_view.classList.remove('disabled');
    const menu_download = document.querySelector("#download");
    menu_download.classList.remove('disabled');

    const watermark_sample = document.querySelector("#watermark_sample");
    wmx = watermark_sample.width;
    wmy = watermark_sample.height;

    let place = document.querySelector("#place");

    for (i = 0; i < images.length; i++) {
        if (i == index) {
            images[i].style.display = "block";
            imx = images[i].width;
            imy = images[i].height;
            console.log('params :', interval, wmx, wmy, imx, imy);
            for (x = 10; x < imx; x=x+interval+wmx) {
                for (y = 10; y < imy; y=y+interval+wmy) {
                    var mark = document.createElement("img");
                    mark.style.position = "absolute";
                    mark.style.left = `${x}px`;
                    mark.style.top = `${y}px`;
                    mark.src = src;
                    mark.style.opacity = opacity;
                    mark.classList.add("mark");
                    place.appendChild(mark);
                    console.log('x:', x, 'y:', y);
                    path = `${images[i].src}`;
                    arr = path.split('/');
                    name = arr[arr.length-1]
                    menu_view.href = `/watermark/view/${name}/${opacity}/${interval}`;
                }
            }
        } else {
            images[i].style.display = "none";
        }
    }

    setTimeout(showImage, 1000);

}

document.addEventListener('DOMContentLoaded', function() {
	console.log('WATERMARK');

	const images = document.querySelectorAll(".image");
	images[0].style.display="block"

	const thumbs = document.querySelectorAll(".thumb");
    for (i = 0; i < thumbs.length; i++) {
        thumbs[i].setAttribute("index", i)
        thumbs[i].addEventListener('click', set_index, false);
    }

    document.getElementById("opacity").addEventListener('change', set_opacity, false);
    document.getElementById("interval").addEventListener('change', set_interval, false);

    const watermark_sample = document.querySelector("#watermark_sample");
    src = watermark_sample.src;

    showImage();
});
