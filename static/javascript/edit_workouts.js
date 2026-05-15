const backdrop = document.getElementById('modalBackdrop');
const form     = document.getElementById('modalForm');
const title    = document.getElementById('modalTitle');
const planId   = document.getElementById('modalPlanId');
const submit   = document.getElementById('modalSubmit');
const createUrl      = document.getElementById('modalSubmit').dataset.url;

function openCreate() {
  title.textContent = 'Create Plan';
  form.action = createUrl;
  planId.value = '';
  document.getElementById('planName').value = '';
  document.getElementById('planDesc').value = '';
  submit.textContent = 'Create';
  backdrop.classList.add('open');
}

function openEdit(id, name, description) {
    title.textContent = 'Edit Plan';
    form.action = `/workouts/plan/${id}/edit/`;
    planId.value = id;
    document.getElementById('planName').value = name;
    document.getElementById('planDesc').value = description;
    submit.textContent = 'Save';
    backdrop.classList.add('open');
}

function openDelete(id, name) {
    if (confirm(`Delete "${name}"? This cannot be undone.`)) {
      fetch(`/workouts/plan/${id}/delete/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}' },
      }).then(() => location.reload());
}
}

function closeModal() {
    backdrop.classList.remove('open');
}

backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) closeModal();
});