/**
 * TaskCert Exam Interface Logic
 * Decoupled from Django Templates to prevent syntax errors.
 */

class ExamManager {
    constructor() {
        this.examId = null;
        this.attemptId = null;
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.answers = {}; // { questionId: answer }
        this.markedForReview = new Set();
        this.visited = new Set();
        this.durationSeconds = 0;
        this.timerInterval = null;
        this.isProctoringActive = false;

        // DOM Elements cache
        this.elements = {
            intro: null,
            loading: null,
            interface: null,
            result: null,
            timerDisplay: null,
            questionArea: null,
            paletteGrid: null,
            prevBtn: null,
            nextBtn: null,
            reviewBtn: null,
            clearBtn: null,
            submitBtn: null
        };
    }

    // --- Initialization ---

    // Called when clicking the Card Button
    prepareExam(examId) {
        console.log(`Preparing ExamManager for Exam ID: ${examId}`);
        this.examId = examId;
        this.cacheElements(examId);

        // Reset UI to Intro
        this.elements.intro.style.display = 'flex';
        this.elements.loading.style.display = 'none';
        this.elements.interface.style.display = 'none';
    }

    // Called when clicking "I Understand" in Modal
    startExam() {
        if (!this.examId) return;

        this.elements.intro.style.display = 'none';
        this.elements.loading.style.display = 'flex';

        // Start Exam Fetch
        this.startExamSession();
    }

    cacheElements(examId) {
        this.elements.intro = document.getElementById(`examIntro${examId}`);
        this.elements.loading = document.getElementById(`examLoading${examId}`);
        this.elements.interface = document.getElementById(`examInterface${examId}`);
        this.elements.result = document.getElementById(`examResult${examId}`); // Optional

        // Interface elements (scoped to this exam's modal)
        const interfaceEl = this.elements.interface;
        this.elements.timerDisplay = interfaceEl.querySelector('.timer-display');
        this.elements.questionArea = interfaceEl.querySelector('.question-area');
        this.elements.paletteGrid = interfaceEl.querySelector('.palette-grid');

        // Buttons
        this.elements.prevBtn = interfaceEl.querySelector('.btn-prev');
        this.elements.nextBtn = interfaceEl.querySelector('.btn-next');
        this.elements.reviewBtn = interfaceEl.querySelector('.btn-review');
        this.elements.clearBtn = interfaceEl.querySelector('.btn-clear');
        this.elements.submitBtn = interfaceEl.querySelector('.btn-submit');

        // Attach Event Listeners to static buttons
        this.attachButtonListeners();
    }

    attachButtonListeners() {
        this.elements.prevBtn.onclick = () => this.navigate(-1);
        this.elements.nextBtn.onclick = () => this.navigate(1);
        this.elements.reviewBtn.onclick = () => this.toggleReview();
        this.elements.clearBtn.onclick = () => this.clearAnswer();
        this.elements.submitBtn.onclick = () => this.confirmSubmit();
    }

    // --- API Interactions ---

