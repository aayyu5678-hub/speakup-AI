const SAVED_WORDS_STORAGE_KEY = 'speakup_saved_words';
let currentCategory = 'all';
let searchDebounceTimer = null;
let lastLookedUpQuery = '';
let activeLookupSeq = 0;

document.addEventListener('DOMContentLoaded', () => {
    initSavedBookmarks();
});

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function initSavedBookmarks() {
    let saved = [];
    if (typeof INITIAL_SAVED_IDS !== 'undefined' && Array.isArray(INITIAL_SAVED_IDS)) {
        saved = INITIAL_SAVED_IDS;
        saveWordIds(saved);
    } else {
        saved = getSavedWordIds();
    }

    document.querySelectorAll('.btn-bookmark').forEach(btn => {
        const id = parseInt(btn.getAttribute('data-id'), 10);
        updateGridBookmarkBtn(btn, saved.includes(id));
    });

    if (typeof DAILY_WORD !== 'undefined' && DAILY_WORD) {
        updateSpotlightBookmarkBtn(saved.includes(DAILY_WORD.id));
    }
}

function getSavedWordIds() {
    try {
        const data = localStorage.getItem(SAVED_WORDS_STORAGE_KEY);
        return data ? JSON.parse(data) : [1];
    } catch (e) {
        return [1];
    }
}

function saveWordIds(ids) {
    try {
        localStorage.setItem(SAVED_WORDS_STORAGE_KEY, JSON.stringify(ids));
    } catch (e) {
        console.warn('LocalStorage error', e);
    }
}

function updateGridBookmarkBtn(btn, isSaved) {
    if (!btn) return;
    if (isSaved) {
        btn.classList.add('active');
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="#F59E0B" stroke="#F59E0B" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>`;
    } else {
        btn.classList.remove('active');
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>`;
    }
}

function updateSpotlightBookmarkBtn(isSaved) {
    const spotlightBtn = document.getElementById('spotlightSaveBtn');
    if (!spotlightBtn) return;
    if (isSaved) {
        spotlightBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#F59E0B" stroke="#F59E0B" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg><span>Saved in My List ★</span>`;
    } else {
        spotlightBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg><span>Save to My List</span>`;
    }
}

function syncBookmarkButtonsUI(wordId, isSaved) {
    document.querySelectorAll(`.btn-bookmark[data-id="${wordId}"]`).forEach(b => {
        updateGridBookmarkBtn(b, isSaved);
    });
    if (typeof DAILY_WORD !== 'undefined' && DAILY_WORD && DAILY_WORD.id === wordId) {
        updateSpotlightBookmarkBtn(isSaved);
    }
    const lookupSaveBtn = document.getElementById('lookupSaveBtn');
    if (lookupSaveBtn && parseInt(lookupSaveBtn.getAttribute('data-id'), 10) === wordId) {
        lookupSaveBtn.innerHTML = isSaved
            ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="#F59E0B" stroke="#F59E0B" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg><span>Saved in My List ★</span>`
            : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg><span>Save to My List</span>`;
    }
}

function playWordFromCard(btn) {
    const card = btn.closest('.vocab-card');
    const word = card ? card.getAttribute('data-word') : '';
    if (word) playWordAudio(word);
}

function toggleCardBookmark(btn) {
    const card = btn.closest('.vocab-card');
    const wordId = parseInt(btn.getAttribute('data-id'), 10);
    const wordText = card ? card.getAttribute('data-word') : `Word #${wordId}`;
    toggleSaveWord(wordId, btn, wordText);
}

async function toggleSaveWord(wordId, btn, wordText, entryObj) {
    let saved = getSavedWordIds();
    const isSaved = saved.includes(wordId);

    if (!wordText) {
        const card = btn ? (btn.closest('.vocab-card') || document.querySelector(`.vocab-card[data-id="${wordId}"]`)) : null;
        wordText = card ? card.getAttribute('data-word') : `Word #${wordId}`;
    }

    const nextSavedState = !isSaved;
    if (nextSavedState) {
        saved.push(wordId);
        showToast(`"${wordText}" saved to your revision list! ⭐`);
        if (entryObj) ensureCardInGrid(entryObj);
    } else {
        saved = saved.filter(id => id !== wordId);
        showToast(`"${wordText}" removed from saved list`);
    }

    saveWordIds(saved);
    syncBookmarkButtonsUI(wordId, nextSavedState);

    try {
        await fetch('/api/vocabulary/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word_id: wordId, word_text: wordText })
        });
    } catch (e) {
        console.warn('Notice: Background sync to SQLite:', e);
    }

    if (currentCategory === 'saved') {
        applyFilters();
    }
}

