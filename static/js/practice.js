let sessionCount = 0;
let recognition = null;
let isRecording = false;
let conversationHistory = [];

function getStudentName() {
    if (typeof CURRENT_STUDENT_NAME !== 'undefined' && CURRENT_STUDENT_NAME && CURRENT_STUDENT_NAME.trim()) {
        return CURRENT_STUDENT_NAME.trim().split(' ')[0];
    }
    const local = localStorage.getItem('speakup_student_name');
    if (local && local.trim()) {
        return local.trim().split(' ')[0];
    }
    return 'there';
}

function getStudentInitials() {
    let name = '';
    if (typeof CURRENT_STUDENT_NAME !== 'undefined' && CURRENT_STUDENT_NAME && CURRENT_STUDENT_NAME.trim()) {
        name = CURRENT_STUDENT_NAME.trim();
    } else {
        name = localStorage.getItem('speakup_student_name') || '';
    }
    
    if (name) {
        const parts = name.split(/\s+/);
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return parts[0].slice(0, 2).toUpperCase();
    }
    return 'ME';
}

function getWelcomeMessage(topicKey) {
    const name = getStudentName();
    switch (topicKey) {
        case "ordering-cafe":
            return `Hello ${name}! Welcome to The Green Bean Cafe. What can I brew fresh for you today?`;
        case "college-life":
            return `Hi ${name}! How is your semester going? Are you preparing for any project presentations or exams?`;
        case "job-interview":
            return `Welcome to your mock interview session, ${name}! Take a calm breath. Let's start: 'Tell me about yourself and your background.'`;
        case "casual-chitchat":
        default:
            return `Hey ${name}! How has your week been so far? Tell me about something enjoyable you did recently.`;
    }
}

const TOPIC_CONFIG = {
    "ordering-cafe": {
        starters: [
            "Could I please get a medium cappuccino?",
            "Do you have any oat milk options?",
            "I would like to order a fresh croissant."
        ],
        vocab: [
            { word: "Decaf", def: "Coffee without caffeine" },
            { word: "Oat milk", def: "Plant-based milk alternative" },
            { word: "To go / Takeaway", def: "Take food/drink outside" }
        ]
    },
    "college-life": {
        starters: [
            "I am currently preparing for my semester exams.",
            "Our team is building an exciting AI web application.",
            "Could you give me advice on speaking up during lectures?"
        ],
        vocab: [
            { word: "Curriculum", def: "The subjects comprising a course of study" },
            { word: "Collaborate", def: "Work together to achieve a goal" },
            { word: "Deadline", def: "The latest time by which work must be finished" }
        ]
    },
    "job-interview": {
        starters: [
            "Certainly. I am a computer science student passionate about web engineering.",
            "In my previous semester project, I led frontend development.",
            "I pride myself on being adaptable, organized, and collaborative."
        ],
        vocab: [
            { word: "Articulate", def: "Express ideas clearly and fluently" },
            { word: "Perseverance", def: "Determination in the face of difficulties" },
            { word: "Impactful", def: "Having a major positive effect" }
        ]
    },
    "casual-chitchat": {
        starters: [
            "I had a really productive weekend catching up on coding.",
            "I watched an inspiring documentary yesterday.",
            "To be honest, the weather has been really pleasant today."
        ],
        vocab: [
            { word: "Leisure", def: "Time when one is not working; relaxation" },
            { word: "Fascinating", def: "Extremely interesting or captivating" },
            { word: "In a nutshell", def: "In very brief words" }
        ]
    }
};

document.addEventListener('DOMContentLoaded', () => {
    initSpeechRecognition();
    
    const urlParams = new URLSearchParams(window.location.search);
    const topicParam = urlParams.get('topic');
    if (topicParam && TOPIC_CONFIG[topicParam]) {
        const select = document.getElementById('practiceTopicSelect');
        if (select) {
            select.value = topicParam;
        }
    }
    
    handleTopicChange();
});

function insertStarter(text) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = text;
        input.focus();
    }
}