    async startExamSession() {
        try {
            const csrf = this.getCookie('csrftoken');
            const response = await fetch('/api/results/start_exam/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf
                },
                body: JSON.stringify({ exam_id: this.examId })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to start exam');
            }

            // Success
            this.handleStartSuccess(data);

        } catch (error) {
            console.error('Start Exam Error:', error);
            this.showError(error.message);
        }
    }

    handleStartSuccess(data) {
        this.attemptId = data.attempt_id;
        this.questions = data.questions || [];
        this.durationSeconds = data.duration_seconds;

        console.log(`Loaded ${this.questions.length} questions.`);

        // Initialize State
        this.answers = {};
        this.markedForReview = new Set();
        this.visited = new Set();

        // Render
        this.renderPalette();
        this.loadQuestion(0);
        this.startTimer();

        // Transition UI
        this.elements.loading.style.display = 'none';
        this.elements.interface.style.display = 'flex';

        // Proctoring
        this.enterProctorMode();
    }

    async submitExam() {
        // Stop timer
        clearInterval(this.timerInterval);

        try {
            const csrf = this.getCookie('csrftoken');
            const response = await fetch('/api/results/submit_exam/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf
                },
                body: JSON.stringify({
                    attempt_id: this.attemptId,
                    answers: this.answers
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to submit exam');
            }

            // Show Success
            alert(`Exam Submitted!\nScore: ${data.score}%\nPassed: ${data.passed}`);
            window.location.reload(); // Reload to update dashboard

        } catch (error) {
            console.error('Submit Error:', error);
            alert('Error submitting exam: ' + error.message);
        }
    }

    // --- Core UI Logic ---

    loadQuestion(index) {
        if (index < 0 || index >= this.questions.length) return;

        this.currentQuestionIndex = index;
        this.visited.add(this.questions[index].id);

        const q = this.questions[index];
        const savedAnswer = this.answers[q.id] || '';

        // Render Question HTML
        let html = `
            <div class="mb-3">
                <span class="badge bg-secondary mb-2">Question ${index + 1} of ${this.questions.length}</span>
                <h5 class="fw-bold">${q.question_text}</h5>
            </div>
        `;

        // Options
        if (q.question_type === 'multiple_choice' || q.question_type === 'true_false') {
            html += `<div class="d-flex flex-column gap-2">`;
            q.options.forEach(opt => {
                const isChecked = savedAnswer === opt ? 'checked' : '';
                html += `
                    <label class="p-3 border rounded d-flex align-items-center gap-2 cursor-pointer hover-bg-light">
                        <input type="radio" name="q_${q.id}" value="${opt}" ${isChecked} onchange="examManager.saveAnswer('${q.id}', this.value)" class="form-check-input">
                        <span>${opt}</span>
                    </label>
                `;
            });
            html += `</div>`;
        } else {
            // Short answer
            html += `
                <textarea class="form-control" rows="5" placeholder="Type your answer here..." 
                    onchange="examManager.saveAnswer('${q.id}', this.value)">${savedAnswer}</textarea>
            `;
        }

        this.elements.questionArea.innerHTML = html;

        this.updatePalette();
        this.updateButtons();
    }

    saveAnswer(qId, value) {
        this.answers[qId] = value;
        this.updatePalette();
    }

    clearAnswer() {
        const q = this.questions[this.currentQuestionIndex];
        delete this.answers[q.id];
        this.loadQuestion(this.currentQuestionIndex); // Re-render to clear inputs
    }

    toggleReview() {
        const qId = this.questions[this.currentQuestionIndex].id;
        if (this.markedForReview.has(qId)) {
            this.markedForReview.delete(qId);
        } else {
            this.markedForReview.add(qId);
        }
        this.updatePalette();
        this.updateButtons(); // Update button text/style
    }

    // --- Navigation & Palette ---

    navigate(offset) {
        this.loadQuestion(this.currentQuestionIndex + offset);
    }

    jumpToQuestion(index) {
        this.loadQuestion(index);
    }

    updateButtons() {
        // Prev/Next disable states
        this.elements.prevBtn.disabled = this.currentQuestionIndex === 0;
        this.elements.nextBtn.disabled = this.currentQuestionIndex === this.questions.length - 1;

        // Review Button State
        const qId = this.questions[this.currentQuestionIndex].id;
        if (this.markedForReview.has(qId)) {
            this.elements.reviewBtn.innerHTML = '<i class="fas fa-flag"></i> Unmark';
            this.elements.reviewBtn.classList.replace('btn-outline-warning', 'btn-warning');
        } else {
            this.elements.reviewBtn.innerHTML = '<i class="far fa-flag"></i> Mark for Review';
            this.elements.reviewBtn.classList.replace('btn-warning', 'btn-outline-warning');
        }
    }

    renderPalette() {
        this.elements.paletteGrid.innerHTML = '';

        this.questions.forEach((q, idx) => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline-secondary btn-sm';
            btn.textContent = idx + 1;
            btn.style.width = '35px';
            btn.style.height = '35px';
            btn.onclick = () => this.jumpToQuestion(idx);

            // We'll update the class in updatePalette
            btn.id = `palette-btn-${q.id}`;

            this.elements.paletteGrid.appendChild(btn);
        });

        this.updatePalette();
    }

    updatePalette() {
        this.questions.forEach((q, idx) => {
            const btn = document.getElementById(`palette-btn-${q.id}`);
            if (!btn) return;

            // Priority: Attempted > Marked > Visited > Default
            btn.className = 'btn btn-sm ';

            const isAnswered = this.answers[q.id];
            const isMarked = this.markedForReview.has(q.id);
            const isVisited = this.visited.add(q.id) && this.currentQuestionIndex === idx; // Current is always visited

            if (this.currentQuestionIndex === idx) {
                btn.style.border = '2px solid var(--primary)';
            } else {
                btn.style.border = '1px solid #dee2e6';
            }

            if (isMarked) {
                btn.className += 'btn-warning text-white';
            } else if (isAnswered) {
                btn.className += 'btn-success text-white';
            } else if (this.visited.has(q.id)) {
                btn.className += 'btn-outline-danger'; // Not Answered but visited
            } else {
                btn.className += 'btn-light'; // Not Visited
            }
        });
    }

    // --- Timer & Proctoring ---

    startTimer() {
        this.updateTimerDisplay();
        this.timerInterval = setInterval(() => {
            this.durationSeconds--;
            if (this.durationSeconds <= 0) {
                this.submitExam();
            }
            this.updateTimerDisplay();
        }, 1000);
    }

    updateTimerDisplay() {
        const m = Math.floor(this.durationSeconds / 60);
        const s = this.durationSeconds % 60;
        if (this.elements.timerDisplay) {
            this.elements.timerDisplay.textContent = `${m}:${s < 10 ? '0' : ''}${s}`;
            if (this.durationSeconds < 300) { // < 5 mins
                this.elements.timerDisplay.classList.add('text-danger');
            }
        }
    }

    enterProctorMode() {
        const el = document.documentElement;
        if (el.requestFullscreen) el.requestFullscreen();

        // Listen for tab switching
        document.addEventListener("visibilitychange", () => {
            if (document.hidden) {
                alert("WARNING: You left the exam screen. This incident has been recorded.");
            }
        });
    }

    confirmSubmit() {
        const answered = Object.keys(this.answers).length;
        const total = this.questions.length;
        if (confirm(`You have answered ${answered} of ${total} questions. Are you ready to submit?`)) {
            this.submitExam();
        }
    }

    // --- Helpers ---

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    showError(msg) {
        this.elements.loading.innerHTML = `<div class="text-danger p-3">Error: ${msg}</div>`;
    }
}

// Global Instance
window.examManager = new ExamManager();

// Global Helper to be called from the "Start Exam" buttons
window.initExamSetup = function (examId) {
    window.examManager.prepareExam(examId);
};