function playWordAudio(word) {
    if (!('speechSynthesis' in window)) {
        showToast('Speech audio is not supported in this browser.');
        return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = 'en-US';
    utterance.rate = 0.85;
    utterance.pitch = 1.0;

    window.speechSynthesis.speak(utterance);
    showToast(`Pronouncing: "${word}" 🔊`);
}

async function refreshDailyWord() {
    const btn = document.getElementById('refreshDailyWordBtn');
    const currentWord = (typeof DAILY_WORD !== 'undefined' && DAILY_WORD && DAILY_WORD.word) ? DAILY_WORD.word : '';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span><span>Loading...</span>';
    }

    try {
        const url = `/api/vocabulary/daily?refresh=1&exclude=${encodeURIComponent(currentWord)}`;
        const resp = await fetch(url);
        const data = await resp.json();
        if (data.success && data.word) {
            renderSpotlightWord(data.word);
            showToast(`Word of the Day updated: "${data.word.word}"`);
        } else {
            showToast('Could not fetch a new daily word right now.');
        }
    } catch (e) {
        console.warn('Daily word refresh error:', e);
        showToast('Network error while loading new daily word.');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span>🔄</span><span>New Word</span>';
        }
    }
}

function renderSpotlightWord(wordObj) {
    DAILY_WORD = wordObj;
    const saved = getSavedWordIds();

    const dateEl = document.getElementById('spotlightDate');
    const wordEl = document.getElementById('spotlightWord');
    const phoneticEl = document.getElementById('spotlightPhonetic');
    const posEl = document.getElementById('spotlightPos');
    const diffEl = document.getElementById('spotlightDiff');
    const defEl = document.getElementById('spotlightDef');
    const synWrap = document.getElementById('spotlightSynonyms');
    const exEl = document.getElementById('spotlightExample');
    const tipEl = document.getElementById('spotlightTip');

    if (dateEl) dateEl.textContent = wordObj.date || 'Today';
    if (wordEl) wordEl.textContent = wordObj.word || '';
    if (phoneticEl) phoneticEl.textContent = wordObj.phonetic || '';
    if (posEl) posEl.textContent = wordObj.part_of_speech || 'Word';
    if (diffEl) {
        const diff = wordObj.difficulty || 'Intermediate';
        diffEl.textContent = diff;
        diffEl.className = `badge-tag diff-${diff}`;
    }
    if (defEl) defEl.textContent = wordObj.definition || '';
    if (synWrap) {
        const syns = Array.isArray(wordObj.synonyms) ? wordObj.synonyms : [];
        if (syns.length > 0) {
            synWrap.style.display = 'flex';
            synWrap.innerHTML = '<span class="vocab-syn-label">Synonyms:</span>' +
                syns.map(s => `<span class="vocab-syn-pill">${escapeHtml(s)}</span>`).join('');
        } else {
            synWrap.style.display = 'none';
            synWrap.innerHTML = '';
        }
    }
    if (exEl) exEl.textContent = wordObj.example ? `"${wordObj.example}"` : '';
    if (tipEl) tipEl.textContent = wordObj.tip || '';

    updateSpotlightBookmarkBtn(saved.includes(wordObj.id));
}

function filterCategory(category, clickedTab) {
    currentCategory = category;

    if (clickedTab) {
        document.querySelectorAll('.filter-tab').forEach(tab => tab.classList.remove('active'));
        clickedTab.classList.add('active');
    }

    applyFilters();
}

function handleVocabSearch() {
    applyFilters();

    const searchInput = document.getElementById('vocabSearchInput');
    const query = searchInput ? searchInput.value.trim() : '';
    const lookupSection = document.getElementById('dictionaryLookupSection');

    if (searchDebounceTimer) {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = null;
    }

    if (!query) {
        lastLookedUpQuery = '';
        activeLookupSeq++;
        if (lookupSection) {
            lookupSection.style.display = 'none';
            lookupSection.innerHTML = '';
        }
        return;
    }

    if (query.length >= 2 && !hasExactCuratedCard(query)) {
        searchDebounceTimer = setTimeout(() => {
            if (lastLookedUpQuery !== query.toLowerCase()) {
                lookupWordMeaning(query);
            }
        }, 650);
    } else if (hasExactCuratedCard(query) && lookupSection) {
        lookupSection.style.display = 'none';
        lookupSection.innerHTML = '';
    }
}

