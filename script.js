// ==========================================================================
// Spreker Flipklok Timer - Controller & Logica
// ==========================================================================

let timerInterval = null;
let totalTime = 300;       // Totale begintijd in seconden (standaard 5 min)
let timeRemaining = 300;   // Resterende tijd in seconden
let isRunning = false;     // Draait de timer?
let isPaused = false;      // Is de timer gepauzeerd?

// DOM Elementen
const minutesDisplay = document.getElementById('minutes-display');
const secondsDisplay = document.getElementById('seconds-display');
const inputMinutes = document.getElementById('inputMinutes');
const inputSeconds = document.getElementById('inputSeconds');
const startButton = document.getElementById('startButton');
const pauseButton = document.getElementById('pauseButton');
const pauseText = document.getElementById('pauseText');
const resetButton = document.getElementById('resetButton');
const warningSelect = document.getElementById('warningSelect');
const themeSelect = document.getElementById('themeSelect');
const progressBar = document.getElementById('progress-bar');
const fullscreenButton = document.getElementById('fullscreenButton');
const fullscreenText = document.getElementById('fullscreenText');

/**
 * Update de cijfers op de flipklok en de bijbehorende invoervelden.
 */
function updateDisplay() {
    const mins = Math.floor(timeRemaining / 60);
    const secs = timeRemaining % 60;

    const minStr = String(mins).padStart(2, '0');
    const secStr = String(secs).padStart(2, '0');

    // Cijfers direct en rotsvast bijwerken zonder schokkend schalen van het kader
    minutesDisplay.textContent = minStr;
    secondsDisplay.textContent = secStr;

    // Synchroniseer handmatige invoervelden als timer niet loopt
    if (!isRunning) {
        inputMinutes.value = mins;
        inputSeconds.value = secs;
    }

    updateProgressBarAndStatus();
}

/**
 * Berekening van voortgangsbalk en kleurstatussen (Veilig -> Waarschuwing -> Tijd om).
 */
function updateProgressBarAndStatus() {
    // Voortgangsbalk berekenen
    if (totalTime > 0) {
        const percentage = Math.max(0, Math.min(100, (timeRemaining / totalTime) * 100));
        progressBar.style.width = `${percentage}%`;
    } else {
        progressBar.style.width = '100%';
    }

    const warningTime = parseInt(warningSelect.value, 10);

    // Verwijder eerdere status-klassen van de body
    document.body.classList.remove('state-warning', 'state-time-up');

    if (timeRemaining <= 0 && isRunning) {
        document.body.classList.add('state-time-up');
    } else if (warningTime > 0 && timeRemaining <= warningTime && isRunning) {
        document.body.classList.add('state-warning');
    }
}

/**
 * Minuten direct aanpassen via de +/- knoppen.
 */
function adjustMinutes(delta) {
    const currentMins = Math.floor(timeRemaining / 60);
    const currentSecs = timeRemaining % 60;
    let newMins = Math.max(0, currentMins + delta);

    if (newMins === 0 && currentSecs === 0) {
        newMins = 1; // Voorkom 0:00 bij verlagen
    }

    const newTotal = (newMins * 60) + currentSecs;

    if (!isRunning) {
        totalTime = newTotal;
        timeRemaining = newTotal;
    } else {
        timeRemaining = Math.max(0, timeRemaining + (delta * 60));
        totalTime = Math.max(totalTime, timeRemaining);
    }

    updatePresetPillState(totalTime);
    updateDisplay();
}

/**
 * Seconden direct aanpassen via de +/- knoppen.
 */
function adjustSeconds(delta) {
    const currentMins = Math.floor(timeRemaining / 60);
    const currentSecs = timeRemaining % 60;
    let newSecs = currentSecs + delta;
    let newMins = currentMins;

    if (newSecs >= 60) {
        newMins += Math.floor(newSecs / 60);
        newSecs = newSecs % 60;
    } else if (newSecs < 0) {
        if (newMins > 0) {
            newMins -= 1;
            newSecs += 60;
        } else {
            newSecs = 0;
        }
    }

    const newTotal = (newMins * 60) + newSecs;
    if (newTotal === 0) return;

    if (!isRunning) {
        totalTime = newTotal;
        timeRemaining = newTotal;
    } else {
        timeRemaining = Math.max(0, timeRemaining + delta);
        totalTime = Math.max(totalTime, timeRemaining);
    }

    updatePresetPillState(totalTime);
    updateDisplay();
}

/**
 * Snelle preset kiezen (bijv. 30s, 1m, 5m, 10m, etc.).
 */
function setTimePreset(seconds) {
    if (isRunning) {
        const confirmChange = confirm("Timer loopt momenteel. Wil je resetten naar deze tijd?");
        if (!confirmChange) return;
        resetTimer();
    }

    totalTime = seconds;
    timeRemaining = seconds;
    updatePresetPillState(seconds);
    updateDisplay();
}

