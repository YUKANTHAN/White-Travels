// --- SEARCH & UI NAVIGATION ---
function headerSearch(e) {
    if(e) e.preventDefault();
    const dest = (document.getElementById('search-bar').value || '').toLowerCase();
    const routeMap = {
        'cabo': '/destinations/cabo',
        'tokyo': '/destinations/tokyo',
        'london': '/destinations/london',
        'paris': '/destinations/paris',
        'new york': '/destinations/new_york_city',
        'honolulu': '/destinations/honolulu'
    };
    for (const [key, url] of Object.entries(routeMap)) {
        if (dest.includes(key)) {
            window.location.href = url;
            return;
        }
    }
}

// --- CHAT & MODAL LOGIC (Floating AI Modal) ---
function toggleChat() {
    const modal = document.getElementById('ai-chat-modal');
    const sections = document.querySelectorAll('header, section, footer');
    
    if (modal.style.display === 'none' || !modal.style.display) {
        modal.style.display = 'flex';
        sections.forEach(el => { if(el) el.style.filter = 'blur(15px)'; });
    } else {
        modal.style.display = 'none';
        sections.forEach(el => { if(el) el.style.filter = 'none'; });
    }
}

function chatSuggestion(text) {
    document.getElementById('chat-input').value = text;
    handleChatSubmit(new Event('submit'));
}

async function handleChatSubmit(e) {
    if(e) e.preventDefault();
    const input = document.getElementById('chat-input');
    const msg = input.value;
    if(!msg) return;
    
    appendChatMessage('user', msg);
    input.value = '';
    
    const aiLog = document.getElementById('skill-reasoning-log');
    if(aiLog) aiLog.innerHTML = `<p style="color: #38bdf8;">[PROCESS]: Analyzing "${msg}"...</p>`;
    
    try {
        const res = await fetch('/ai/plan', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ dest: msg, transport: 'Flight', prefs: 'Interactive' })
        });
        const data = await res.json();
        
        appendChatMessage('ai', "I have orchestrated your master plan. You can view it below the chat box in the Travel Expert section!");
        
        const planOutput = document.getElementById('ai-plan-output');
        if(planOutput) {
            planOutput.innerHTML = data.plan.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
        }
        
        await refreshItineraryStatus();
    } catch (err) {
        appendChatMessage('ai', "Error connecting to Deep Concierge. Check your terminal.");
    }
}

