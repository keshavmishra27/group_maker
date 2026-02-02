const API = "http://127.0.0.1:8000";

// Helper: Get params from URL
function getDomainId() {
    return new URLSearchParams(window.location.search).get('domain_id');
}
function getDomainName() {
    return new URLSearchParams(window.location.search).get('domain_name') || 'Domain';
}

// 1. Auto-run when page loads to set the Title
window.addEventListener('DOMContentLoaded', () => {
    const name = getDomainName();
    const titleEl = document.querySelector('.title h1');
    if (titleEl) {
        titleEl.textContent = `${name} Details`; // Sets heading to "Cybersecurity Details"
    }
});

// 2. The function triggered by your Button
async function fetchMembers() {
    const domainId = getDomainId();
    const domainName = getDomainName();
    const listContainer = document.getElementById("members-container");

    if (!domainId) {
        alert("Error: No Domain ID found in URL. Please go back to Home.");
        return;
    }

    // Show Loading
    listContainer.innerHTML = `<p style='text-align: center; color: #7dd3fc;'>Loading ${domainName} members...</p>`;

    try {
        const res = await fetch(`${API}/members?domain_id=${domainId}`);
        const members = await res.json();

        // Build HTML
        let html = `<h2 style="color: #22c55e; border-bottom: 1px solid #444; padding-bottom: 10px;">${domainName} Members</h2>`;
        
        if (members.length === 0) {
            html += `<p>No members found.</p>`;
        } else {
            html += `<ul>`;
            members.forEach(m => {
                html += `<li style="color: #cbd5e1; margin-top: 5px; list-style: none;">
                            • <strong>${m.name}</strong> <span style="color: #94a3b8;">(${m.category})</span>
                         </li>`;
            });
            html += `</ul>`;
        }
        
        listContainer.innerHTML = html;

    } catch (error) {
        console.error(error);
        listContainer.innerHTML = `<p style='color: red;'>Server Error: ${error.message}</p>`;
    }
}