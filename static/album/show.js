var slideIndex = 0;

function showSlides() {
    var rule;
    var i;
    const slides = document.querySelectorAll(".mySlides");

    if (slideIndex == slides.length) {
        slideIndex = 0;
    }
    const amode = slides[slideIndex].getAttribute("amode");
    // let aname = amode.slice(9);
    // const acaption = document.querySelector("#acaption");
    // acaption.innerHTML = aname;

    const titles = document.querySelectorAll(".title");
    const caption = document.querySelector("#caption");
    var dots = document.getElementsByClassName("dot");

    const delay = document.querySelector("#delay").value;
    stylesheets = document.styleSheets;
    stylesheet = stylesheets[stylesheets.length-1]
    rules = stylesheet.cssRules;
    for (i = 0; i < rules.length; i++) {
        if (rules[i].selectorText == amode) {
            rule = rules[i];
            rule.style.animationDuration = `${delay}s`;
        }
    }

    pause = document.getElementById("pause");
    if (pause.className == 'fa fa-pause') {
        slideIndex++;
        rule.style.animationDuration = `${delay}s`;
    } else {
        rule.style.animationDuration = `0s`;
    }

    for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
    }

    if (slideIndex > slides.length) {slideIndex = 1}
    for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
    }

    slides[slideIndex-1].style.display = "block";
    dots[(slideIndex-1)%3].className += " active";
    caption.innerHTML = `${slideIndex}/${slides.length} ` + titles[slideIndex-1].innerHTML;

    setTimeout(showSlides, delay*1000);
}

function pause_play() {
    const slides = document.querySelectorAll(".mySlides");
    console.log('pause_play', this.className);
    if (this.className == 'fa fa-pause') {
        slides[slideIndex-1].style.webkitAnimationPlayState = 'paused';
        this.className = 'fa fa-play';
    } else {
        slides[slideIndex-1].style.webkitAnimationPlayState = 'running';
        this.className = 'fa fa-pause';
    }
}

function music_play() {
    console.log('music_play', this);
    const music = document.getElementById("music");
    if (music.paused) {
        music.play();
        this.style.color = 'red';
    } else {
        music.pause();
        this.style.color = 'white';
    }
}

function openFullscreen() {
  const elem = document.querySelector("body");
  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.webkitRequestFullscreen) { /* Safari */
    elem.webkitRequestFullscreen();
  } else if (elem.msRequestFullscreen) { /* IE11 */
    elem.msRequestFullscreen();
  }
  f11 = document.getElementById("f11")
  f11.addEventListener('click', closeFullscreen, false);
  f11.classList.remove('fa-expand');
  f11.classList.add('fa-compress');
}

function closeFullscreen() {
  const elem = document.querySelector("body");
  if (document.exitFullscreen) {
    document.exitFullscreen();
  } else if (document.webkitExitFullscreen) { /* Safari */
    document.webkitExitFullscreen();
  } else if (document.msExitFullscreen) { /* IE11 */
    document.msExitFullscreen();
  }
  f11 = document.getElementById("f11")
  f11.addEventListener('click', openFullscreen, false);
  f11.classList.remove('fa-compress');
  f11.classList.add('fa-expand');
}


document.addEventListener('DOMContentLoaded', function() {

	console.log('SHOW');

    const music = document.getElementById("music");
    document.getElementById("pause").addEventListener('click', pause_play, false);
    document.getElementById("play").addEventListener('click', music_play, false);
    document.getElementById("f11").addEventListener('click', openFullscreen, false);

    console.log(music);
    if (music != null) {
        music.loop = true;
        music.autoplay;
    }

    showSlides();
});

