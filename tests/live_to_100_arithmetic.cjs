// Pure arithmetic tests; these do not replace browser interaction or visual QA.
const assert = require('node:assert/strict');
const { yearsTo100 } = require('../compound/site/static/live-to-100.js');
for (const [input, result] of [['30', 70], ['65', 35], ['18', 82], ['100', 0], ['99', 1], ['80', 20]]) {
  assert.equal(yearsTo100(input), result, input);
}
for (const input of ['', ' ', '17', '101', '-1', '30.5', 'abc', 'Infinity', '1e2', '0x64']) {
  assert.equal(yearsTo100(input), null, JSON.stringify(input));
}
// A retirement example remains independent of a selected current age.
assert.deepEqual(['80', '65'].map(yearsTo100), [20, 35]);
console.log('17 arithmetic and validation checks passed.');
