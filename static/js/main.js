document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const resultsSection = document.getElementById('resultsSection');
    const resultsBody = document.getElementById('resultsBody');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const jobsList = document.getElementById('jobsList');

    // Gestion du drag & drop
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileInfo(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            updateFileInfo(e.target.files[0]);
        }
    });

    function updateFileInfo(file) {
        fileName.textContent = file.name;
        fileInfo.classList.remove('d-none');
    }

    // Soumission du formulaire
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(uploadForm);
        
        if (!fileInput.files[0]) {
            alert('Veuillez sélectionner un fichier');
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyse en cours...';

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showResults(result);
                loadJobs();
            } else {
                alert(`Erreur: ${result.error}`);
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur s\'est produite lors de l\'analyse');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-magic"></i> Lancer l\'analyse';
        }
    });

    function showResults(result) {
        resultsSection.style.display = 'block';
        
        let html = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i> Analyse terminée avec succès !
                <a href="/results/${result.job_id}" class="btn btn-sm btn-success float-end">
                    <i class="fas fa-external-link-alt"></i> Voir les résultats
                </a>
            </div>
            <p><strong>Job ID:</strong> ${result.job_id}</p>
        `;

        if (result.files && result.files.length > 0) {
            html += '<h6>Fichiers générés:</h6><ul class="list-unstyled">';
            result.files.forEach(file => {
                html += `
                    <li>
                        <i class="fas fa-file"></i> ${file.name}
                        <a href="${file.url}" class="btn btn-sm btn-link">Télécharger</a>
                    </li>
                `;
            });
            html += '</ul>';
        }

        resultsBody.innerHTML = html;
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Charger l'historique des jobs
    async function loadJobs() {
        try {
            const response = await fetch('/api/jobs');
            const jobs = await response.json();
            
            if (jobs.length === 0) {
                jobsList.innerHTML = '<p class="text-muted text-center">Aucune analyse récente</p>';
                return;
            }

            let html = '<div class="list-group">';
            jobs.slice(0, 5).forEach(job => {
                const date = new Date(job.created * 1000).toLocaleString('fr-FR');
                html += `
                    <a href="/results/${job.id}" class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1"><i class="fas fa-folder-open"></i> Job ${job.id}</h6>
                            <small class="text-muted">${date}</small>
                        </div>
                        <p class="mb-1">${job.files_count} fichier(s) généré(s)</p>
                    </a>
                `;
            });
            html += '</div>';
            
            jobsList.innerHTML = html;
        } catch (error) {
            console.error('Erreur chargement jobs:', error);
            jobsList.innerHTML = '<p class="text-muted text-center">Erreur de chargement</p>';
        }
    }

    // Charger les jobs au démarrage
    loadJobs();
});
