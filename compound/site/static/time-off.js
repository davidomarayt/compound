(() => {
  const need = document.getElementById('rest-need');
  const time = document.getElementById('rest-time');
  const title = document.getElementById('rest-result-title');
  const text = document.getElementById('rest-result-text');
  if (!need || !time || !title || !text) return;
  const ideas = {
    quiet: {
      5: ['A quieter few minutes', 'Find a comfortable spot and pause without adding a task. Quiet or familiar music are both options; choose whichever feels easier.'],
      20: ['Keep it undemanding', 'Put on familiar music, read something easy or simply sit comfortably. You do not have to fill the whole twenty minutes.'],
      60: ['An unhurried patch of time', 'Leave some of the hour unplanned. Choose a familiar programme, a book or quiet company, with permission to change your mind.']
    },
    distance: {
      5: ['Leave tomorrow a note', 'If unfinished work is on your mind, write one next action and when you will return to it. Put the note aside; this is not a new to-do list.'],
      20: ['Change the subject', 'Choose something unrelated to work: a short story, music or a chat about something else. Silence work alerts only if you are not expected to be available.'],
      60: ['Make a little space from work', 'Within your agreed availability, put work messages aside and choose an activity that holds your interest. Keep any necessary urgent contact route open.']
    },
    different: {
      5: ['A small change of scene', 'Try a few lines of drawing or listen closely to one unfamiliar song. Curiosity is enough; there is nothing to finish.'],
      20: ['Try, without committing', 'Explore a simple puzzle, sketch an object or practise a few words in another language. Stop if it starts to feel like another assignment.'],
      60: ['Follow a little curiosity', 'Spend some time on an activity you already have the materials for. A library book, sketch or piece of music is enough; no purchase or progress goal is needed.']
    },
    choice: {
      5: ['One choice that is yours', 'Choose where to sit, what to listen to or whether to have quiet. Keep the choice small enough to fit around what cannot wait.'],
      20: ['Keep a small gap unclaimed', 'If circumstances allow, reserve this gap before adding chores. Decide in the moment what you would like to do, including doing very little.'],
      60: ['An hour with some say in it', 'If responsibilities permit, leave this hour free of a preset plan. Where useful, agree a specific handover with someone first; needing that support is not a failure.']
    }
  };
  const update = () => {
    const idea = ideas[need.value]?.[time.value];
    if (!idea) return;
    title.textContent = idea[0]; text.textContent = idea[1];
  };
  need.addEventListener('change', update); time.addEventListener('change', update); update();
})();