/**
 * Markeer de juiste preset pill als actief.
 */
function updatePresetPillState(seconds) {
    const pills = document.querySelectorAll('.preset-pill');
    pills.forEach(pill => {
        const onClickAttr = pill.getAttribute('onclick');
        if (onClickAttr && onClickAttr.includes(`(${seconds})`)) {
            pill.classList.add('active');
        } else {
            pill.classList.remove('active');
        }
    });
}

/**
 * Als de gebruiker handmatig getallen intypt in de inputvakjes.
 */
function onDirectInputChange() {
    let mins = parseInt(inputMinutes.value, 10);
    let secs = parseInt(inputSeconds.value, 10);

    if (isNaN(mins) || mins < 0) mins = 0;
    if (isNaN(secs) || secs < 0) secs = 0;
    if (secs > 59) {
        mins += Math.floor(secs / 60);
        secs = secs % 60;
    }

    if (mins === 0 && secs === 0) {
        mins = 1;
    }

    const newTotal = (mins * 60) + secs;
    totalTime = newTotal;
    timeRemaining = newTotal;

    updatePresetPillState(totalTime);
    updateDisplay();
}

/**
 * Start de timer.
 */
function startTimer() {
    clearInterval(timerInterval);

    if (timeRemaining <= 0) {
        onDirectInputChange();
    }

    isRunning = true;
    isPaused = false;
    document.body.classList.add('is-running');

    startButton.style.display = 'none';
    pauseButton.disabled = false;
    pauseText.textContent = 'Pauze';

    updateDisplay();

    timerInterval = setInterval(() => {
        if (timeRemaining <= 1) {
            timeRemaining = 0;
            clearInterval(timerInterval);
            pauseButton.disabled = true;
            startButton.style.display = 'inline-flex';
            document.body.classList.remove('is-running');
            updateDisplay();
            return;
        }

        timeRemaining--;
        updateDisplay();
    }, 1000);
}

/**
 * Pauzeer of hervat de timer.
 */
function togglePause() {
    if (!isRunning) return;

    if (isPaused) {
        isPaused = false;
        pauseText.textContent = 'Pauze';
        document.body.classList.add('is-running');

        timerInterval = setInterval(() => {
            if (timeRemaining <= 1) {
                timeRemaining = 0;
                clearInterval(timerInterval);
                pauseButton.disabled = true;
                startButton.style.display = 'inline-flex';
                document.body.classList.remove('is-running');
                updateDisplay();
                return;
            }
            timeRemaining--;
            updateDisplay();
        }, 1000);
    } else {
        isPaused = true;
        pauseText.textContent = 'Hervatten';
        document.body.classList.remove('is-running');
        clearInterval(timerInterval);
    }
}

/**
 * Reset de timer naar de ingestelde begintijd.
 */
function resetTimer() {
    clearInterval(timerInterval);
    isRunning = false;
    isPaused = false;
    document.body.classList.remove('is-running', 'state-warning', 'state-time-up');

    startButton.style.display = 'inline-flex';
    pauseButton.disabled = true;
    pauseText.textContent = 'Pauze';

    // Herstel naar totale ingestelde tijd
    timeRemaining = totalTime;
    progressBar.style.width = '100%';

    updateDisplay();
}

/**
 * Waarschuwing selectie veranderd.
 */
function onWarningChanged() {
    updateProgressBarAndStatus();
}

/**
 * Schakelen tussen Volledig Scherm en Normaal Venster.
 */
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.warn(`Fullscreen fout: ${err.message}`);
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

document.addEventListener('fullscreenchange', () => {
    if (document.fullscreenElement) {
        fullscreenText.textContent = 'Venster Verlaten';
    } else {
        fullscreenText.textContent = 'Volledig Scherm';
    }
});

/**
 * Thema wisselaar en persistentie.
 */
function changeTheme(themeClass) {
    document.body.classList.remove('theme-dark', 'theme-stage', 'theme-bright');
    document.body.classList.add(themeClass);

    if (themeSelect) {
        themeSelect.value = themeClass;
    }

    try {
        localStorage.setItem('speakerTimerFlipTheme', themeClass);
    } catch (e) {}
}

// Sneltoetsen
document.addEventListener('keydown', (e) => {
    // Negeer toetsen tijdens het typen in een input veld
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

    if (e.key === 'f' || e.key === 'F') {
        e.preventDefault();
        toggleFullscreen();
    } else if (e.code === 'Space') {
        e.preventDefault();
        if (isRunning) {
            togglePause();
        } else {
            startTimer();
        }
    }
});

// Thema inladen bij opstarten
try {
    const savedTheme = localStorage.getItem('speakerTimerFlipTheme');
    if (savedTheme) {
        changeTheme(savedTheme);
    }
} catch (e) {}

// Initiële weergave
updateDisplay();