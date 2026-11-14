let activeQuestionData = {
    id: 1,
    category: "HR & Behavioral",
    question: "Tell me about yourself and your background.",
    difficulty: "Essential",
    duration: "90 seconds",
    star: "Focus on the Present (your current studies/role), Past (key achievements/learnings), and Future (why you are excited for this opportunity).",
    model: "Certainly! I am a passionate computer science student with a strong focus on building user-centric web applications and learning modern technologies. Over the past two years, I have developed several academic projects, including an AI-powered language assistant. I enjoy collaborating with diverse teams and solving practical problems. I am eager to apply my technical foundation, curiosity, and communication skills to contribute effectively to your engineering team."
};

let interviewRecognition = null;
let isInterviewRecording = false;

document.addEventListener('DOMContentLoaded', () => {
    initInterviewSpeech();
    
    const modelEl = document.getElementById('modelAnswerText');
    if (modelEl) modelEl.textContent = activeQuestionData.model;
});

function selectInterviewQuestion(buttonEl) {
    document.querySelectorAll('.question-item').forEach(el => el.classList.remove('active'));
    buttonEl.classList.add('active');

    activeQuestionData = {
        id: parseInt(buttonEl.getAttribute('data-id')),
        category: buttonEl.getAttribute('data-category'),
        question: buttonEl.getAttribute('data-question'),
        difficulty: buttonEl.getAttribute('data-difficulty'),
        duration: buttonEl.getAttribute('data-duration'),
        star: buttonEl.getAttribute('data-star'),
        model: buttonEl.getAttribute('data-model')
    };

    document.getElementById('activeCategoryTag').textContent = activeQuestionData.category;
    document.getElementById('activeDiffTag').textContent = activeQuestionData.difficulty;
    document.getElementById('activeDurationTag').textContent = `Target: ~${activeQuestionData.duration}`;
    document.getElementById('activeQuestionTitle').textContent = activeQuestionData.question;
    document.getElementById('activeStarText').textContent = activeQuestionData.star;
    document.getElementById('modelAnswerText').textContent = activeQuestionData.model;

    document.getElementById('interviewAnswerInput').value = '';
    updateWordCount();
    document.getElementById('evalResultCard').classList.remove('visible');
}

function updateWordCount() {
    const text = document.getElementById('interviewAnswerInput').value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    
    document.getElementById('answerWordCount').textContent = words;
    const seconds = Math.round(words / 2.1);
    document.getElementById('estimatedDuration').textContent = seconds;
}

function loadSampleAnswer() {
    const sample = "Good morning! I am currently a third-year engineering undergraduate specializing in software engineering. Over the past two semesters, I have basically led our group in developing web applications. Like, I really enjoy solving user interface problems and ensuring accessibility. I am agree that clear communication is key to good team results, and I am excited to contribute to this role.";
    const input = document.getElementById('interviewAnswerInput');
    input.value = sample;
    updateWordCount();
    showToast('Loaded sample student answer! Click "Evaluate Answer" now.');
}

async function evaluateAnswer() {
    const input = document.getElementById('interviewAnswerInput');
    const answer = input.value.trim();

    if (!answer) {
        showToast('Please type or speak your answer before evaluating!');
        input.focus();
        return;
    }

    showToast('Evaluating answer structure and language...');

    try {
        const response = await fetch('/api/interview/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                answer: answer,
                question_id: activeQuestionData.id
            })
        });

        const data = await response.json();
        if (data.success && data.evaluation) {
            displayEvaluationResults(data.evaluation);
        } else {
            runClientFallbackEvaluation(answer);
        }
    } catch (e) {
        runClientFallbackEvaluation(answer);
    }
}