function hasExactCuratedCard(query) {
    const lowerQ = query.trim().toLowerCase();
    return Array.from(document.querySelectorAll('.vocab-card')).some(card => {
        return (card.getAttribute('data-word') || '').trim().toLowerCase() === lowerQ;
    });
}

function lookupWordFromInput() {
    if (searchDebounceTimer) {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = null;
    }
    const searchInput = document.getElementById('vocabSearchInput');
    const query = searchInput ? searchInput.value.trim() : '';
    if (!query) {
        showToast('Type any English word or phrase to look up its meaning.');
        if (searchInput) searchInput.focus();
        return;
    }
    lookupWordMeaning(query);
}

async function lookupWordMeaning(rawWord) {
    const query = (rawWord || '').trim();
    if (!query) return;

    const seq = ++activeLookupSeq;
    lastLookedUpQuery = query.toLowerCase();

    const lookupSection = document.getElementById('dictionaryLookupSection');
    const lookupBtn = document.getElementById('vocabLookupBtn');
    const emptyState = document.getElementById('vocabEmptyState');

    if (lookupBtn) {
        lookupBtn.disabled = true;
        lookupBtn.textContent = 'Searching...';
    }
    if (lookupSection) {
        lookupSection.style.display = 'block';
        lookupSection.innerHTML = `
            <div class="dictionary-lookup-card">
                <div style="display:flex; align-items:center; gap:10px; color: var(--brand-deep-indigo); font-weight:600;">
                    <span>🔍 Looking up meaning for "<strong>${escapeHtml(query)}</strong>" in the full English dictionary...</span>
                </div>
            </div>
        `;
    }

    try {
        const resp = await fetch(`/api/vocabulary/lookup?word=${encodeURIComponent(query)}`);
        const data = await resp.json();

        if (seq !== activeLookupSeq) return;

        if (resp.ok && data.success && data.entry) {
            renderLookupResultCard(data.entry);
            if (emptyState) emptyState.style.display = 'none';
        } else {
            renderLookupError(data.error || `No definition found for "${query}".`);
        }
    } catch (e) {
        if (seq !== activeLookupSeq) return;
        renderLookupError('Could not connect to the dictionary lookup service right now.');
    } finally {
        if (lookupBtn && seq === activeLookupSeq) {
            lookupBtn.disabled = false;
            lookupBtn.textContent = 'Look Up';
        }
    }
}

function renderLookupResultCard(entry) {
    const lookupSection = document.getElementById('dictionaryLookupSection');
    if (!lookupSection) return;

    const saved = getSavedWordIds();
    const isSaved = saved.includes(entry.id);
    const syns = Array.isArray(entry.synonyms) ? entry.synonyms : [];
    const synsHtml = syns.length > 0
        ? `<div class="vocab-synonyms-row"><span class="vocab-syn-label">Synonyms:</span>${syns.map(s => `<span class="vocab-syn-pill">${escapeHtml(s)}</span>`).join('')}</div>`
        : '';

    lookupSection.style.display = 'block';
    lookupSection.innerHTML = `
        <div class="dictionary-lookup-card">
            <span class="dictionary-source-badge">✨ Unlimited Dictionary Result</span>
            <div class="dictionary-lookup-header">
                <div>
                    <div class="spotlight-word-row">
                        <span class="vocab-card-word" style="font-size: 1.7rem;">${escapeHtml(entry.word)}</span>
                        <span class="vocab-card-phonetic" style="font-size: 0.98rem;">${escapeHtml(entry.phonetic || '')}</span>
                        <span class="badge-tag pos">${escapeHtml(entry.part_of_speech || 'Word')}</span>
                        <span class="badge-tag diff-${escapeHtml(entry.difficulty || 'Intermediate')}">${escapeHtml(entry.difficulty || 'Intermediate')}</span>
                    </div>
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button type="button" id="lookupListenBtn" class="btn-secondary" style="padding: 8px 14px; font-size:0.85rem;">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>
                        <span>Pronounce</span>
                    </button>
                    <button type="button" id="lookupSaveBtn" data-id="${entry.id}" class="btn-secondary" style="padding: 8px 14px; font-size:0.85rem;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="${isSaved ? '#F59E0B' : 'none'}" stroke="${isSaved ? '#F59E0B' : 'currentColor'}" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
                        <span>${isSaved ? 'Saved in My List ★' : 'Save to My List'}</span>
                    </button>
                </div>
            </div>
            <p class="vocab-card-def" style="font-size: 1rem; margin-bottom: 12px;">${escapeHtml(entry.definition)}</p>
            ${synsHtml}
            ${entry.example ? `<div class="vocab-card-example" style="margin-bottom: 12px;">"${escapeHtml(entry.example)}"</div>` : ''}
            ${entry.tip ? `<div class="vocab-card-tip"><span>💡</span><span>${escapeHtml(entry.tip)}</span></div>` : ''}
        </div>
    `;

    const listenBtn = document.getElementById('lookupListenBtn');
    if (listenBtn) listenBtn.onclick = () => playWordAudio(entry.word);

    const saveBtn = document.getElementById('lookupSaveBtn');
    if (saveBtn) saveBtn.onclick = () => toggleSaveWord(entry.id, saveBtn, entry.word, entry);
}

