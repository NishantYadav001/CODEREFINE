import { get, showToast, setClick, setChange } from './utils.js';

// Global error handler for debugging
window.onerror = function(msg, url, line, col, error) {
    console.error("❌ Global Error:", msg, "\nLine:", line, "\nError:", error);
    return false;
};

// Initialize application when DOM is ready
const initApp = () => {
    // Prevent double initialization
    if (window.appInitialized) return;
    window.appInitialized = true;

    // Register Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW registration failed', err));
    }

    // Initialize Mermaid
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });
    }
    
    // Initialize Monaco Editor
    require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }});
    require(['vs/editor/editor.main'], function() {
        const savedCode = localStorage.getItem('codeRefine_content') || "# Paste your code here or drag & drop a file\n# Press Ctrl+Enter to Review\n\ndef hello_world():\n    print('Hello Code Refine!')";
        const savedSettings = JSON.parse(localStorage.getItem('editorSettings')) || { fontSize: 14, minimap: false, wordWrap: 'off', lineNumbers: 'on' };

        window.monacoEditor = monaco.editor.create(document.getElementById('monaco-container'), {
            value: savedCode,
            language: "python",
            theme: "vs-dark",
            automaticLayout: true,
            minimap: { enabled: savedSettings.minimap },
            fontSize: savedSettings.fontSize,
            wordWrap: savedSettings.wordWrap,
            lineNumbers: savedSettings.lineNumbers,
            fontFamily: "'Fira Code', monospace",
            scrollBeyondLastLine: false,
            padding: { top: 16, bottom: 16 }
        });

        // Event Listeners for Editor
        window.monacoEditor.onDidChangeCursorPosition((e) => {
            const status = document.getElementById('cursorStatus');
            if(status) status.innerText = `Ln ${e.position.lineNumber}, Col ${e.position.column}`;
        });

        window.monacoEditor.onDidChangeModelContent(() => {
            localStorage.setItem('codeRefine_content', window.monacoEditor.getValue());
        });
        
        // Sync Language Selector
        const langSelect = document.getElementById('editorLang');
        if(langSelect) {
            langSelect.value = 'python'; // Default
            langSelect.onchange = () => monaco.editor.setModelLanguage(window.monacoEditor.getModel(), langSelect.value);
        }

        // Initialize Settings UI
        const fsInput = get('settingFontSize');
        if(fsInput) fsInput.value = savedSettings.fontSize;
        const mmInput = get('settingMinimap');
        if(mmInput) mmInput.checked = savedSettings.minimap;
    });

    // Fetch Piston Runtimes
    fetch('https://emkc.org/api/v2/piston/runtimes').then(r => r.json()).then(data => window.pistonRuntimes = data);

    console.log("🚀 Code Refine: Initializing...");

    try {
        // --- 1. CONFIGURATION & STATE ---
        const params = new URLSearchParams(window.location.search);
        const userType = params.get('userType') || 'developer';
        const studentName = params.get('email') || params.get('username') || 'Guest';

        // Security Check
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (!token && studentName !== 'Guest') {
            window.location.href = '/login';
            return;
        }

        const modes = {
            'student': { title: 'AI DEBUGGER', sub: 'STUDENT Edition', badge: 'Student' },
            'enterprise': { title: 'Security Shield', sub: 'Enterprise Edition', badge: 'Admin' },
            'organisation': { title: 'Team Reviewer', sub: 'Organisation Edition', badge: 'Team' },
            'developer': { title: 'Code Refine', sub: 'Developer Edition', badge: 'Pro' }
        };

        // --- 2. UI SETUP ---
        const config = modes[userType] || modes.developer;
        if (get('platform-subtitle')) get('platform-subtitle').innerText = config.sub;
        if (get('user-badge')) get('user-badge').innerText = config.badge;

        if (userType === 'student') {
            if (get('student-tracking')) get('student-tracking').classList.remove('hidden');
            if (get('plagiarism-badge')) get('plagiarism-badge').classList.remove('hidden');
        }
        if ((userType === 'enterprise' || userType === 'organisation') && get('policy-upload-zone')) {
            get('policy-upload-zone').classList.remove('hidden');
        }

        // --- 3. CORE FUNCTIONS ---

        // Process Code (Review or Rewrite)
        async function processCode(action) {
            // Get code from Monaco
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const code = window.monacoEditor ? window.monacoEditor.getValue() : "";
            
            if (!code.trim()) {
                showToast("Please paste some code first!", "warning");
                return;
            }

            const focusAreas = Array.from(document.querySelectorAll('input[name="focusArea"]:checked')).map(cb => cb.value);
            
            // Auto-detect language
            let language = 'python';
            if (typeof hljs !== 'undefined') {
                try {
                    const detected = hljs.highlightAuto(code);
                    language = detected.language || 'python';
                } catch (e) { console.warn("HighlightJS error", e); }
            }
            
            // Map common aliases
            const aliasMap = { 'js': 'javascript', 'ts': 'typescript', 'c++': 'cpp', 'cs': 'csharp', 'py': 'python' };
            language = aliasMap[language] || language;

            const langDisplay = get('detectedLangDisplay');
            if (langDisplay) { 
                langDisplay.textContent = `(Detected: ${language})`; 
                langDisplay.classList.remove('hidden'); 
            }
            
            // UI Updates for Processing State
            const originalSection = get('originalCodeSection');
            const codeDisplaySection = get('codeDisplaySection');
            const generatedSection = get('generatedCodeSection');
            const originalOutput = get('originalCodeOutput');
            const feedback = get('reviewFeedback');
            
            if (originalSection) originalSection.style.display = 'block';
            if (codeDisplaySection) {
                codeDisplaySection.classList.remove('lg:grid-cols-1');
                codeDisplaySection.classList.add('lg:grid-cols-2');
                codeDisplaySection.classList.remove('hidden');
            }
            if (generatedSection) {
                const h3 = generatedSection.querySelector('h3');
                if (h3) h3.innerHTML = '<i class="fas fa-wand-magic-sparkles text-emerald-400 mr-2"></i>AI Rewritten Version';
            }
            
            if (originalOutput) {
                originalOutput.textContent = code;
                if (typeof hljs !== 'undefined') hljs.highlightElement(originalOutput);
            }

            if (feedback) {
                feedback.innerHTML = `
                    <div class="space-y-4 p-2">
                        <div class="flex items-center gap-2 text-sky-400 mb-4"><i class="fas fa-spinner fa-spin"></i> <span class="text-sm font-bold">AI is analyzing your code...</span></div>
                        <div class="skeleton h-8 w-3/4"></div>
                        <div class="skeleton h-4 w-full"></div>
                        <div class="skeleton h-4 w-5/6"></div>
                        <div class="skeleton h-32 w-full"></div>
                        <div class="grid grid-cols-2 gap-4"><div class="skeleton h-20"></div><div class="skeleton h-20"></div></div>
                    </div>`;
            }

            try {
                const endpoint = action === 'review' ? 'review' : 'rewrite';
                const model = get('globalModelSelector') ? get('globalModelSelector').value : 'llama-3.3-70b';
                const response = await fetch(`/api/${endpoint}`, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        code: code,
                        language: language,
                        user_type: userType,
                        student_name: studentName,
                        focus_areas: focusAreas,
                        model: model
                    })
                });

                if (!response.ok) throw new Error("Server Error: " + response.status);
                const data = await response.json();

                // Update Stats
                if (get('critical-count')) get('critical-count').innerText = data.stats?.critical || 0;
                if (get('high-count')) get('high-count').innerText = data.stats?.high || 0;
                if (get('medium-count')) get('medium-count').innerText = data.stats?.medium || 0;
                if (get('low-count')) get('low-count').innerText = data.stats?.low || 0;

                if (userType === 'student') {
                    if (get('plag-score')) get('plag-score').innerText = data.plagiarism || "0%";
                    if (get('review-count')) get('review-count').innerText = data.student_stats || 0;
                }

                if (feedback) feedback.innerHTML = typeof marked !== 'undefined' ? marked.parse(data.review) : data.review;
                
                if (action === 'fix') {
                    const rwOut = get('rewrittenCodeOutput');
                    if (rwOut) {
                        rwOut.textContent = data.rewritten_code;
                        if (typeof hljs !== 'undefined') hljs.highlightElement(rwOut);
                    }
                    
                    if (get('complexity-section')) get('complexity-section').classList.remove('hidden');
                    if (get('original-complexity-display')) get('original-complexity-display').innerText = data.time_complexity_original || "O(n)";
                    if (get('rewritten-complexity-display')) get('rewritten-complexity-display').innerText = data.time_complexity_rewritten || "O(n)";
                    
                    if (get('download-section')) get('download-section').classList.remove('hidden');
                    if (get('downloadCodeBtn')) get('downloadCodeBtn').classList.remove('hidden');
                    if (get('toggleDiffBtn')) get('toggleDiffBtn').classList.remove('hidden');

                    // Save data for downloads
                    window.downloadData = {
                        code: data.rewritten_code,
                        review: data.review,
                        language: language,
                        originalCode: code,
                        stats: data.stats,
                        complexity_original: data.time_complexity_original || "O(n)",
                        complexity_rewritten: data.time_complexity_rewritten || "O(n)"
                    };
                }
                if (typeof hljs !== 'undefined') hljs.highlightAll();
                showToast(`✅ ${action === 'review' ? 'Review' : 'Rewrite'} Complete`, 'success');

            } catch (err) {
                if (feedback) feedback.innerHTML = `<p class="text-red-400">Error: ${err.message}</p>`;
                showToast("Operation failed: " + err.message, "error");
            }
        }

        // --- NEW FEATURES: RUN & VISUALIZE ---

        async function runCode() {
            const code = window.monacoEditor ? window.monacoEditor.getValue() : "";
            if (!code.trim()) return showToast("No code to run!", "warning");

            const terminalContainer = get('terminalContainer');
            const terminalOutput = get('terminalOutput');
            const toolsSection = get('toolsOutputSection');
            
            if(toolsSection) toolsSection.classList.remove('hidden');
            if(terminalContainer) terminalContainer.classList.remove('hidden');
            if(get('visualizerContainer')) get('visualizerContainer').classList.add('hidden');
            
            // Scroll to output
            setTimeout(() => terminalContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);

            terminalOutput.innerHTML = '<span class="animate-pulse text-yellow-400">⏳ Compiling and executing...</span>';

            let lang = 'python';
            if (window.monacoEditor) {
                const modelLang = window.monacoEditor.getModel().getLanguageId();
                const monacoToPiston = {
                    'python': 'python', 'javascript': 'javascript', 'typescript': 'typescript',
                    'java': 'java', 'cpp': 'c++', 'c': 'c', 'csharp': 'csharp',
                    'go': 'go', 'rust': 'rust', 'php': 'php', 'ruby': 'ruby'
                };
                lang = monacoToPiston[modelLang] || modelLang;
            }

            const runtime = window.pistonRuntimes ? window.pistonRuntimes.find(r => r.language === lang) : null;
            const version = runtime ? runtime.version : "*";
            
            const escapeHtml = (text) => text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");

            try {
                const res = await fetch('https://emkc.org/api/v2/piston/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        language: lang,
                        version: version,
                        files: [{ content: code }]
                    })
                });
                const data = await res.json();
                
                if (data.run) {
                    let output = data.run.stdout || "";
                    let error = data.run.stderr || "";
                    terminalOutput.innerHTML = "";
                    if (output) terminalOutput.innerHTML += `<span class="text-emerald-300">${escapeHtml(output)}</span>`;
                    if (error) terminalOutput.innerHTML += `<span class="text-red-400">\n${escapeHtml(error)}</span>`;
                    if (!output && !error) terminalOutput.innerHTML = `<span class="text-slate-500 italic">Program executed successfully with no output.</span>`;
                } else {
                    terminalOutput.innerHTML = `<span class="text-red-400">Execution failed: ${data.message || "Unknown error"}</span>`;
                }
            } catch (e) {
                terminalOutput.innerHTML = `<span class="text-red-400">API Error: ${e.message}</span>`;
            }
        }

        async function formatCode() {
            if (!window.monacoEditor) return;
            const code = window.monacoEditor.getValue();
            const lang = window.monacoEditor.getModel().getLanguageId();

            try {
                let parser = null;
                if (lang === 'javascript' || lang === 'typescript') parser = 'babel';
                else if (lang === 'html') parser = 'html';
                else if (lang === 'css') parser = 'css';
                else if (lang === 'json') parser = 'json';
                else if (lang === 'markdown') parser = 'markdown';
                else if (lang === 'yaml') parser = 'yaml';

                if (parser && window.prettier && window.prettierPlugins) {
                    const formatted = await window.prettier.format(code, {
                        parser: parser,
                        plugins: window.prettierPlugins
                    });
                    window.monacoEditor.setValue(formatted);
                    showToast("Code formatted with Prettier!", "success");
                } else {
                    await window.monacoEditor.getAction('editor.action.formatDocument').run();
                    showToast("Triggered editor formatter", "info");
                }
            } catch (e) {
                showToast("Formatting error: " + e.message, "error");
            }
        }

        async function minifyCode() {
            if (!window.monacoEditor) return;
            const code = window.monacoEditor.getValue();
            if (!code.trim()) return showToast("No code to minify!", "warning");
            
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;
            
            showToast("Minifying code...", "info");

            try {
                const model = get('globalModelSelector') ? get('globalModelSelector').value : 'llama-3.3-70b';
                const lang = window.monacoEditor.getModel().getLanguageId();
                
                const response = await fetch(`/api/generate`, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        prompt: `Minify the following ${lang} code. Remove all unnecessary whitespace, newlines, and comments to make it as compact as possible while preserving functionality. Return ONLY the minified code. Do not use markdown blocks.\n\nCode:\n${code}`,
                        language: lang,
                        user_type: "developer",
                        model: model
                    })
                });

                if (!response.ok) throw new Error("Minification failed");
                const data = await response.json();
                let minified = data.generated_code || "";
                
                minified = minified.replace(/^```[a-z]*\n?/i, '').replace(/```$/, '').trim();
                
                if(minified) {
                    window.monacoEditor.setValue(minified);
                    showToast("Code minified successfully!", "success");
                } else {
                    showToast("AI returned empty code", "error");
                }
            } catch (e) {
                showToast("Error: " + e.message, "error");
            }
        }

        async function visualizeCode() {
            const code = window.monacoEditor ? window.monacoEditor.getValue() : "";
            if (!code.trim()) return showToast("No code to visualize!", "warning");

            const vizContainer = get('visualizerContainer');
            const mermaidOutput = get('mermaidOutput');
            const toolsSection = get('toolsOutputSection');

            if(toolsSection) toolsSection.classList.remove('hidden');
            if(vizContainer) vizContainer.classList.remove('hidden');
            if(get('terminalContainer')) get('terminalContainer').classList.add('hidden');

            mermaidOutput.innerHTML = '<div class="animate-pulse text-purple-400"><i class="fas fa-brain fa-spin mr-2"></i>Analyzing logic flow...</div>';
            
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            try {
                const prompt = "Generate a Mermaid.js flowchart (graph TD) representing the logic of this code. Return ONLY the mermaid code inside a markdown block (```mermaid ... ```). Do not explain.";
                const model = get('globalModelSelector') ? get('globalModelSelector').value : 'llama-3.3-70b';
                
                const response = await fetch(`/api/generate`, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        prompt: `${prompt}\n\nCode:\n${code}`,
                        language: "mermaid",
                        user_type: "developer",
                        model: model
                    })
                });
                
                const data = await response.json();
                let mermaidCode = data.generated_code || "";
                
                mermaidCode = mermaidCode.replace(/```mermaid/g, '').replace(/```/g, '').trim();

                mermaidOutput.innerHTML = '';
                const { svg } = await mermaid.render('graphDiv', mermaidCode);
                mermaidOutput.innerHTML = svg;
                
            } catch (e) {
                mermaidOutput.innerHTML = `<p class="text-red-400">Visualization failed: ${e.message}</p>`;
            }
        }

        // --- CHAT FEATURE ---
        const setupChat = () => {
            const tabResults = get('tabResults');
            const tabChat = get('tabChat');
            const reviewResults = get('reviewResults');
            const chatInterface = get('chatInterface');
            const chatInput = get('chatInput');
            const sendChatBtn = get('sendChatBtn');
            const chatHistory = get('chatHistory');
            const clearChatBtn = get('clearChatBtn');

            if(tabResults && tabChat) {
                tabResults.onclick = () => {
                    reviewResults.classList.remove('hidden');
                    chatInterface.classList.add('hidden');
                    tabResults.classList.add('bg-slate-600', 'text-white', 'shadow-sm');
                    tabResults.classList.remove('text-slate-400', 'hover:bg-slate-700/50');
                    tabChat.classList.remove('bg-slate-600', 'text-white', 'shadow-sm');
                    tabChat.classList.add('text-slate-400', 'hover:bg-slate-700/50');
                };
                tabChat.onclick = () => {
                    reviewResults.classList.add('hidden');
                    chatInterface.classList.remove('hidden');
                    tabChat.classList.add('bg-slate-600', 'text-white', 'shadow-sm');
                    tabChat.classList.remove('text-slate-400', 'hover:bg-slate-700/50');
                    tabResults.classList.remove('bg-slate-600', 'text-white', 'shadow-sm');
                    tabResults.classList.add('text-slate-400', 'hover:bg-slate-700/50');
                };
            }

            const sendMsg = async () => {
                const msg = chatInput.value.trim();
                if(!msg) return;

                chatHistory.innerHTML += `
                    <div class="flex gap-3 flex-row-reverse">
                        <div class="w-8 h-8 rounded-full bg-sky-600 flex items-center justify-center flex-shrink-0"><i class="fas fa-user text-white text-xs"></i></div>
                        <div class="bg-sky-900/30 p-3 rounded-2xl rounded-tr-none text-sm text-sky-100 border border-sky-700/50">${msg}</div>
                    </div>`;
                chatInput.value = '';
                chatHistory.scrollTop = chatHistory.scrollHeight;

                const loadingId = 'loading-' + Date.now();
                chatHistory.innerHTML += `
                    <div id="${loadingId}" class="flex gap-3">
                        <div class="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0"><i class="fas fa-robot text-white text-xs"></i></div>
                        <div class="bg-slate-700/50 p-3 rounded-2xl rounded-tl-none text-sm text-slate-400 border border-slate-600 animate-pulse">Thinking...</div>
                    </div>`;
                chatHistory.scrollTop = chatHistory.scrollHeight;

                try {
                    const code = window.monacoEditor ? window.monacoEditor.getValue() : "";
                    const model = get('globalModelSelector') ? get('globalModelSelector').value : 'llama-3.3-70b';
                    
                    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
                    const headers = { 'Content-Type': 'application/json' };
                    if (token) headers['Authorization'] = `Bearer ${token}`;
                    
                    const res = await fetch('/api/generate', {
                        method: 'POST',
                        headers: headers,
                        body: JSON.stringify({
                            prompt: `Context Code:\n${code}\n\nUser Question: ${msg}\n\nAnswer the question based on the code context. Keep it concise.`,
                            language: "markdown",
                            user_type: "developer",
                            model: model
                        })
                    });
                    const data = await res.json();
                    const aiMsg = data.generated_code || "I couldn't generate a response.";
                    
                    document.getElementById(loadingId).remove();
                    chatHistory.innerHTML += `
                        <div class="flex gap-3">
                            <div class="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0"><i class="fas fa-robot text-white text-xs"></i></div>
                            <div class="bg-slate-700/50 p-3 rounded-2xl rounded-tl-none text-sm text-slate-300 border border-slate-600 prose prose-invert prose-sm max-w-none">
                                ${typeof marked !== 'undefined' ? marked.parse(aiMsg) : aiMsg}
                            </div>
                        </div>`;
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                } catch(e) {
                    document.getElementById(loadingId).innerHTML = `<div class="text-red-400">Error: ${e.message}</div>`;
                }
            };

            if(clearChatBtn) {
                clearChatBtn.onclick = () => {
                    chatHistory.innerHTML = `
                        <div class="flex gap-3">
                            <div class="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0"><i class="fas fa-robot text-white text-xs"></i></div>
                            <div class="bg-slate-700/50 p-3 rounded-2xl rounded-tl-none text-sm text-slate-300 border border-slate-600">
                                Hello! I'm ready to answer questions about your code.
                            </div>
                        </div>`;
                    showToast('Chat history cleared', 'info');
                };
            }

            if(sendChatBtn) sendChatBtn.onclick = sendMsg;
            if(chatInput) chatInput.onkeypress = (e) => { if(e.key === 'Enter') sendMsg(); };
        };
        setupChat();

        // --- 4. EVENT LISTENERS ---

        // OCR
        setChange('ocrFile', async (e) => {
            if (!e.target.files[0]) return;
            if (!window.monacoEditor) return;

            const originalValue = window.monacoEditor.getValue();
            window.monacoEditor.setValue("# ⏳ Scanning image... please wait...");
            
            const modeAnalysis = get('modeAnalysis');
            if (modeAnalysis) modeAnalysis.click();

            try {
                if (typeof Tesseract !== 'undefined') {
                    const worker = await Tesseract.createWorker('eng');
                    const ret = await worker.recognize(e.target.files[0]);
                    await worker.terminate();
                    
                    if (ret.data.text) {
                        window.monacoEditor.setValue(ret.data.text);
                        showToast('✅ OCR Complete (Client-side)', 'success');
                        return;
                    }
                }
                throw new Error("Client OCR skipped or failed");

            } catch (err) { 
                const formData = new FormData();
                formData.append('file', e.target.files[0]);
                try {
                    const res = await fetch('/api/ocr', { method: 'POST', body: formData });
                    if (!res.ok) throw new Error("Backend OCR Failed");
                    const data = await res.json();
                    window.monacoEditor.setValue(data.extracted_code || "// No code detected");
                    showToast('✅ OCR Complete (Server-side)', 'success');
                } catch (serverErr) {
                    alert("OCR Failed: " + serverErr.message);
                    window.monacoEditor.setValue(originalValue);
                }
            } finally {
                e.target.value = ''; 
            }
        });

        // GitHub Loader
        setClick('loadGithubBtn', async () => {
            const urlInput = get('githubUrl');
            if (!urlInput || !urlInput.value) return showToast("Please enter a URL", "warning");
            
            let url = urlInput.value.trim();
            if (url.includes('github.com') && url.includes('/blob/')) {
                url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/');
            }

            try {
                showToast("Fetching code...", "info");
                const res = await fetch(url);
                if (!res.ok) throw new Error("Failed to fetch");
                const text = await res.text();
                if (window.monacoEditor) window.monacoEditor.setValue(text);
                showToast("Code loaded from URL", "success");
                urlInput.value = ""; 
            } catch (e) {
                showToast("Error loading URL: " + e.message, "error");
            }
        });

        // Policy Upload
        setChange('policyFile', async (e) => {
            if (!e.target.files[0]) return;
            const formData = new FormData();
            formData.append('file', e.target.files[0]);
            try {
                const res = await fetch('/api/upload-policy', { method: 'POST', body: formData });
                const data = await res.json();
                showToast(data.message, 'success');
            } catch (err) { showToast("Upload failed", "error"); }
        });

        // Buttons
        setClick('reviewBtn', () => processCode('review'));
        setClick('fixBtn', () => processCode('fix'));
        setClick('runCodeBtn', runCode);
        setClick('visualizeBtn', visualizeCode);
        setClick('formatBtn', formatCode);
        setClick('minifyBtn', minifyCode);
        
        setClick('wordWrapBtn', () => {
            if(!window.monacoEditor) return;
            const current = window.monacoEditor.getOption(monaco.editor.EditorOption.wordWrap);
            const newState = current === 'off' ? 'on' : 'off';
            window.monacoEditor.updateOptions({ wordWrap: newState });
            showToast(`Word Wrap: ${newState.toUpperCase()}`, 'info');
        });

        setClick('clearEditorBtn', () => {
            if(window.monacoEditor && confirm("Clear editor content?")) window.monacoEditor.setValue('');
        });
        
        setClick('fullscreenBtn', () => {
            const wrapper = document.getElementById('editorWrapper');
            const container = document.getElementById('monaco-container');
            
            if (!document.fullscreenElement) {
                wrapper.requestFullscreen().catch(err => {
                    showToast(`Error enabling fullscreen: ${err.message}`, 'error');
                });
                container.style.height = '100vh';
            } else {
                document.exitFullscreen();
                container.style.height = '400px';
            }
        });

        document.addEventListener('fullscreenchange', () => {
            const container = document.getElementById('monaco-container');
            if (!document.fullscreenElement) {
                container.style.height = '400px';
            } else {
                container.style.height = 'calc(100vh - 80px)';
            }
            if (window.monacoEditor) window.monacoEditor.layout();
        });

        // Shortcuts Modal
        const modal = get('shortcutsModal');
        setClick('shortcuts-btn', () => modal.classList.remove('hidden'));
        setClick('closeShortcutsBtn', () => modal.classList.add('hidden'));

        // Settings Modal
        const settingsModal = get('settingsModal');
        setClick('settings-btn', () => settingsModal.classList.remove('hidden'));
        setClick('closeSettingsBtn', () => settingsModal.classList.add('hidden'));

        const updateSettings = () => {
            if(!window.monacoEditor) return;
            const fontSize = parseInt(get('settingFontSize').value);
            const minimap = get('settingMinimap').checked;
            const wordWrap = get('settingWordWrap').checked ? 'on' : 'off';
            const lineNumbers = get('settingLineNumbers').checked ? 'on' : 'off';

            get('fontSizeVal').innerText = fontSize + 'px';
            
            window.monacoEditor.updateOptions({
                fontSize: fontSize,
                minimap: { enabled: minimap },
                wordWrap: wordWrap,
                lineNumbers: lineNumbers
            });

            localStorage.setItem('editorSettings', JSON.stringify({ fontSize, minimap, wordWrap, lineNumbers }));
        };

        ['settingFontSize', 'settingMinimap', 'settingWordWrap', 'settingLineNumbers'].forEach(id => {
            const el = get(id);
            if(el) el.addEventListener(el.type === 'checkbox' ? 'change' : 'input', updateSettings);
        });

        // Command Palette
        const cmdPalette = get('commandPalette');
        const cmdInput = get('cmdInput');
        const cmdList = get('cmdList');

        const commands = [
            { label: 'Run Review', icon: 'microscope', action: () => get('reviewBtn').click() },
            { label: 'Generate Code', icon: 'wand-magic-sparkles', action: () => window.location.href = '/generate' },
            { label: 'Format Code', icon: 'align-left', action: () => formatCode() },
            { label: 'Minify Code', icon: 'compress-arrows-alt', action: () => minifyCode() },
            { label: 'Run Code', icon: 'play', action: () => runCode() },
            { label: 'Visualize Logic', icon: 'project-diagram', action: () => visualizeCode() },
            { label: 'Toggle Fullscreen', icon: 'expand', action: () => get('fullscreenBtn').click() },
            { label: 'Clear Editor', icon: 'trash', action: () => get('clearEditorBtn').click() },
            { label: 'Open Settings', icon: 'cog', action: () => get('settings-btn').click() }
        ];

        const renderCommands = (filter = '') => {
            cmdList.innerHTML = '';
            const filtered = commands.filter(c => c.label.toLowerCase().includes(filter.toLowerCase()));
            filtered.forEach((cmd, idx) => {
                const div = document.createElement('div');
                div.className = `p-2 hover:bg-slate-700 rounded cursor-pointer flex items-center gap-3 text-sm text-slate-300 ${idx === 0 ? 'bg-slate-700' : ''}`;
                div.innerHTML = `<i class="fas fa-${cmd.icon} w-5 text-center"></i> ${cmd.label}`;
                div.onclick = () => {
                    cmd.action();
                    cmdPalette.classList.add('hidden');
                };
                cmdList.appendChild(div);
            });
        };

        cmdInput.addEventListener('input', (e) => renderCommands(e.target.value));

        // Mobile Tabs
        const leftPanel = get('left-panel');
        const rightPanel = get('right-panel');
        const mTabEditor = get('mobile-tab-editor');
        const mTabOutput = get('mobile-tab-output');
        const mTabChat = get('mobile-tab-chat');

        const setMobileView = (view) => {
            [mTabEditor, mTabOutput, mTabChat].forEach(t => {
                t.className = "flex-1 py-2 text-xs font-bold rounded-lg text-slate-400 hover:text-white transition-all";
            });

            if(view === 'editor') {
                leftPanel.classList.remove('mobile-hidden');
                rightPanel.classList.add('mobile-hidden');
                mTabEditor.className = "flex-1 py-2 text-xs font-bold rounded-lg bg-sky-600 text-white shadow-sm transition-all";
            } else {
                leftPanel.classList.add('mobile-hidden');
                rightPanel.classList.remove('mobile-hidden');
                if(view === 'output') {
                    get('tabResults').click();
                    mTabOutput.className = "flex-1 py-2 text-xs font-bold rounded-lg bg-sky-600 text-white shadow-sm transition-all";
                } else {
                    get('tabChat').click();
                    mTabChat.className = "flex-1 py-2 text-xs font-bold rounded-lg bg-sky-600 text-white shadow-sm transition-all";
                }
            }
        };

        if(mTabEditor) {
            mTabEditor.onclick = () => setMobileView('editor');
            mTabOutput.onclick = () => setMobileView('output');
            mTabChat.onclick = () => setMobileView('chat');
        }

        // File Open
        setChange('localFile', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            try {
                const text = await file.text();
                if (window.monacoEditor) {
                    window.monacoEditor.setValue(text);
                    const ext = file.name.split('.').pop();
                    const langMap = {'js':'javascript', 'py':'python', 'html':'html', 'css':'css', 'json':'json', 'md':'markdown', 'ts':'typescript', 'java':'java', 'cpp':'cpp', 'c':'c', 'cs':'csharp', 'go':'go', 'rs':'rust', 'sql':'sql'};
                    if(langMap[ext]) monaco.editor.setModelLanguage(window.monacoEditor.getModel(), langMap[ext]);
                }
                showToast(`📂 Opened: ${file.name}`, 'success');
            } catch (err) {
                showToast("Failed to read file", "error");
            }
            e.target.value = '';
        });

        // Downloads
        const triggerDownload = (blob, filename) => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = filename;
            document.body.appendChild(a); a.click();
            window.URL.revokeObjectURL(url); a.remove();
        };

        setClick('downloadCodeBtn', () => {
            if (!window.downloadData) return showToast('Run Auto-Rewrite first', 'warning');
            const extMap = { 'python': 'py', 'java': 'java', 'javascript': 'js', 'cpp': 'cpp' };
            const ext = extMap[window.downloadData.language] || 'txt';
            const blob = new Blob([window.downloadData.code], { type: 'text/plain' });
            triggerDownload(blob, `refactored_code.${ext}`);
        });

        setClick('downloadCodeFileBtn', () => {
            if (!window.downloadData) return showToast('Run Auto-Rewrite first', 'warning');
            const extMap = { 'python': 'py', 'java': 'java', 'javascript': 'js', 'cpp': 'cpp' };
            const ext = extMap[window.downloadData.language] || 'txt';
            const blob = new Blob([window.downloadData.code], { type: 'text/plain' });
            triggerDownload(blob, `refactored_code.${ext}`);
        });

        setClick('downloadSummaryBtn', async () => {
            if (!window.downloadData) return showToast('Run Auto-Rewrite first', 'warning');
            const formatEl = document.querySelector('input[name="downloadFormat"]:checked');
            const format = formatEl ? formatEl.value : 'docx';
            
            try {
                const res = await fetch('/api/download/summary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ format, review: window.downloadData.review, stats: window.downloadData.stats })
                });
                if (res.ok) triggerDownload(await res.blob(), `summary.${format}`);
                else throw new Error("Download failed");
            } catch (e) { showToast("Download failed", "error"); }
        });

        setClick('downloadReportBtn', async () => {
            if (!window.downloadData) return showToast('Run Auto-Rewrite first', 'warning');
            const formatEl = document.querySelector('input[name="downloadFormat"]:checked');
            const format = formatEl ? formatEl.value : 'docx';
            
            try {
                const res = await fetch('/api/download/report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        format, ...window.downloadData,
                        original_code: window.downloadData.originalCode,
                        rewritten_code: window.downloadData.code
                    })
                });
                if (res.ok) triggerDownload(await res.blob(), `report.${format}`);
                else throw new Error("Download failed");
            } catch (e) { showToast("Download failed", "error"); }
        });
        
        // Mode Switching
        const btnAnalysis = document.getElementById('modeAnalysis');
        const btnGenerate = document.getElementById('modeGenerate');
        
        const setActive = (btn) => {
            [btnAnalysis, btnGenerate].forEach(b => {
                if (b) {
                    b.classList.remove('active', 'bg-sky-600', 'border-sky-600', 'bg-emerald-600', 'border-emerald-600', 'text-white');
                    b.classList.add('bg-slate-700', 'border-slate-700', 'text-slate-300');
                    b.classList.remove('hidden');
                }
            });
            if (btn) {
                btn.classList.remove('bg-slate-700', 'border-slate-700', 'text-slate-300');
                btn.classList.add('active', 'text-white');
                if (btn === btnAnalysis) btn.classList.add('bg-sky-600', 'border-sky-600');
                if (btn === btnGenerate) btn.classList.add('bg-emerald-600', 'border-emerald-600');
            }
        };

        if (btnAnalysis) {
            btnAnalysis.addEventListener('click', (e) => {
                if(e) e.preventDefault();
                setActive(btnAnalysis);
            });
        }

        if (btnGenerate) {
            btnGenerate.addEventListener('click', (e) => {
                if(e) e.preventDefault();
                window.location.href = '/generate';
            });
        }

        // Advanced Features
        setClick('generateTestsBtn', async () => {
            if (!window.downloadData) return showToast('Generate or analyze code first', 'warning');
            const feedback = get('reviewFeedback');
            if (feedback) feedback.innerHTML = '<p class="text-blue-400"><i class="fas fa-spinner animate-spin mr-2"></i>Generating tests...</p>';
            try {
                const res = await fetch('/api/generate-tests', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: window.downloadData.code, language: window.downloadData.language, user: studentName })
                });
                const data = await res.json();
                if (feedback) feedback.innerHTML = `<h4 class="text-emerald-400 font-bold mb-2">Unit Tests</h4><pre class="bg-slate-800 p-3 rounded text-sm overflow-auto max-h-96"><code>${data.tests.replace(/</g, '&lt;')}</code></pre>`;
            } catch (e) { showToast("Test generation failed", "error"); }
        });

        setClick('generateDocsBtn', async () => {
            if (!window.downloadData) return showToast('Generate or analyze code first', 'warning');
            const feedback = get('reviewFeedback');
            if (feedback) feedback.innerHTML = '<p class="text-blue-400"><i class="fas fa-spinner animate-spin mr-2"></i>Generating docs...</p>';
            try {
                const res = await fetch('/api/generate-docs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: window.downloadData.code, language: window.downloadData.language, user: studentName })
                });
                const data = await res.json();
                if (feedback) feedback.innerHTML = `<h4 class="text-blue-400 font-bold mb-2">Documentation</h4><div class="bg-slate-800 p-3 rounded max-h-96 overflow-auto">${typeof marked !== 'undefined' ? marked.parse(data.documentation) : data.documentation}</div>`;
            } catch (e) { showToast("Docs generation failed", "error"); }
        });

        setClick('securityScanBtn', async () => {
            if (!window.downloadData) return showToast('Generate or analyze code first', 'warning');
            const feedback = get('reviewFeedback');
            if (feedback) feedback.innerHTML = '<p class="text-yellow-400"><i class="fas fa-spinner animate-spin mr-2"></i>Scanning...</p>';
            try {
                const res = await fetch('/api/security-scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: window.downloadData.code, language: window.downloadData.language, user: studentName })
                });
                const data = await res.json();
                if (feedback) feedback.innerHTML = `<h4 class="text-red-400 font-bold mb-2">Security Analysis</h4><div class="bg-slate-800 p-3 rounded max-h-96 overflow-auto whitespace-pre-wrap text-sm">${data.security_analysis.replace(/</g, '&lt;')}</div>`;
            } catch (e) { showToast("Security scan failed", "error"); }
        });

        setClick('refactorSuggestionsBtn', async () => {
            if (!window.downloadData) return showToast('Generate or analyze code first', 'warning');
            const feedback = get('reviewFeedback');
            if (feedback) feedback.innerHTML = '<p class="text-purple-400"><i class="fas fa-spinner animate-spin mr-2"></i>Analyzing...</p>';
            try {
                const res = await fetch('/api/refactor-suggestions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: window.downloadData.code, language: window.downloadData.language, user: studentName })
                });
                const data = await res.json();
                if (feedback) feedback.innerHTML = `<h4 class="text-purple-400 font-bold mb-2">Refactoring Suggestions</h4><div class="bg-slate-800 p-3 rounded max-h-96 overflow-auto">${typeof marked !== 'undefined' ? marked.parse(data.refactoring_suggestions) : data.refactoring_suggestions}</div>`;
            } catch (e) { showToast("Analysis failed", "error"); }
        });

        setClick('saveSnippetBtn', () => {
            if (!window.downloadData) return showToast('Generate or analyze code first', 'warning');
            const title = prompt('Snippet title:', 'My Code Snippet');
            if (!title) return;
            
            fetch('/api/snippets/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: userType, title, code: window.downloadData.code, language: window.downloadData.language })
            }).then(res => res.json()).then(data => {
                showToast(`✅ Snippet saved as #${data.snippet_id}`, 'success');
            }).catch(err => showToast("Save failed", "error"));
        });

        setClick('viewHistoryBtn', async () => {
            const feedback = get('reviewFeedback');
            try {
                const res = await fetch(`/api/history/${userType}`);
                const data = await res.json();
                if (data.history.length === 0) {
                    if (feedback) feedback.innerHTML = '<p class="text-slate-400">No version history yet.</p>';
                    return;
                }
                let html = `<h4 class="text-cyan-400 font-bold mb-2">Code History (${data.total_versions} versions)</h4>`;
                data.history.forEach(v => {
                    html += `<div class="bg-slate-700 p-2 rounded mb-2"><p class="text-sm text-cyan-300">Version ${v.version} - ${v.action} (${new Date(v.timestamp).toLocaleString()})</p></div>`;
                });
                if (feedback) feedback.innerHTML = html;
            } catch (e) { showToast("History fetch failed", "error"); }
        });

        // Diff View
        setClick('toggleDiffBtn', () => {
            const codeSection = get('codeDisplaySection');
            const diffContainer = get('diffViewContainer');
            
            if (diffContainer && diffContainer.classList.contains('hidden')) {
                if (!window.downloadData || !window.downloadData.originalCode) return showToast('No code to diff', 'warning');
                
                if (typeof Diff !== 'undefined' && typeof Diff2HtmlUI !== 'undefined') {
                    const diffStr = Diff.createTwoFilesPatch("Original", "Rewritten", window.downloadData.originalCode, window.downloadData.code);
                    const ui = new Diff2HtmlUI(diffContainer, diffStr, {
                        drawFileList: false,
                        matching: 'lines',
                        outputFormat: 'side-by-side'
                    });
                    
                    if (codeSection) codeSection.classList.add('hidden');
                    diffContainer.classList.remove('hidden');
                    ui.draw();
                } else {
                    showToast("Diff library not loaded", "error");
                }
            } else {
                if (codeSection) codeSection.classList.remove('hidden');
                if (diffContainer) diffContainer.classList.add('hidden');
            }
        });

        // Theme Event Listener
        window.addEventListener('themeChanged', (e) => {
            const isLight = e.detail.theme === 'light';
            if (window.monacoEditor) monaco.editor.setTheme(isLight ? 'vs' : 'vs-dark');
            showToast(`Switched to ${isLight ? 'Light' : 'Dark'} mode`, 'success');
        });

        // Search
        const searchBox = get('search-results');
        if (searchBox) {
            searchBox.oninput = () => {
                const query = searchBox.value.toLowerCase();
                const feedback = get('reviewFeedback');
                if (!feedback) return;
                
                if (!query) {
                    feedback.classList.remove('search-highlight');
                    return;
                }
                
                if (feedback.innerText.toLowerCase().includes(query)) {
                    feedback.classList.add('search-highlight');
                } else {
                    feedback.classList.remove('search-highlight');
                }
            };
        }

        // Drag & Drop
        const setupDragDrop = () => {
            const dropZone = document.getElementById('monaco-container');
            if (!dropZone) return;
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'));
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'));
            });
            
            dropZone.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    const file = files[0];
                    if (file.type.startsWith('text') || file.name.endsWith('.py') || file.name.endsWith('.js') || file.name.endsWith('.java') || file.name.endsWith('.cpp')) {
                        const reader = new FileReader();
                        reader.onload = (event) => {
                            if (window.monacoEditor) window.monacoEditor.setValue(event.target.result);
                            showToast(`✅ File uploaded: ${file.name}`, 'success');
                        };
                        reader.readAsText(file);
                    } else {
                        showToast('❌ Please drop valid code files', 'error');
                    }
                }
            });
        };
        setupDragDrop();

        // Keyboard Shortcuts
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const btn = get('reviewBtn');
                if (btn) btn.click();
            } else if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
                e.preventDefault();
                window.location.href = '/generate';
            } else if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const search = get('search-results');
                if (search) {
                    search.classList.toggle('hidden');
                    if (!search.classList.contains('hidden')) search.focus();
                }
            } else if (e.altKey && e.shiftKey && e.key === 'F') {
                e.preventDefault();
                formatCode();
            } else if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
                e.preventDefault();
                cmdPalette.classList.remove('hidden');
                cmdInput.focus();
                renderCommands();
            } else if (e.key === 'Escape') {
                cmdPalette.classList.add('hidden');
                settingsModal.classList.add('hidden');
            }
        });

        // Voice Coding
        setClick('voiceCodeBtn', () => {
            if (!('webkitSpeechRecognition' in window)) return showToast("Voice not supported in this browser", "error");
            const recognition = new webkitSpeechRecognition();
            recognition.lang = 'en-US';
            recognition.start();
            showToast("Listening...", "info");
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                showToast(`Heard: "${transcript}"`, "info");
                if(transcript.includes("format")) formatCode();
                else if(transcript.includes("run")) runCode();
                else if(transcript.includes("clear")) get('clearEditorBtn').click();
            }
        });

        // Logout Function
        window.logout = function() {
            localStorage.removeItem('token');
            sessionStorage.removeItem('token');
            window.location.href = '/login';
        };

        console.log("✅ Code Refine: Initialization Complete");

    } catch (criticalError) {
        console.error("CRITICAL INIT ERROR:", criticalError);
        alert("Application failed to initialize. Check console for details.");
    }
};

// Run Init
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}