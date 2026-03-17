const cards = Array.from(document.querySelectorAll(".card"));
const maxLength = cards.length - 1;
let currentIndex = 0;

function initZIndex() {
  cards.forEach((card, index) => {
    card.style.zIndex = cards.length - index;
  });
}

initZIndex();

function goPrev() {
  if (currentIndex > 0) {
    currentIndex--;
    cards[currentIndex].classList.remove("flipped");
  }
}

function goNext() {
  if (currentIndex < maxLength) {
    cards[currentIndex].classList.add("flipped");
    currentIndex++;
  }
}

function resetDeck() {
  cards.forEach((card) => {
    card.classList.remove("flipped");
  });
  currentIndex = 0;
}

// Fetch and load projects dynamically
async function loadProjects() {
  try {
    const response = await fetch("./projects.json");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const projectsContainer = document.getElementById("projects-container");

    if (!projectsContainer) return;

    projectsContainer.innerHTML = data.Projects.map((project) => {
      const isIOS = project.link.includes("apps.apple.com");
      const ctaClass = isIOS ? "project-cta ios" : "project-cta";
      const ctaText = isIOS
        ? 'Download for iOS <i class="fab fa-apple" style="font-size: 2rem"></i>'
        : "View Project &rarr;";

      return `
        <div class="project-card">
          <div class="project-header">
            <span class="project-name">${project.name}</span>
            <span class="project-tech">${project.tech}</span>
          </div>
          <span class="body-text">
            ${project.description}
          </span>
          <a href="${project.link}" target="_blank" class="${ctaClass}">
            ${ctaText}
          </a>
        </div>
      `;
    }).join("");
  } catch (error) {
    console.error("Error loading projects:", error);
  }
}

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", loadProjects);