function updateStartersBar(suggestions) {
    const startersBar = document.getElementById('startersBar');
    if (!startersBar || !suggestions || !suggestions.length) return;

    let html = '<span class="starters-label">Try saying:</span>';
    suggestions.forEach(item => {
        const escaped = item.replace(/'/g, "\\'");
        html += `<button type="button" class="starter-pill" onclick="insertStarter('${escaped}')">"${item}"</button>`;
    });
    startersBar.innerHTML = html;
}

function handleTopicChange() {
    const select = document.getElementById('practiceTopicSelect');
    const topicKey = select ? select.value : 'ordering-cafe';
    const config = TOPIC_CONFIG[topicKey] || TOPIC_CONFIG['ordering-cafe'];

    updateStartersBar(config.starters);

    const vocabList = document.getElementById('contextVocabList');
    if (vocabList) {
        let vocabHtml = '';
        config.vocab.forEach(item => {
            vocabHtml += `
                <div class="context-vocab-item">
                    <strong>${item.word}</strong>
                    <span>${item.def}</span>
                </div>
            `;
        });
        vocabList.innerHTML = vocabHtml;
    }

    restartConversation(getWelcomeMessage(topicKey));
}

function restartConversation(customWelcome) {
    const chatContainer = document.getElementById('chatMessages');
    const select = document.getElementById('practiceTopicSelect');
    const topicKey = select ? select.value : 'ordering-cafe';
    const welcomeText = customWelcome || getWelcomeMessage(topicKey);

    sessionCount = 0;
    updateSessionCount();

    conversationHistory = [
        { role: "assistant", content: welcomeText }
    ];

    if (chatContainer) {
        chatContainer.innerHTML = `
            <div class="chat-row ai-row">
                <div class="row-avatar">S</div>
                <div class="message-bubble-box">
                    <div class="chat-bubble-content">${welcomeText}</div>
                    <button type="button" class="btn-speech-play" onclick="playTextAudio(this)">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>
                        <span>Listen to Sophia</span>
                    </button>
                </div>
            </div>
        `;
    }

    const feedbackPanel = document.getElementById('grammarFeedbackPanel');
    if (feedbackPanel) {
        feedbackPanel.innerHTML = `
            <div class="feedback-empty-state">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                <p>Speak naturally! If you make a common mistake, friendly tips and explanations will appear here.</p>
            </div>
        `;
    }
}

async function handleSendMessage(event) {
    if (event) event.preventDefault();

    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    const select = document.getElementById('practiceTopicSelect');
    const topic = select ? select.value : 'ordering-cafe';
    const levelSelect = document.getElementById('practiceLevelSelect');
    const level = levelSelect ? levelSelect.value : 'intermediate';

    renderUserMessage(message);
    conversationHistory.push({ role: "user", content: message });
    sessionCount++;
    updateSessionCount();

    showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                topic: topic,
                level: level,
                history: conversationHistory,
                student_name: getStudentName()
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        removeTypingIndicator();

        if (data.success && data.ai_response) {
            if (data.grammar_feedback && data.grammar_feedback.length > 0) {
                renderGrammarFeedback(data.grammar_feedback);
            }

            renderAiMessage(data.ai_response);
            conversationHistory.push({ role: "assistant", content: data.ai_response });

            if (data.suggested_vocab && data.suggested_vocab.length > 0) {
                updateStartersBar(data.suggested_vocab);
            }
        } else {
            fallbackAiResponse(message, topic);
        }
    } catch (err) {
        console.warn('Network or API issue:', err);
        removeTypingIndicator();
        fallbackAiResponse(message, topic);
    }
}

function fallbackAiResponse(message, topic) {
    const name = getStudentName();
    const reply = `That is a thoughtful point, ${name}! Practicing expressing yourself clearly like this builds real speaking fluency. Could you elaborate a little more on that?`;
    renderAiMessage(reply);
    conversationHistory.push({ role: "assistant", content: reply });
}

function renderUserMessage(text) {
    const chatContainer = document.getElementById('chatMessages');
    const row = document.createElement('div');
    row.className = 'chat-row user-row';
    row.innerHTML = `
        <div class="row-avatar">${getStudentInitials()}</div>
        <div class="message-bubble-box">
            <div class="chat-bubble-content">${escapeHtml(text)}</div>
        </div>
    `;
    chatContainer.appendChild(row);
    scrollToBottom();
}

