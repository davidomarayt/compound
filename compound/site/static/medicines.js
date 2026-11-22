const medicineSearch = document.querySelector('.medicines-search');
const medicineQuery = medicineSearch.querySelector('input');
const medicineGuides = [...document.querySelectorAll('[data-medicine-guide]')];
const medicineGroups = [...document.querySelectorAll('[data-medicine-group]')];
const medicineCount = document.querySelector('[data-medicine-count]');
const medicineEmpty = document.querySelector('.medicines-empty');

function filterMedicines() {
  const words = medicineQuery.value.trim().toLowerCase().split(/\s+/);
  let visibleCount = 0;
  for (const guide of medicineGuides) {
    const searchableText = guide.dataset.search.toLowerCase();
    const matches = words.every(word => searchableText.includes(word));
    guide.hidden = !matches;
    if (matches) visibleCount += 1;
  }
  for (const group of medicineGroups) {
    group.hidden = !group.querySelector('[data-medicine-guide]:not([hidden])');
  }
  medicineCount.textContent = `${visibleCount} ${visibleCount === 1 ? 'guide' : 'guides'}`;
  medicineEmpty.hidden = visibleCount !== 0;
}

medicineQuery.addEventListener('input', filterMedicines);
medicineSearch.addEventListener('submit', event => event.preventDefault());
medicineEmpty.querySelector('button').addEventListener('click', () => {
  medicineQuery.value = '';
  filterMedicines();
  medicineQuery.focus();
});
filterMedicines();
medicineSearch.hidden = false;
