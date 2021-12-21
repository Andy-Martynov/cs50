var index=1;


function preview() {

    const sample = document.querySelector("#sample");
    const sample2 = document.querySelector("#sample2");
    console.log('preview', index);

    if (index == 1) {
        sample.style.display = "none";
        sample2.style.display = "block";
        index = 2;
    } else {
        sample.style.display = "block";
        sample2.style.display = "none";
        index = 1;
    }

    setTimeout(preview, 10000); // Change image every 10 seconds
}

document.addEventListener('DOMContentLoaded', function() {

	console.log('PREVIEW');

    preview();
});