function renderAiMessage(text) {
    const chatContainer = document.getElementById('chatMessages');
    const row = document.createElement('div');
    row.className = 'chat-row ai-row';
    row.innerHTML = `
        <div class="row-avatar">S</div>
        <div class="message-bubble-box">
            <div class="chat-bubble-content">${escapeHtml(text)}</div>
            <button type="button" class="btn-speech-play" onclick="playTextAudio(this)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>
                <span>Listen to Sophia</span>
            </button>
        </div>
    `;
    chatContainer.appendChild(row);
    scrollToBottom();
}

function renderGrammarFeedback(corrections) {
    const chatContainer = document.getElementById('chatMessages');
    const feedbackPanel = document.getElementById('grammarFeedbackPanel');

    corrections.forEach(corr => {
        const card = document.createElement('div');
        card.className = 'inline-grammar-card';
        card.innerHTML = `
            <div class="header-tip">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                <span>Smart Grammar Tip</span>
            </div>
            <div class="diff-text">
                Instead of <strong>"${escapeHtml(corr.found)}"</strong> &rarr; try: <ins>${escapeHtml(corr.suggestion)}</ins>
            </div>
            <div class="explanation-text">${escapeHtml(corr.explanation)}</div>
        `;
        chatContainer.appendChild(card);

        if (feedbackPanel) {
            feedbackPanel.innerHTML = `
                <div style="background-color: #FAF9FF; border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                    <div style="font-size: 0.82rem; font-weight: 700; color: var(--brand-primary); margin-bottom: 4px;">Recent Correction:</div>
                    <div style="font-size: 0.88rem; color: var(--text-dark); margin-bottom: 4px;">
                        Say: <strong style="color: #22A06B;">${escapeHtml(corr.suggestion)}</strong>
                    </div>
                    <div style="font-size: 0.78rem; color: var(--text-muted);">${escapeHtml(corr.explanation)}</div>
                </div>
            `;
        }
    });

    scrollToBottom();
}

function showTypingIndicator() {
    const chatContainer = document.getElementById('chatMessages');
    const existing = document.getElementById('typingIndicator');
    if (existing) existing.remove();

    const indicator = document.createElement('div');
    indicator.id = 'typingIndicator';
    indicator.className = 'chat-row ai-row';
    indicator.innerHTML = `
        <div class="row-avatar">S</div>
        <div class="typing-indicator-box">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatContainer.appendChild(indicator);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function updateSessionCount() {
    const el = document.getElementById('sessionMessageCount');
    if (el) el.textContent = sessionCount;
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chatMessages');
    if (chatContainer) {
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 50);
    }
}

function playTextAudio(btn) {
    if (!('speechSynthesis' in window)) {
        showToast('Text-to-speech is not supported on this browser.');
        return;
    }

    const bubble = btn.parentElement.querySelector('.chat-bubble-content');
    if (!bubble) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(bubble.innerText);
    utterance.rate = 0.95;
    utterance.pitch = 1.05;
    utterance.lang = 'en-US';

    btn.style.opacity = '0.6';
    utterance.onend = () => { btn.style.opacity = '1'; };
    utterance.onerror = () => { btn.style.opacity = '1'; };

    window.speechSynthesis.speak(utterance);
    showToast('Playing spoken audio 🔊');
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isRecording = true;
        updateMicUI(true);
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('chatInput');
        if (input) {
            input.value = transcript;
            showToast('Voice captured! Sending response...');
            setTimeout(() => {
                handleSendMessage();
            }, 600);
        }
    };

    recognition.onerror = (event) => {
        isRecording = false;
        updateMicUI(false);
        showToast('Microphone note: ' + event.error);
    };

    recognition.onend = () => {
        isRecording = false;
        updateMicUI(false);
    };
}

function toggleSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition || !recognition) {
        showToast('Voice input is supported on modern Chrome or Edge. You can also type directly!');
        return;
    }

    if (isRecording) {
        recognition.stop();
        isRecording = false;
        updateMicUI(false);
    } else {
        try {
            recognition.start();
        } catch (e) {
            console.warn(e);
        }
    }
}

function updateMicUI(active) {
    const micBtn = document.getElementById('micBtn');
    const banner = document.getElementById('micStatusBanner');
    if (micBtn) {
        if (active) micBtn.classList.add('listening');
        else micBtn.classList.remove('listening');
    }
    if (banner) {
        if (active) banner.classList.add('visible');
        else banner.classList.remove('visible');
    }
}

function escapeHtml(string) {
    const div = document.createElement('div');
    div.innerText = string;
    return div.innerHTML;
}
