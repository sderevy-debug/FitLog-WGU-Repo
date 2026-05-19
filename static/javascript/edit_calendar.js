const assignBackdrop = document.getElementById('assignModalBackdrop');

function openAssignModal(dataset) {
  document.getElementById('assignDate').value = dataset.date;
  document.getElementById('assignModalTitle').textContent = `Assign Workout — ${dataset.date}`;

  const list = document.getElementById('assignedList');
  list.innerHTML = '';

  if (dataset.dayWorkouts) {
    fetch(`/calendar/day_workouts/?date=${dataset.date}`)
      .then(r => r.json())
      .then(workouts => {
        workouts.forEach(w => addAssignedItem(w.id, w.name, dataset.date));
      });
  }

  assignBackdrop.classList.add('open');
}

function closeAssignModal() {
  assignBackdrop.classList.remove('open');
}

function addAssignedItem(id, name, date) {
  const list = document.getElementById('assignedList');
  const item = document.createElement('div');
  item.className = 'assigned-item';
  item.innerHTML = `
    <span>${name}</span>
    <button type="button" class="assigned-item__remove"
            onclick="removeAssignment(${id}, '${date}', this)">✕</button>
  `;
  list.appendChild(item);
}

function removeAssignment(dayWorkoutId, date, btn) {
  if (!confirm('Remove this workout from the day?')) return;
  fetch(`/calendar/remove_workout/${dayWorkoutId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') },
  }).then(() => {
    btn.closest('.assigned-item').remove();
    location.reload();
  });
}

assignBackdrop.addEventListener('click', e => {
  if (e.target === assignBackdrop) closeAssignModal();
});