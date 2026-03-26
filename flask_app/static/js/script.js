// --- SEARCH & UI NAVIGATION ---
function headerSearch(e) {
    if(e) e.preventDefault();
    const dest = document.getElementById('search-bar').value;
    if(dest.toLowerCase().includes('cabo')) window.location.href = '/destinations/cabo';
    else if(dest.toLowerCase().includes('tokyo')) window.location.href = '/destinations/tokyo';
    else if(dest.toLowerCase().includes('london')) window.location.href = '/destinations/london';
    else if(dest.toLowerCase().includes('paris')) window.location.href = '/destinations/paris';
    else if(dest.toLowerCase().includes('new york')) window.location.href = '/destinations/new_york_city';
    else if(dest.toLowerCase().includes('honolulu')) window.location.href = '/destinations/honolulu';
}

// --- AI CONCIERGE CHAT ---
function toggleAIChat() {
    const chatWin = document.getElementById('ai-chat-window');
    if(chatWin) {
        chatWin.style.display = chatWin.style.display === 'none' ? 'flex' : 'none';
        if(chatWin.style.display === 'flex') document.getElementById('ai-chat-input').focus();
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
async function simulateAIBooking(flightNo) {
    try {
        const res = await fetch('/booking/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ flight_no: flightNo })
        });
        const data = await res.json();
        if(data.success) {
            alert(`[AI CONCIERGE]: Flight ${flightNo} locked! Monitoring actual status in workspace...`);
            window.location.href = '/#travel-expert-monitor';
        }
    } catch (err) { console.error("Simulation failed:", err); }
}

async function refreshItineraryStatus() {
    try {
        const res = await fetch('/itinerary/status');
        const data = await res.json();
        const flightEl = document.getElementById('itinerary-flight');
        const statusEl = document.getElementById('itinerary-status');
        const pnrEl = document.getElementById('itinerary-pnr');
        
        if(flightEl) flightEl.innerText = data.flight_no || '---';
        if(pnrEl) pnrEl.innerText = data.pnr || '---';
        if(statusEl) {
            statusEl.innerText = data.status.toUpperCase();
            if(data.status.toUpperCase() === 'CANCELLED') {
                statusEl.style.color = '#e11d48';
                statusEl.style.background = 'rgba(225, 29, 72, 0.1)';
            } else if(data.status.toUpperCase() === 'REBOOKED') {
                statusEl.style.color = '#38bdf8';
                statusEl.style.background = 'rgba(56, 189, 248, 0.1)';
            } else {
                statusEl.style.color = '#10b981';
                statusEl.style.background = 'rgba(16, 185, 129, 0.1)';
            }
        }
        return data.status;
    } catch (err) { console.error("Error refreshing itinerary:", err); }
}

async function triggerSkillDisruption() {
    const log = document.getElementById('skill-reasoning-log');
    if(log) log.innerHTML = "<p style='color: #fbbf24;'>[SYSTEM]: Sending disruption signal to itinerary.json...</p>";
    
    try {
        const res = await fetch('/itinerary/disruption', { method: 'POST' });
        const data = await res.json();
        
        if(data.success) {
            await refreshItineraryStatus();
            if(log) {
                log.innerHTML += "<p style='color: #e11d48;'>[ALERT]: itinerary.json status changed to CANCELLED.</p>";
                log.innerHTML += "<p style='color: #fff;'>[SKILL]: Workspace Watcher activated.</p>";
                
                setTimeout(async () => {
                    log.innerHTML += "<p style='color: #38bdf8;'>[AGENT]: rebook_logic.py triggered. Querying Amadeus API...</p>";
                    const rebookRes = await fetch('/itinerary/rebook', { method: 'POST' });
                    const rebookData = await rebookRes.json();
                    
                    if(rebookData.success) {
                        const output = rebookData.output.split('\n').filter(l => l.includes('[REBOOKER]')).join('<br>');
                        log.innerHTML += `<p style='color: #10b981;'>[SUCCESS]: <br>${output}</p>`;
                        await refreshItineraryStatus();
                    }
                }, 2000);
            }
        }
    } catch (err) { console.error("Disruption trigger failed:", err); }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    if(document.getElementById('itinerary-live-box')) refreshItineraryStatus();
});

document.addEventListener('keydown', (e) => {
    if(e.key === 'Enter' && document.activeElement && document.activeElement.id === 'ai-chat-input') sendAIChat();
});