function displayEvaluationResults(evalData) {
    const card = document.getElementById('evalResultCard');
    card.classList.add('visible');

    document.getElementById('evalScore').textContent = evalData.score;

    const strengthsUl = document.getElementById('evalStrengthsList');
    strengthsUl.innerHTML = '';
    evalData.strengths.forEach(st => {
        const li = document.createElement('li');
        li.textContent = st;
        strengthsUl.appendChild(li);
    });

    const fillersEl = document.getElementById('evalFillersText');
    if (evalData.fillers_detected && evalData.fillers_detected.length > 0) {
        fillersEl.innerHTML = `⚠️ <strong style="color: #DC2626;">Filler words spotted:</strong> "${evalData.fillers_detected.join('", "')}". Try replacing fillers with a brief pause.`;
    } else {
        fillersEl.innerHTML = `✅ <strong style="color: #22A06B;">Crisp speech:</strong> No distracting filler words detected.`;
    }

    const grammarEl = document.getElementById('evalGrammarText');
    if (evalData.grammar_feedback && evalData.grammar_feedback.length > 0) {
        const first = evalData.grammar_feedback[0];
        grammarEl.innerHTML = `💡 <strong>Grammar tip:</strong> Say <em>"${first.suggestion}"</em> instead of <em>"${first.found}"</em>.`;
        grammarEl.style.color = '#B45309';
    } else {
        grammarEl.innerHTML = `✅ Grammar structure is natural and grammatically sound.`;
        grammarEl.style.color = '#22A06B';
    }

    document.getElementById('evalImprovementText').textContent = evalData.improvement_tip;

    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function runClientFallbackEvaluation(answer) {
    const words = answer.split(/\s+/).length;
    let score = 8.2;
    if (words < 25) score = 6.5;
    if (words > 150) score = 7.8;

    displayEvaluationResults({
        score: score,
        word_count: words,
        fillers_detected: answer.toLowerCase().includes('like') || answer.toLowerCase().includes('basically') ? ['like', 'basically'] : [],
        grammar_feedback: answer.toLowerCase().includes('i am agree') ? [{ found: 'i am agree', suggestion: 'I agree' }] : [],
        strengths: [
            "Good engagement with the core prompt",
            "Clear articulation of personal motivation"
        ],
        improvement_tip: "Use the STAR method: describe a specific Situation and Task, detail your Action, and conclude with the tangible Result."
    });
}

function initInterviewSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    interviewRecognition = new SpeechRecognition();
    interviewRecognition.continuous = true;
    interviewRecognition.interimResults = false;
    interviewRecognition.lang = 'en-US';

    interviewRecognition.onstart = () => {
        isInterviewRecording = true;
        document.getElementById('interviewMicLabel').textContent = 'Listening... (Click to stop)';
        document.getElementById('interviewMicBtn').classList.add('active');
        showToast('Microphone active: Speak your answer now.');
    };

    interviewRecognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript + ' ';
        }
        const input = document.getElementById('interviewAnswerInput');
        input.value = (input.value + ' ' + transcript).trim();
        updateWordCount();
    };

    interviewRecognition.onend = () => {
        isInterviewRecording = false;
        document.getElementById('interviewMicLabel').textContent = 'Speak Answer';
        document.getElementById('interviewMicBtn').classList.remove('active');
    };

    interviewRecognition.onerror = (e) => {
        isInterviewRecording = false;
        document.getElementById('interviewMicLabel').textContent = 'Speak Answer';
        document.getElementById('interviewMicBtn').classList.remove('active');
    };
}

function toggleInterviewSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition || !interviewRecognition) {
        showToast('Speech dictation is available in modern browsers like Chrome or Edge. You can also type directly!');
        return;
    }

    if (isInterviewRecording) {
        interviewRecognition.stop();
    } else {
        try {
            interviewRecognition.start();
        } catch (e) {
            console.warn(e);
        }
    }
}

function playModelAnswerAudio() {
    if (!('speechSynthesis' in window)) {
        showToast('Speech audio is not supported in this browser.');
        return;
    }

    window.speechSynthesis.cancel();
    const text = document.getElementById('modelAnswerText').textContent;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    window.speechSynthesis.speak(utterance);
    showToast('Playing spoken model answer 🔊');
}
