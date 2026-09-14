(() => {
  const root = document.getElementById('compound-hobby-picker');
  if (!root) return;
  const time = root.querySelector('#hobby-time');
  const budget = root.querySelector('#hobby-budget');
  const company = root.querySelector('#hobby-company');
  const result = root.querySelector('#hobby-results');
  const ideas = [
    {title:'Try a little drawing',text:'Pick an everyday object and sketch it with a pen and scrap paper. Stop whenever you like.',time:15,budget:0,company:'solo'},
    {title:'Follow your curiosity',text:'Read a few pages of a book you already have, purely because it interests you.',time:15,budget:0,company:'solo'},
    {title:'Take a photo wander',text:'Use your phone to look for interesting colours or textures on a short, familiar route. An indoor version works too.',time:30,budget:0,company:'solo'},
    {title:'Make a tiny collage',text:'Arrange scraps of old packaging or magazines into a picture. Use materials you already have.',time:30,budget:0,company:'solo'},
    {title:'Get lost in a story',text:'Settle in with a borrowed novel, comic or audiobook. There is no reading target to reach.',time:60,budget:0,company:'solo'},
    {title:'Try a simple paper craft',text:'Consider a small pack of coloured paper, within your allowance. Fold, cut or make a card using tools you already own.',time:30,budget:10,company:'solo'},
    {title:'Experiment with watercolour',text:'Look for a basic paint set and paper within your allowance. Paint shapes and colour patches before worrying about a finished picture.',time:60,budget:25,company:'solo'},
    {title:'Draw each other',text:'Invite someone to try a quick portrait with pens and scrap paper. No artistic credentials needed.',time:15,budget:0,company:'together'},
    {title:'Swap a favourite song',text:'Take turns choosing a song and saying what you like about it. Use music you already have access to.',time:15,budget:0,company:'together'},
    {title:'Bring out the cards',text:'Use a pack you already have and play a familiar game together, or learn one simple new game.',time:30,budget:0,company:'together'},
    {title:'Walk and notice',text:'Pick a familiar route and look for something neither of you has noticed before. Choose a seated or indoor version if that suits you better.',time:30,budget:0,company:'together'},
    {title:'Share a reading hour',text:'Bring your own books, read for a while, then chat about what caught your attention.',time:60,budget:0,company:'together'},
    {title:'Make postcards together',text:'Choose paper or card within your allowance. Use pens you already own to draw a place you remember.',time:30,budget:10,company:'together'},
    {title:'Try a small craft afternoon',text:'Choose one simple craft and a shared set of materials within your allowance. Check the full cost before buying anything.',time:60,budget:25,company:'together'}
  ];
  function update() {
    const matches = ideas.filter(i => i.time <= Number(time.value) && i.budget <= Number(budget.value) && i.company === company.value)
      .sort((a,b) => b.time-a.time || b.budget-a.budget).slice(0,2);
    result.replaceChildren();
    for (const idea of matches) {
      const heading = document.createElement('h3'); heading.textContent = idea.title;
      const description = document.createElement('p'); description.textContent = idea.text;
      result.append(heading,description);
    }
  }
  [time,budget,company].forEach(input => input.addEventListener('change',update));
  update();
})();
