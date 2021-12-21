
function changeK() {
	k = document.getElementById('K');
    nnc = document.getElementById('nnc');
    href = `/learn/nnc/${k.value}`;
    nnc.setAttribute('href', href);
    console.log(nnc);
}
function changeAlpha() {
	alpha = document.getElementById('alpha');
	gamma = document.getElementById('gamma');
    perceptron = document.getElementById('perceptron');
    href = `/learn/perceptron/${alpha.value}/${gamma.value}`;
    perceptron.setAttribute('href', href);
    console.log(perceptron);
}
function changeClassification() {
	delta = document.getElementById('delta');
    classification = document.getElementById('classification');
    href = `/learn/classification/${delta.value}`;
    classification.setAttribute('href', href);
    console.log(classification);
}

document.addEventListener('DOMContentLoaded', function() {
	console.log('CLASSIFICATION');

	k = document.getElementById('K').addEventListener('change', changeK, false);
    changeK();

	alpha = document.getElementById('alpha').addEventListener('change', changeAlpha, false);
	gamma = document.getElementById('gamma').addEventListener('change', changeAlpha, false);
    changeAlpha();

	delta = document.getElementById('delta').addEventListener('change', changeClassification, false);
    changeClassification();
});
