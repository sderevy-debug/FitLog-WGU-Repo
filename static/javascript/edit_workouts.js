const backdrop = document.getElementById('modalBackdrop');
const form     = document.getElementById('modalForm');
const title    = document.getElementById('modalTitle');
const planId   = document.getElementById('modalPlanId');
const submit   = document.getElementById('modalSubmit');
const workoutBackdrop = document.getElementById('workoutModalBackdrop');
const createUrl      = document.getElementById('modalSubmit').dataset.url;

function openCreate() {
  title.textContent = 'Create Plan';
  form.action = createUrl;
  planId.value = '';
  document.getElementById('planName').value = '';
  document.getElementById('planTimesPerWeek').value = 0;
  document.getElementById('planDesc').value = '';
  submit.textContent = 'Create';
  backdrop.classList.add('open');
}

function openWorkoutModal(planId) {
  document.getElementById('workoutPlanId').value = planId;
  document.getElementById('workoutId').value = '';
  document.getElementById('workoutName').value = '';
  document.getElementById('workoutGoal').value = '';
  document.querySelector('#workoutModalBackdrop .modal__title').textContent = 'Add Workout';
  form.action = document.getElementById('addWorkout').dataset.createUrl;
  const tbody = document.getElementById('exerciseRows');
  tbody.innerHTML = '';
  addExerciseRow();
  addExerciseRow();
  addExerciseRow();
  workoutBackdrop.classList.add('open');
  document.getElementById('deleteWorkoutBtn').style.display = 'none';
  workoutBackdrop.classList.add('open');
}

function openWorkoutEdit(dataset) {
  document.getElementById('workoutPlanId').value = dataset.planId;
  document.getElementById('workoutId').value = dataset.workoutId;
  document.getElementById('workoutName').value = dataset.workoutName;
  document.getElementById('workoutGoal').value = dataset.workoutGoal;
  document.querySelector('#workoutModalBackdrop .modal__title').textContent = 'Edit Workout';
  document.getElementById('workoutForm').action = `/workout_edit/${dataset.workoutId}/`;

  const tbody = document.getElementById('exerciseRows');
  tbody.innerHTML = '';

  fetch(`/workout_exercises/${dataset.workoutId}/`)
    .then(r => r.json())
    .then(exercises => {
      if (exercises.length === 0) {
        addExerciseRow();
        addExerciseRow();
        addExerciseRow();
      } else {
        exercises.forEach(ex => addExerciseRow(ex));
      }
    });

  workoutBackdrop.classList.add('open');
  document.getElementById('deleteWorkoutBtn').style.display = 'inline-flex';
  workoutBackdrop.classList.add('open');
}

function addExerciseRow(ex = {}) {
  const tbody = document.getElementById('exerciseRows');
  const row = document.createElement('tr');
  row.innerHTML = `
    <td><input class="exercise-input" type="text"   name="exercise_name[]"      value="${ex.name || ''}"      placeholder="e.g. Squat" /></td>
    <td><input class="exercise-input" type="number" name="exercise_weight[]"     value="${ex.weight || ''}"    placeholder="kg" min="0" /></td>
    <td><input class="exercise-input" type="number" name="exercise_reps[]"       value="${ex.repetitions || ''}" placeholder="reps" min="0" /></td>
    <td><input class="exercise-input" type="number" name="exercise_sets[]"       value="${ex.sets || ''}" placeholder="3"/></td>
    <td><input class="exercise-input" type="text" name="exercise_rest[]" value="${ex.rest_time || '0:00'}" placeholder="0:00" maxlength="5" style="width:70px;" /></td>
    <td>
      <select class="exercise-input" name="exercise_intensity[]">
        <option value="LO" ${ex.intensity === 'LO' ? 'selected' : ''}>Light</option>
        <option value="ME" ${ex.intensity === 'ME' || !ex.intensity ? 'selected' : ''}>Moderate</option>
        <option value="HI" ${ex.intensity === 'HI' ? 'selected' : ''}>Vigorous</option>
        <option value="EX" ${ex.intensity === 'EX' ? 'selected' : ''}>Deadly</option>
      </select>
    </td>
    <td><button type="button" class="row-delete" onclick="this.closest('tr').remove()">✕</button></td>
  `;
  tbody.appendChild(row);
}

function deleteWorkout() {
  const workoutId = document.getElementById('workoutId').value;
  if (!confirm('Delete this workout and all its exercises? This cannot be undone.')) return;
  fetch(`/workout_delete/${workoutId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') },
  }).then(() => location.reload());
}

function getCookie(name) {
  return document.cookie.split(';')
    .map(c => c.trim())
    .find(c => c.startsWith(name + '='))
    ?.split('=')[1];
}

function handleImport(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    fetch('/workouts/import/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: e.target.result,
    }).then(r => r.json())
      .then(data => {
        if (data.success) location.reload();
        else alert('Import failed: ' + data.error);
      });
  };
  reader.readAsText(file);
}

function closeModal() {
    backdrop.classList.remove('open');
    workoutBackdrop.classList.remove('open')
}

backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) closeModal();
});

workoutBackdrop.addEventListener('click', e => {
  if (e.target === workoutBackdrop) closeModal();
});