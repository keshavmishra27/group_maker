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
    const groupContainer = document.getElementById("group");
    const rewardText = document.getElementById("reward");

    groupContainer.innerHTML = "";
    rewardText.textContent = "Generating all groups…";

    const res = await fetch(`${API}/groups/generate-all`);
    const data = await res.json();

    groupContainer.innerHTML = "";

    data.groups.forEach((grp, gIndex) => {
        const title = document.createElement("li");
        title.innerHTML = `<strong>Group ${gIndex + 1} (Reward: ${grp.reward})</strong>`;
        title.style.marginTop = "12px";
        groupContainer.appendChild(title);

        grp.members.forEach((m, index) => {
            const li = document.createElement("li");
            li.textContent = `${m.name} (${m.category})`;
            li.style.opacity = 0;
            li.style.marginLeft = "12px";

            groupContainer.appendChild(li);

            anime({
                targets: li,
                opacity: [0, 1],
                translateX: [-15, 0],
                delay: (gIndex * 300) + (index * 80),
                duration: 500,
                easing: "easeOutQuad"
            });
        });
    });

    rewardText.textContent = `Total Groups Generated: ${data.total_groups}`;

    if (window.pulseSuccess) {
        window.pulseSuccess();
    }
}
