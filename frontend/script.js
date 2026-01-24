const API = "http://127.0.0.1:8000";

async function fetchMembers() {
    const list = document.getElementById("members");
    list.innerHTML = "";

    if (window.startLoading) window.startLoading();

    const res = await fetch(`${API}/members/`);
    const members = await res.json();

    members.forEach((m, index) => {
        const li = document.createElement("li");
        li.textContent = `${m.name} (${m.category})`;
        li.style.opacity = 0;
        list.appendChild(li);

        anime({
            targets: li,
            opacity: [0, 1],
            translateX: [-20, 0],
            delay: index * 30,
            duration: 500,
            easing: "easeOutQuad"
        });
    });

    if (window.stopLoading) window.stopLoading();
}

async function generateGroup() {
    const list = document.getElementById("group");
    const rewardText = document.getElementById("reward");

    list.innerHTML = "";
    rewardText.textContent = "Generating…";

    if (window.startLoading) window.startLoading();

    const res = await fetch(`${API}/groups/generate`);
    const data = await res.json();

    list.innerHTML = "";

    data.members.forEach((m, index) => {
        const li = document.createElement("li");
        li.textContent = `${m.name} (${m.category})`;
        li.style.opacity = 0;
        list.appendChild(li);

        anime({
            targets: li,
            opacity: [0, 1],
            scale: [0.9, 1],
            delay: index * 120,
            duration: 600,
            easing: "easeOutBack"
        });
    });

    anime({
        targets: rewardText,
        opacity: [0, 1],
        translateY: [10, 0],
        duration: 600,
        easing: "easeOutCubic"
    });

    rewardText.textContent = `Reward Score: ${data.reward}`;

    if (window.updateRewardColor) {
        window.updateRewardColor(data.reward);
    }

    if (window.stopLoading) window.stopLoading();
}


async function generateAllGroups() {
    const container = document.getElementById("group");
    container.innerHTML = "<p>Generating all groups...</p>";

    const res = await fetch("http://127.0.0.1:8000/groups/generate-all");
    const data = await res.json();

    console.log("API RESPONSE:", data); // keep for sanity

    container.innerHTML = "";

    if (!data.groups || !data.groups.length) {
        container.innerHTML = "<p>No groups generated.</p>";
        return;
    }

    data.groups.forEach((g, index) => {
        const groupTitle = document.createElement("h4");
        groupTitle.textContent = `Group ${g.group_id} (Reward: ${g.reward})`;
        container.appendChild(groupTitle);

        const ul = document.createElement("ul");

        g.group.forEach(member => {
            const li = document.createElement("li");
            li.textContent = `${member.name} (${member.category})`;
            ul.appendChild(li);
        });

        container.appendChild(ul);
    });

    const summary = document.createElement("p");
    summary.innerHTML = `
        <strong>Total Groups:</strong> ${data.total_groups}<br>
        <strong>Students Used:</strong> ${data.students_used}
    `;
    container.appendChild(summary);
}

