var index=1;

function setParams() {
    var dir;
    var timing;
    var fill;

    const duration = document.querySelector("#duration").value;
    const iduration = document.querySelector("#iduration");

    const delay = document.querySelector("#delay").value;
    const idelay = document.querySelector("#idelay");

    const count = document.querySelector("#count").value;
    const icount = document.querySelector("#icount");

    switch (document.querySelector("#direction").value) {
        case "1" :
            direction = "normal";
            break;
        case "2" :
            direction = "reverse";
            break;
        case "3" :
            direction = "alternate";
            break;
        case "4" :
            direction = "alternate-reverse";
    }
    const idirection = document.querySelector("#idirection");

    switch (document.querySelector("#timing").value) {
        case "1" :
            timing = "ease";
            break;
        case "2" :
            timing = "linear";
            break;
        case "3" :
            timing = "ease-in";
            break;
        case "4" :
            timing = "ease-out";
            break;
        case "5" :
            timing = "ease-in-out";
    }
    const itiming = document.querySelector("#itiming");

    switch (document.querySelector("#fill").value) {
        case "1" :
            fill = "none";
            break;
        case "2" :
            fill = "forwards";
            break;
        case "3" :
            fill = "backwards";
            break;
        case "4" :
            fill = "both";
    }
    const ifill = document.querySelector("#ifill");

    console.log('SetParams:', duration, delay, count, direction, timing, fill);


    stylesheets = document.styleSheets;
    var stylesheet;
    for (i = 0; i < stylesheets.length; i++) {
        console.log(stylesheets[i].ownerNode.id);
        if (stylesheets[i].ownerNode.id == 'animation_stylesheet') {
            stylesheet = stylesheets[i];
        }
    }
    rules = stylesheet.cssRules;

    console.log(stylesheet, rules);

    for (i = 0; i < rules.length; i++) {
        if (rules[i].selectorText) {
            if (rules[i].selectorText.slice(0,8) == '.animate') {
                rule = rules[i];

                rule.style.animationDuration = `${duration}s`;
                iduration.innerHTML = `${duration}`;
                document.querySelector("#id_duration").value = `${duration}`;

                rule.style.animationDelay = `${delay}s`;
                idelay.innerHTML = `${delay}`;
                document.querySelector("#id_delay").value = `${delay}`;

                console.log('count:', count)
                if (count == 0) {
                    rule.style.animationIterationCount = 'infinite';
                    icount.innerHTML = 'infinite';
                    document.querySelector("#id_count").value = 'infinite';
                } else {
                    rule.style.animationIterationCount = `${count}`;
                    icount.innerHTML = `${count}`;
                    document.querySelector("#id_count").value = `${count}`;
                }

                rule.style.animationDirection = `${direction}`;
                idirection.innerHTML = `${direction}`;
                document.querySelector("#id_direction").value = `${direction}`;

                rule.style.animationTimingFunction = `${timing}`;
                itiming.innerHTML = `${timing}`;
                document.querySelector("#id_timing").value = `${timing}`;

                rule.style.animationFillMode = `${fill}`;
                ifill.innerHTML = `${fill}`;
                document.querySelector("#id_fill").value = `${fill}`;

                console.log(rules[i]);
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {

	console.log('PREVIEW');

    document.querySelector("#duration").addEventListener('change', setParams, false);
    document.querySelector("#delay").addEventListener('change', setParams, false);
    document.querySelector("#count").addEventListener('change', setParams, false);
    document.querySelector("#direction").addEventListener('change', setParams, false);
    document.querySelector("#timing").addEventListener('change', setParams, false);
    document.querySelector("#fill").addEventListener('change', setParams, false);

});