function renderLookupError(message) {
    const lookupSection = document.getElementById('dictionaryLookupSection');
    if (!lookupSection) return;
    lookupSection.style.display = 'block';
    lookupSection.innerHTML = `
        <div class="dictionary-lookup-card" style="border-color: var(--border-color);">
            <p style="margin:0; color: var(--text-muted); font-weight: 500;">${escapeHtml(message)}</p>
        </div>
    `;
}

function ensureCardInGrid(entry) {
    const grid = document.getElementById('vocabGrid');
    if (!grid || document.querySelector(`.vocab-card[data-id="${entry.id}"]`)) return;

    const card = document.createElement('div');
    card.className = 'vocab-card';
    card.setAttribute('data-id', entry.id);
    card.setAttribute('data-category', entry.category || 'Dictionary');
    card.setAttribute('data-word', entry.word);
    card.setAttribute('data-def', entry.definition);

    card.innerHTML = `
        <div>
            <div class="vocab-card-header">
                <div>
                    <div class="vocab-card-word">${escapeHtml(entry.word)}</div>
                    <div class="vocab-card-phonetic">${escapeHtml(entry.phonetic || '')}</div>
                </div>
                <div class="vocab-card-badges">
                    <span class="badge-tag pos">${escapeHtml(entry.part_of_speech || 'Word')}</span>
                    <span class="badge-tag diff-${escapeHtml(entry.difficulty || 'Intermediate')}">${escapeHtml(entry.difficulty || 'Intermediate')}</span>
                </div>
            </div>
            <p class="vocab-card-def">${escapeHtml(entry.definition)}</p>
            <div class="vocab-card-example">"${escapeHtml(entry.example || '')}"</div>
            <div class="vocab-card-tip"><span>💡</span><span>${escapeHtml(entry.tip || '')}</span></div>
        </div>
        <div class="vocab-card-footer">
            <button type="button" class="btn-card-audio" onclick="playWordFromCard(this)">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>
                <span>Pronounce</span>
            </button>
            <button type="button" class="btn-bookmark active" data-id="${entry.id}" onclick="toggleCardBookmark(this)" title="Bookmark word">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="#F59E0B" stroke="#F59E0B" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
            </button>
        </div>
    `;
    grid.prepend(card);
}

function applyFilters() {
    const searchInput = document.getElementById('vocabSearchInput');
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const cards = document.querySelectorAll('.vocab-card');
    const emptyState = document.getElementById('vocabEmptyState');
    const emptyHint = document.getElementById('vocabEmptyHint');
    const savedIds = getSavedWordIds();

    let visibleCount = 0;

    cards.forEach(card => {
        const wordText = (card.getAttribute('data-word') || '').toLowerCase();
        const defText = (card.getAttribute('data-def') || '').toLowerCase();
        const catText = card.getAttribute('data-category') || '';
        const id = parseInt(card.getAttribute('data-id'), 10);

        let categoryMatch = false;
        if (currentCategory === 'all') {
            categoryMatch = true;
        } else if (currentCategory === 'saved') {
            categoryMatch = savedIds.includes(id);
        } else {
            categoryMatch = (catText === currentCategory);
        }

        let searchMatch = false;
        if (!query) {
            searchMatch = true;
        } else if (wordText.includes(query) || defText.includes(query) || catText.toLowerCase().includes(query)) {
            searchMatch = true;
        }

        if (categoryMatch && searchMatch) {
            card.style.display = 'flex';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    if (emptyState) {
        const hasLookupVisible = document.getElementById('dictionaryLookupSection')?.style.display === 'block';
        emptyState.style.display = (visibleCount === 0 && !hasLookupVisible) ? 'block' : 'none';
        if (emptyHint && query) {
            emptyHint.innerHTML = `Looking up "<strong>${escapeHtml(query)}</strong>" in the full English dictionary, or click <strong>Look Up</strong>.`;
        } else if (emptyHint) {
            emptyHint.textContent = 'Try searching for a different keyword or choose another category filter.';
        }
    }
}
