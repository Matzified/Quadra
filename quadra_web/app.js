const VALID_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789_";
let isRunning = false;
let totalChecked = 0;
let attemptsTarget = 100;
let delay = 2000;
let availableNames = [];

// DOM Elements
const elements = {
    attemptsInput: document.getElementById('attempts'),
    delayInput: document.getElementById('delay'),
    startBtn: document.getElementById('startBtn'),
    stopBtn: document.getElementById('stopBtn'),
    currentStatus: document.getElementById('currentStatus'),
    checkedCount: document.getElementById('checkedCount'),
    foundCount: document.getElementById('foundCount'),
    progressBar: document.getElementById('progressBar'),
    activeUsername: document.getElementById('activeUsername'),
    resultsList: document.getElementById('resultsList'),
    emptyState: document.getElementById('emptyState'),
    copyBtn: document.getElementById('copyBtn')
};

function generateRandom4CharName() {
    let result = '';
    for (let i = 0; i < 4; i++) {
        result += VALID_CHARS.charAt(Math.floor(Math.random() * VALID_CHARS.length));
    }
    return result;
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function updateStatusBadge(state, text) {
    elements.currentStatus.className = `status-badge ${state}`;
    elements.currentStatus.textContent = text;
}

function updateProgress() {
    const percentage = Math.min((totalChecked / attemptsTarget) * 100, 100);
    elements.progressBar.style.width = `${percentage}%`;
    elements.checkedCount.textContent = `Checked: ${totalChecked} / ${attemptsTarget}`;
    elements.foundCount.textContent = `Found: ${availableNames.length}`;
}

function addFoundName(username) {
    availableNames.push(username);
    elements.emptyState.style.display = 'none';
    
    const card = document.createElement('div');
    card.className = 'result-card';
    card.textContent = username;
    
    // Copy interaction
    card.onclick = () => {
        navigator.clipboard.writeText(username);
        card.textContent = 'COPIED!';
        card.style.color = '#fff';
        setTimeout(() => { 
            card.textContent = username; 
            card.style.color = 'var(--success)';
        }, 1000);
    };
    
    elements.resultsList.prepend(card);
}

async function searchLoop() {
    while (isRunning && totalChecked < attemptsTarget) {
        const username = generateRandom4CharName();
        elements.activeUsername.textContent = username;
        elements.activeUsername.className = 'active-username'; // Reset classes

        try {
            // Fetch from local Python backend to bypass CORS
            const response = await fetch(`/api/check?name=${username}`);
            const data = await response.json();

            totalChecked++;

            if (data.available) {
                elements.activeUsername.classList.add('success');
                addFoundName(username);
            } else if (data.status === 'Rate Limited') {
                elements.activeUsername.classList.add('error');
                elements.activeUsername.textContent = 'RATE LIMITED';
                updateStatusBadge('limited', 'Rate Limited');
                updateProgress();
                
                // Wait longer if rate limited
                await sleep(delay * 5); 
                updateStatusBadge('running', 'Running');
                continue;
            } else {
                elements.activeUsername.classList.add('taken');
            }

        } catch (error) {
            console.error('API Error:', error);
            elements.activeUsername.classList.add('error');
            elements.activeUsername.textContent = 'SERVER ERROR';
            totalChecked++;
        }

        updateProgress();
        
        if (isRunning) {
            await sleep(delay);
        }
    }

    if (totalChecked >= attemptsTarget) {
        finishSearch('Completed');
    }
}

function startSearch() {
    if (isRunning) return;
    
    attemptsTarget = parseInt(elements.attemptsInput.value) || 100;
    delay = (parseFloat(elements.delayInput.value) || 2.0) * 1000;
    
    totalChecked = 0;
    availableNames = [];
    
    // Reset UI
    elements.resultsList.innerHTML = '';
    elements.emptyState.style.display = 'block';
    updateProgress();
    elements.progressBar.style.width = '0%';
    elements.activeUsername.textContent = 'Starting...';
    elements.activeUsername.className = 'active-username';
    
    isRunning = true;
    elements.startBtn.classList.add('hidden');
    elements.stopBtn.classList.remove('hidden');
    
    updateStatusBadge('running', 'Running');
    
    searchLoop();
}

function stopSearch() {
    isRunning = false;
    finishSearch('Stopped');
}

function finishSearch(reason = 'Completed') {
    isRunning = false;
    elements.startBtn.classList.remove('hidden');
    elements.stopBtn.classList.add('hidden');
    updateStatusBadge(reason === 'Stopped' ? 'stopped' : 'idle', reason);
    elements.activeUsername.className = 'active-username';
    elements.activeUsername.textContent = `Search ${reason}`;
}

// Event Listeners
elements.startBtn.addEventListener('click', startSearch);
elements.stopBtn.addEventListener('click', stopSearch);

elements.copyBtn.addEventListener('click', () => {
    if (availableNames.length === 0) return;
    const text = availableNames.join('\n');
    navigator.clipboard.writeText(text);
    
    const originalText = elements.copyBtn.textContent;
    elements.copyBtn.textContent = 'Copied!';
    elements.copyBtn.style.background = 'var(--success)';
    elements.copyBtn.style.color = '#000';
    
    setTimeout(() => { 
        elements.copyBtn.textContent = originalText;
        elements.copyBtn.style.background = 'var(--secondary)';
        elements.copyBtn.style.color = '#fff';
    }, 2000);
});