function appendChatMessage(role, text) {
    const chat = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.style.alignSelf = role === 'user' ? 'flex-end' : 'flex-start';
    div.style.background = role === 'user' ? '#38bdf8' : '#1e293b';
    div.style.color = role === 'user' ? '#000' : '#fff';
    div.style.padding = '1.5rem 2rem';
    div.style.borderRadius = role === 'user' ? '2rem 2rem 0 2rem' : '2rem 2rem 2rem 0';
    div.style.fontSize = '1.4rem';
    div.style.maxWidth = '80%';
    div.innerText = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function toggleAIAssistant() {
    const modal = document.getElementById('quick-book-modal');
    if (modal) {
        modal.style.display = 'flex';
        nextQB(1);
    } else {
        window.location.href = '/?quickbook=1';
    }
}

async function sendAIChat() {
    const input = document.getElementById('ai-chat-input');
    const body = document.getElementById('ai-chat-body');
    const prompt = (input.value || '').trim();
    if(!prompt) return;

    appendChatBubble(body, prompt, 'user');
    input.value = '';
    
    const botDiv = appendChatBubble(body, "Thinking...", 'bot');
    try {
        const res = await fetch('/ai/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        });
        const d = await res.json();
        botDiv.innerText = d.response;
    } catch(e) { botDiv.innerText = "Deep Concierge is briefly offline."; }
    body.scrollTop = body.scrollHeight;
}

// --- HERO CHAT LOGIC ---
async function sendHeroChat() {
    const input = document.getElementById('hero-chat-input');
    const body = document.getElementById('hero-chat-messages');
    const prompt = (input.value || '').trim();
    if(!prompt) return;

    // User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'user-msg';
    userDiv.innerText = prompt;
    body.appendChild(userDiv);
    input.value = '';
    body.scrollTop = body.scrollHeight;

    // Bot Response
    const botDiv = document.createElement('div');
    botDiv.className = 'ai-msg';
    botDiv.innerText = 'Analyzing your journey...';
    body.appendChild(botDiv);
    
    try {
        const res = await fetch('/ai/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        });
        const d = await res.json();
        botDiv.innerText = d.response;
        
        // If the prompt strictly signals intent to plan or book a trip, offer the detailed planner
        const lowerPrompt = prompt.toLowerCase();
        if (lowerPrompt.includes('plan') || lowerPrompt.includes('want to go') || lowerPrompt.includes('book') || lowerPrompt.includes('surprise me')) {
            const planBtn = document.createElement('button');
            planBtn.className = 'btn';
            planBtn.style.cssText = 'margin-top: 1rem; padding: 0.8rem 1.5rem; font-size: 1.2rem; display: block;';
            planBtn.innerHTML = '<i class="fas fa-magic"></i> Open Detailed Planner';
            planBtn.onclick = () => toggleAIAssistant();
            botDiv.appendChild(planBtn);
        }
    } catch(e) { 
        botDiv.innerText = "Deep Concierge is briefly offline. Try again later."; 
    }
    body.scrollTop = body.scrollHeight;
}

function appendChatBubble(body, text, type) {
    const div = document.createElement('div');
    div.style.cssText = type === 'user' 
        ? "align-self: flex-end; background: #38bdf8; color: #fff; padding: 1rem 1.5rem; border-radius: 15px 15px 0 15px; max-width: 85%; font-size: 1.4rem; line-height: 1.6;"
        : "align-self: flex-start; background: #fff; padding: 1rem 1.5rem; border-radius: 15px 15px 15px 0; border: 1px solid #e2e8f0; max-width: 85%; color: #1e293b; font-size: 1.4rem; line-height: 1.6;";
    div.innerText = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
    return div;
}

// --- SIMULATION & MONITORING ---
async function simulateAIBooking(flightNo, trainNo, hotelName) {
    try {
        const payload = {};
        if (flightNo) payload.flight_no = flightNo;
        if (trainNo) payload.train_no = trainNo;
        if (hotelName) payload.hotel = hotelName;

        const res = await fetch('/booking/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.success) {
            let type = flightNo ? `Flight ${flightNo}` : (trainNo ? `Train ${trainNo}` : `Hotel ${hotelName}`);
            alert(`[AI CONCIERGE]: Payment successful! ${type} locked. Disruption monitoring activated...`);
            window.location.href = '/#travel-expert-monitor';
        }
    } catch (err) { console.error("Simulation failed:", err); }
}

let currentPaymentType = null;
let currentPaymentId = null;

window.requestPayment = function(type, id) {
    currentPaymentType = type;
    currentPaymentId = id;
    
    let modal = document.getElementById('global-payment-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'global-payment-modal';
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); z-index: 20000; display: flex; align-items: center; justify-content: center;';
        
        modal.innerHTML = `
            <div style="background: #fff; width: 500px; padding: 4rem; border-radius: 2rem; position: relative;">
                <i class="fas fa-times" onclick="document.getElementById('global-payment-modal').style.display='none'" style="position: absolute; top: 2rem; right: 2rem; font-size: 2.5rem; cursor: pointer; color: #666;" aria-label="Close payment"></i>
                <h2 style="font-size: 2.5rem; margin-bottom: 2rem; color: #0f172a;"><i class="fas fa-lock" style="color: #10b981;"></i> Secure Checkout</h2>
                <p style="font-size: 1.4rem; color: #64748b; margin-bottom: 2rem;">Please enter your card details to finalize the transaction for this ${type}.</p>
                <form onsubmit="confirmGlobalPayment(event)" style="display: flex; flex-direction: column; gap: 1.5rem;">
                    <input type="text" id="global-card-input" placeholder="Card Number (required)" required style="width: 100%; padding: 1.5rem; font-size: 1.6rem; border: 1px solid #e2e8f0; border-radius: .8rem; box-sizing: border-box;">
                    <button type="submit" class="btn" style="width: 100%; padding: 1.5rem; font-size: 1.6rem; background: #0f172a; color: #fff; border: none; border-radius: .8rem; cursor: pointer;">
                        Confirm Payment
                    </button>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
    }
    document.getElementById('global-card-input').value = '';
    modal.style.display = 'flex';
};

window.confirmGlobalPayment = function(e) {
    e.preventDefault();
    document.getElementById('global-payment-modal').style.display = 'none';
    
    if (currentPaymentType === 'flight') {
        simulateAIBooking(currentPaymentId, null, null);
    } else if (currentPaymentType === 'train') {
        simulateAIBooking(null, currentPaymentId, null);
    } else if (currentPaymentType === 'hotel') {
        simulateAIBooking(null, null, currentPaymentId);
    }
};

let lastNotifiedState = '';

async function refreshItineraryStatus() {
    try {
        const res = await fetch('/itinerary/status');
        const data = await res.json();
        const passengerEl = document.getElementById('itinerary-passenger');
        const flightEl = document.getElementById('itinerary-flight');
        const trainEl = document.getElementById('itinerary-train');
        const statusEl = document.getElementById('itinerary-status');
        const pnrEl = document.getElementById('itinerary-pnr');
        const seatEl = document.getElementById('itinerary-seat');
        const gateEl = document.getElementById('itinerary-gate');
        const visaEl = document.getElementById('itinerary-visa');
        const spentEl = document.getElementById('itinerary-spent');
        const limitEl = document.getElementById('itinerary-limit');
        const carbonEl = document.getElementById('itinerary-carbon');
        const budgetBar = document.getElementById('itinerary-budget-bar');
        
        if(passengerEl) passengerEl.innerText = data.passenger_name || 'Anonymous';
        if(flightEl) flightEl.innerText = data.flight_no || '---';
        if(trainEl) trainEl.innerText = data.train_no || '---';
        if(pnrEl) pnrEl.innerText = data.pnr || '---';
        if(seatEl) seatEl.innerText = (data.seat || '--') + ' / ' + (data.class_type || '--');
        if(gateEl) gateEl.innerText = (data.gate || '--') + ' | ' + (data.boarding_time || '--');
        if(visaEl) visaEl.innerText = data.visa_status || 'Visa-Free';
        if(spentEl) spentEl.innerText = `$${data.budget_spent || 0}`;
        if(limitEl) limitEl.innerText = `$${data.budget_limit || 2500}`;
        if(carbonEl) carbonEl.innerText = data.carbon_kg || '---';
        if(budgetBar) {
            const perc = ((data.budget_spent || 0) / (data.budget_limit || 2500)) * 100;
            budgetBar.style.width = `${perc}%`;
        }

        if(statusEl) {
            statusEl.innerText = data.status ? data.status.toUpperCase() : '---';
            if(data.status && data.status.toUpperCase() === 'CANCELLED') {
                statusEl.style.color = '#e11d48';
                statusEl.style.background = 'rgba(225, 29, 72, 0.1)';
            } else if(data.status && data.status.toUpperCase() === 'REBOOKED') {
                statusEl.style.color = '#38bdf8';
                statusEl.style.background = 'rgba(56, 189, 248, 0.1)';
            } else {
                statusEl.style.color = '#10b981';
                statusEl.style.background = 'rgba(16, 185, 129, 0.1)';
            }
        }

        // Real-time Notification Injection
        const currentState = (data.flight_no || '') + '|' + (data.train_no || '') + '|' + (data.status || '');
        if (data.status && data.status.toUpperCase() === 'CANCELLED' && currentState !== lastNotifiedState) {
            lastNotifiedState = currentState;
            const notifBox = document.getElementById('dynamic-notifications');
            const badge = document.getElementById('notification-badge');
            
            if (notifBox) {
                if (notifBox.innerHTML.includes('No recent disruptions detected.')) {
                    notifBox.innerHTML = ''; 
                }
                const flAlert = data.flight_no ? `Flight ${data.flight_no}` : '';
                const trAlert = data.train_no ? `Train ${data.train_no}` : '';
                const joined = [flAlert, trAlert].filter(Boolean).join(' & ');
                
                const ticketInfo = `[${data.passenger_name || 'Passenger'}] ${data.seat ? 'Seat ' + data.seat : ''}`;

                const alertHtml = `
                    <div class="alert-item" style="margin-bottom: 1.5rem; padding: 1rem; background: #fff5f5; border-left: 4px solid #e11d48; border-radius: 0.5rem; animation: fadein 0.5s;">
                        <p style="font-size: 1.4rem; color: #333; margin-bottom: 0.5rem;"><b><i class="fas fa-exclamation-triangle" style="color: #e11d48;"></i> TARGETED DISRUPTION: ${joined} Cancelled!</b></p>
                        <p style="font-size: 1.2rem; color: #666; margin-bottom: 0.5rem;">The AI monitor detected a cancellation for your exact booked ticket: <span style="font-weight: bold; color: #333;">${ticketInfo}</span>.</p>
                        <p style="font-size: 1.1rem; color: #64748b; margin-top: .5rem;"><a href="/#travel-expert-monitor" style="color: var(--primary); font-weight: bold;">Tap For AI Recovery Strategy</a></p>
                    </div>
                `;
                notifBox.innerHTML = alertHtml + notifBox.innerHTML;
            }
            if (badge) {
                badge.style.display = 'block';
                badge.innerText = parseInt(badge.innerText || '0') + 1;
            }
        }
        
        return data.status;
    } catch (err) { console.error("Error refreshing itinerary:", err); }
}

async function triggerSkillDisruption() {
    const log = document.getElementById('skill-reasoning-log');
    if(log) log.innerHTML = "<p style='color: #a855f7;'><i class='fas fa-search'></i> [SYSTEM]: Pinging suthan06it.app.n8n.cloud... AI Agent is actively searching Google...</p>";
    
    try {
        const res = await fetch('/itinerary/disruption', { method: 'POST' });
        const data = await res.json();
        
        if(data.success) {
            await refreshItineraryStatus();
            if(log) {
                if(data.status === 'CANCELLED') {
                    log.innerHTML += `<p style='color: #e11d48;'>[ALERT]: AI Search determined status is CANCELLED.</p>`;
                    log.innerHTML += `<p style='color: #fca5a5;'>[LIVE REASON]: ${data.reason}</p>`;
                    log.innerHTML += "<p style='color: #fff;'>[SKILL]: Workspace Watcher activated.</p>";
                    
                    setTimeout(async () => {
                        log.innerHTML += "<p style='color: #38bdf8;'>[AGENT]: rebook_logic.py triggered. Querying recovery AI...</p>";
                        const rebookRes = await fetch('/itinerary/rebook', { method: 'POST' });
                        const rebookData = await rebookRes.json();
                        
                        if(rebookData.success) {
                            const output = rebookData.output.split('\\n').filter(l => l.includes('[REBOOKER]') || l.includes('[N8N RECOVERY]')).join('<br>');
                            log.innerHTML += `<p style='color: #10b981;'>[SUCCESS]: <br>${output}</p>`;
                            await refreshItineraryStatus();
                        }
                    }, 2000);
                } else {
                    log.innerHTML += `<p style='color: #10b981;'>[OK]: Checked Web - Flight/Train is CONFIRMED.</p>`;
                    log.innerHTML += `<p style='color: #6ee7b7;'>[LIVE REASON]: ${data.reason}</p>`;
                }
            }
        }
    } catch (err) { console.error("Disruption trigger failed:", err); }
}

// --- QUICK BOOK (QB) MULTI-STEP LOGIC ---
function nextQB(step) {
    document.querySelectorAll('.qb-step').forEach(el => el.style.display = 'none');
    const target = document.getElementById(`qb-step-${step}`);
    if(target) target.style.display = 'block';
}

function closeQuickBook() {
    document.getElementById('quick-book-modal').style.display = 'none';
}

function closeWelcomePopup() {
    const modal = document.getElementById('welcome-onload-modal');
    if(modal) {
        modal.style.opacity = '0';
        modal.querySelector('.welcome-modal-content').style.transform = 'translateY(20px)';
        setTimeout(() => modal.style.display = 'none', 500);
    }
}

let userPlanChoices = {};

function generatePlan() {
    const dest = document.getElementById('qb-destination').value;
    const days = document.getElementById('qb-days').value || "1";
    const budget = document.getElementById('qb-budget').value || "1000";
    const people = document.getElementById('qb-people').value || "1";
    const prefs = document.getElementById('qb-preferences').value || "general exploring";

    if(!dest) return alert("Please enter a destination!");
    
    nextQB(6);
    const planBox = document.getElementById('qb-plan-content');
    userPlanChoices = { dest, days, budget, people, prefs };
    
    // Step 1: Transport Choice
    planBox.innerHTML = `
        <div style="margin-bottom: 2rem;">
            <b>🤖 Agent:</b> I am analyzing routes to ${dest}. To optimize your budget of $${budget}, please review your transport options:
        </div>
        <div style="display: flex; gap: 2rem; margin-bottom: 2rem;">
            <div style="flex: 1; padding: 1.5rem; border: 1px solid #e2e8f0; border-radius: 1rem; background: #f8fafc;">
                <h4 style="margin-bottom: 1rem; color: #0f172a; font-size: 1.6rem;">✈️ Option A: Flight</h4>
                <ul style="font-size: 1.3rem; margin-bottom: 1.5rem; color: #475569; padding-left: 2rem;">
                    <li><b style="color: #10b981;">Pros:</b> Extremely fast, skip terrain.</li>
                    <li><b style="color: #ef4444;">Cons:</b> Higher CO2 footprint, airport wait times.</li>
                    <li style="margin-top: .5rem;"><b style="color: #38bdf8;">Why choose this?</b> Best if you have limited days and want to maximize your actual time at the destination.</li>
                </ul>
                <button onclick="handlePlanChoice('transport', 'Flight', this.closest('#qb-plan-content'))" class="btn" style="width: 100%; background: #38bdf8; padding: 1rem; font-size: 1.4rem;">Select Flight</button>
            </div>
            <div style="flex: 1; padding: 1.5rem; border: 1px solid #e2e8f0; border-radius: 1rem; background: #f8fafc;">
                <h4 style="margin-bottom: 1rem; color: #0f172a; font-size: 1.6rem;">🚆 Option B: Train</h4>
                <ul style="font-size: 1.3rem; margin-bottom: 1.5rem; color: #475569; padding-left: 2rem;">
                    <li><b style="color: #10b981;">Pros:</b> Scenic views, highly sustainable.</li>
                    <li><b style="color: #ef4444;">Cons:</b> Takes significantly longer.</li>
                    <li style="margin-top: .5rem;"><b style="color: #38bdf8;">Why choose this?</b> Best if you love the journey itself, have lots of time, or want a greener footprint.</li>
                </ul>
                <button onclick="handlePlanChoice('transport', 'Train', this.closest('#qb-plan-content'))" class="btn" style="width: 100%; background: #10b981; padding: 1rem; font-size: 1.4rem;">Select Train</button>
            </div>
        </div>
    `;
}

window.handlePlanChoice = function(type, choice, box) {
    userPlanChoices[type] = choice;
    
    if (type === 'transport') {
        box.innerHTML = `
            <div style="margin-bottom: 2rem;">
                <b>🤖 Agent:</b> Great, ${choice} secured! Now, regarding your preferences for "${userPlanChoices.prefs}", here are two tailored itineraries:
            </div>
            <div style="display: flex; gap: 2rem; margin-bottom: 2rem;">
                <div style="flex: 1; padding: 1.5rem; border: 1px solid #e2e8f0; border-radius: 1rem; background: #fcf6e5;">
                    <h4 style="margin-bottom: 1rem; color: #0f172a; font-size: 1.6rem;">🏛️ Plan A: Heritage & Culture</h4>
                    <ul style="font-size: 1.3rem; margin-bottom: 1.5rem; color: #475569; padding-left: 2rem;">
                        <li><b style="color: #10b981;">Pros:</b> Deeply educational, iconic photos.</li>
                        <li><b style="color: #ef4444;">Cons:</b> Can be crowded, heavy walking.</li>
                        <li style="margin-top: .5rem;"><b style="color: #f59e0b;">Why choose this?</b> Perfect if you want to understand the deep history of the city and see the main landmarks.</li>
                    </ul>
                    <button onclick="handlePlanChoice('places', 'Historical & Culture', this.closest('#qb-plan-content'))" class="btn" style="width: 100%; background: #f59e0b; padding: 1rem; font-size: 1.4rem;">Lock Plan A</button>
                </div>
                <div style="flex: 1; padding: 1.5rem; border: 1px solid #e2e8f0; border-radius: 1rem; background: #f4ecfc;">
                    <h4 style="margin-bottom: 1rem; color: #0f172a; font-size: 1.6rem;">🌳 Plan B: Outdoors & Adventure</h4>
                    <ul style="font-size: 1.3rem; margin-bottom: 1.5rem; color: #475569; padding-left: 2rem;">
                        <li><b style="color: #10b981;">Pros:</b> Relaxing, away from tourist traps.</li>
                        <li><b style="color: #ef4444;">Cons:</b> Heavily dependent on good weather.</li>
                        <li style="margin-top: .5rem;"><b style="color: #8b5cf6;">Why choose this?</b> Ideal if you want a local, authentic, and refreshing experience away from crowds.</li>
                    </ul>
                    <button onclick="handlePlanChoice('places', 'Outdoor & Adventure', this.closest('#qb-plan-content'))" class="btn" style="width: 100%; background: #8b5cf6; padding: 1rem; font-size: 1.4rem;">Lock Plan B</button>
                </div>
            </div>
        `;
    } else if (type === 'places') {
        box.innerHTML = `
            <div style="margin-bottom: 2rem;">
                <b>🤖 Agent:</b> Choice locked. Finally, let's establish a disruption contingency plan for your group of ${userPlanChoices.people}:
            </div>
            <div style="display: flex; gap: 2rem; margin-bottom: 2rem;">
                <div style="flex: 1; padding: 1.5rem; border: 1px solid #e2e8f0; border-radius: 1rem; background: #ffeeee;">
                    <h4 style="margin-bottom: 1rem; color: #0f172a; font-size: 1.6rem;">🚕 Pivot Strategy + Cabs</h4>
                    <ul style="font-size: 1.3rem; margin-bottom: 1.5rem; color: #475569; padding-left: 2rem;">
                        <li><b style="color: #10b981;">Pros:</b> Zero missed events, super comfortable.</li>
                        <li><b style="color: #ef4444;">Cons:</b> More exhausting, higher cab fees.</li>
                        <li style="margin-top: .5rem;"><b style="color: #ef4444;">Why choose this?</b> Choose this if you absolutely do not want to miss any planned activities and don't mind a tighter schedule.</li>
                    </ul>
                    <button onclick="handlePlanChoice('final', 'Pivot & Cab', this.closest('#qb-plan-content'))" class="btn" style="width: 100%; background: #ef4444; padding: 1rem; font-size: 1.2rem;">Select Pivot</button>
                </div>
                <div style="flex: 1; padding: 1.5rem; border: 1px solid #e2e8f0; border-radius: 1rem; background: #e0f2fe;">
                    <h4 style="margin-bottom: 1rem; color: #0f172a; font-size: 1.6rem;">🚇 Skip Activities + Metro</h4>
                    <ul style="font-size: 1.3rem; margin-bottom: 1.5rem; color: #475569; padding-left: 2rem;">
                        <li><b style="color: #10b981;">Pros:</b> Keeps the trip relaxed, extremely cheap.</li>
                        <li><b style="color: #ef4444;">Cons:</b> You will have to skip some planned sights.</li>
                        <li style="margin-top: .5rem;"><b style="color: #3b82f6;">Why choose this?</b> Best if you prefer a stress-free trip and are okay with missing a few minor spots.</li>
                    </ul>
                    <button onclick="handlePlanChoice('final', 'Skip & Metro', this.closest('#qb-plan-content'))" class="btn" style="width: 100%; background: #3b82f6; padding: 1rem; font-size: 1.2rem;">Select Skip</button>
                </div>
            </div>
        `;
    } else if (type === 'final') {
        box.innerHTML = `<div class='loader'></div> Generating your Final Master Itinerary...`;
        fetchFinalPlan(box);
    }
};

async function fetchFinalPlan(box) {
    try {
        const res = await fetch('/ai/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userPlanChoices)
        });
        const data = await res.json();
        let htmlPlan = data.plan
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<b style="color: var(--primary);">$1</b>')
            .replace(/#### (.*?)(<br>|$)/g, '<h4 style="font-size: 1.8rem; color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: .5rem; margin-top: 1rem; margin-bottom: 1rem;">$1</h4>')
            .replace(/• (.*?)(<br>|$)/g, '<li style="margin-left: 2rem; margin-bottom: .5rem;">$1</li>');
        box.innerHTML = htmlPlan;
    } catch(e) {
        box.innerHTML = "Error generating plan. Please try again.";
    }
}

function confirmQuickBook() {
    closeQuickBook();
    const type = userPlanChoices.transport ? userPlanChoices.transport.toLowerCase() : 'flight';
    const fakeNum = Math.floor(Math.random() * 900 + 100);
    const id = type === 'flight' ? "DL" + fakeNum : "TRN" + fakeNum;
    requestPayment(type, id);
}

// Smart Polling: pause when tab is hidden, resume when visible
let pollIntervalId = null;

function startSmartPolling() {
    if (pollIntervalId) clearInterval(pollIntervalId);
    pollIntervalId = setInterval(refreshItineraryStatus, 10000);
}

function stopPolling() {
    if (pollIntervalId) {
        clearInterval(pollIntervalId);
        pollIntervalId = null;
    }
}

// UI Feature Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Real-time background polling with visibility awareness
    if(document.getElementById('ai-notifications')) {
        startSmartPolling();
        
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopPolling();
            } else {
                refreshItineraryStatus(); // Immediate refresh on tab return
                startSmartPolling();
            }
        });
    }

    if (window.location.search.includes('quickbook=1')) {
        const modal = document.getElementById('quick-book-modal');
        if (modal) {
            modal.style.display = 'flex';
            nextQB(1);
        }
    }

    const loginBtn = document.querySelector('#login-btn');
    const loginForm = document.querySelector('.login-form-container');
    const formClose = document.querySelector('#form-close');
    const searchBtn = document.querySelector('#search-btn');
    const searchBar = document.querySelector('.search-bar-container');

    if(loginBtn && loginForm) {
        loginBtn.addEventListener('click', () => {
            loginForm.classList.add('active');
        });
    }

    if(formClose && loginForm) {
        formClose.addEventListener('click', () => {
            loginForm.classList.remove('active');
        });
    }

    if(searchBtn && searchBar) {
        searchBtn.addEventListener('click', () => {
            searchBar.classList.toggle('active');
        });
    }

    const qbTrigger = document.getElementById('quick-book-trigger');
    if(qbTrigger) {
        qbTrigger.addEventListener('click', () => {
            document.getElementById('quick-book-modal').style.display = 'flex';
            nextQB(1);
        });
    }

    if(document.getElementById('itinerary-live-box')) refreshItineraryStatus();
});

document.addEventListener('keydown', (e) => {
    if(e.key === 'Enter' && document.activeElement && document.activeElement.id === 'ai-chat-input') sendAIChat();
});
