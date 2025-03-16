document.getElementById('toggleLookup').addEventListener('click', function() {
    document.getElementById('lookupForm').classList.remove('hidden');
    document.getElementById('diagnosisForm').classList.add('hidden');
    this.classList.add('selected');
    document.getElementById('toggleDiagnosis').classList.remove('selected');
});

document.getElementById('toggleDiagnosis').addEventListener('click', function() {
    document.getElementById('lookupForm').classList.add('hidden');
    document.getElementById('diagnosisForm').classList.remove('hidden');
    this.classList.add('selected');
    document.getElementById('toggleLookup').classList.remove('selected');
});

document.querySelector('#lookupForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    fetch('/lookup', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('results');
        if (data.length > 0) {
            resultsDiv.innerHTML = '<h2 class="text-base mb-4 text-left">Results:</h2>' + data.map(disease => `
                <div class="bg-gray-800 p-4 mb-4 rounded-lg shadow-lg border border-gray-600 text-left">
                    <p class="text-sm text-white mb-2"><span class="font-normal">Name:</span> <span class="font-bold">${disease.primary_name}</span></p>
                    <p class="text-sm text-white mb-2"><span class="font-normal">ICD-10-CM Codes:</span> <span class="font-bold">${disease.icd10cm_codes}</span></p>
                    <p class="text-sm text-white mb-2"><span class="font-normal">Type:</span> <span class="font-bold">${disease.is_procedure ? 'Medical Procedure (e.g., surgery, diagnostic tests)' : 'Disease or Condition'}</span></p>
                    <p class="text-sm text-white mb-2"><span class="font-normal">Synonyms:</span> <span class="font-bold">${disease.synonyms.join(', ')}</span></p>
                    <p class="text-sm text-white mb-2"><span class="font-normal">Info Links:</span> <span class="font-bold">${disease.info_links.map(link => `<a href="${link[0]}" target="_blank" class="text-blue-400 hover:underline">${link[1]}</a>`).join(', ')}</span></p>
                </div>
            `).join('');
        } else {
            resultsDiv.innerHTML = '<p class="text-red-500 text-center">No results found.</p>';
        }
    });
});

document.querySelector('#diagnosisForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const spinner = document.getElementById('spinner');
    spinner.style.display = 'block';
    fetch('/diagnosis?' + new URLSearchParams(formData).toString())
    .then(response => response.json())
    .then(data => {
        spinner.style.display = 'none';
        const resultsDiv = document.getElementById('results');
        if (data.length > 0) {
            resultsDiv.innerHTML = '<h2 class="text-base mb-4 text-left">Diagnosis:</h2>' + data.map(disease => `
                <div class="bg-gray-800 p-4 mb-4 rounded-lg shadow-lg border border-gray-600 text-left">
                    <p class="text-lg text-white font-bold mb-2" style="color: #6b8ed6;">${disease.primary_name}</p>
                    <p class="text-sm text-white mb-2">${disease.description}</p>
                    <p class="text-sm text-white mb-2"><span class="font-normal">Possible Remedies:</span> ${disease.remedies}</p>
                </div>
            `).join('');
        } else {
            resultsDiv.innerHTML = '<p class="text-red-500 text-center">No diagnosis found.</p>';
        }
    })
    .catch(error => {
        spinner.style.display = 'none';
        console.error('Error fetching diagnosis:', error);
    });
});

document.getElementById('symptoms').addEventListener('input', function() {
    document.getElementById('results').innerHTML = '';
});