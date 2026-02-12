const projects = Array.from({ length: 16 }, (_, i) => ({
  title: `Project ${i + 1}`,
  description: 'Showcase item built with performance and accessibility in mind.',
  link: `/projects/project-${i + 1}.html`,
}));

const perPage = 8;
let currentPage = 1;
const totalPages = Math.ceil(projects.length / perPage);

const grid = document.getElementById('project-grid');
const indicator = document.getElementById('page-indicator');
const prev = document.getElementById('prev-page');
const next = document.getElementById('next-page');

function renderPage() {
  const start = (currentPage - 1) * perPage;
  const pageProjects = projects.slice(start, start + perPage);
  grid.innerHTML = pageProjects.map((project) => `
    <article class="project-card">
      <h3>${project.title}</h3>
      <p>${project.description}</p>
      <a href="${project.link}">View project</a>
    </article>
  `).join('');

  indicator.textContent = `Page ${currentPage} of ${totalPages}`;
  prev.disabled = currentPage === 1;
  next.disabled = currentPage === totalPages;
}

prev.addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage -= 1;
    renderPage();
  }
});

next.addEventListener('click', () => {
  if (currentPage < totalPages) {
    currentPage += 1;
    renderPage();
  }
});

renderPage();
