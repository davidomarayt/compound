/* All measurements stay in this page. No network requests or persistent storage. */
(() => {
  'use strict';
  const get = id => document.getElementById('bmi-' + id);
  const form = get('form');
  if (!form) return;
  const num = id => get(id).value.trim() === '' ? NaN : Number(get(id).value);
  const unit = name => form.querySelector(`input[name="${name}-unit"]:checked`).value;
  const near = (n, boundary) => Math.abs(n - boundary) < 1e-10;
  const below = (n, boundary) => n < boundary && !near(n, boundary);
  const readHeight = () => unit('height') === 'cm' ? num('cm') : (num('ft') * 12 + num('inch')) * 2.54;
  const readWeight = () => unit('weight') === 'kg' ? num('kg') : (num('st') * 14 + num('lb')) * .45359237;
  let lastHeightUnit = 'cm', lastWeightUnit = 'kg', lastWaistUnit = 'cm';
  let announcementTimer;
  function announce(message) { clearTimeout(announcementTimer); announcementTimer = setTimeout(() => { get('announcement').textContent = message; }, 500); }
  function resetResult(message) {
    get('output').hidden = true; get('empty').hidden = false;
    get('empty-message').textContent = message; announce(message);
  }
  function render(explicit = false) {
    get('error').textContent = '';
    const suitability = get('suitability').value;
    if (suitability !== 'adult' && suitability !== 'older') {
      resetResult(suitability === 'excluded' ? 'This adult calculator is not suitable for you. Your GP or relevant care team can help you choose an appropriate assessment. You can still read the guidance below.' : 'Choose who this is for, then enter your height and weight to see your result.');
      if (explicit && !suitability) get('error').textContent = 'Please choose who this calculator is for.';
      return;
    }
    const height = readHeight(), weight = readWeight();
    const imperialHeightValid = unit('height') === 'cm' || (Number.isInteger(num('ft')) && num('inch') >= 0 && num('inch') < 12);
    const imperialWeightValid = unit('weight') === 'kg' || (Number.isInteger(num('st')) && num('st') >= 0 && num('lb') >= 0 && num('lb') < 14);
    if (!Number.isFinite(height) || !Number.isFinite(weight) || height < 100 || height > 250 || weight < 20 || weight > 500 || !imperialHeightValid || !imperialWeightValid) {
      resetResult('Enter a height from 100 to 250 cm and a weight from 20 to 500 kg (or equivalent). These are this tool’s input limits, not healthy ranges.');
      if (explicit || (Number.isFinite(height) && Number.isFinite(weight))) get('error').textContent = 'Check your measurements. Use whole feet/stones, inches from 0 to below 12, and pounds from 0 to below 14. Enter 0 for an unused inches or pounds field.';
      return;
    }
    const bmi = weight / (height / 100) ** 2;
    const lower = get('background').value === 'lower';
    const cuts = lower ? [18.5, 23, 27.5] : [18.5, 25, 30];
    const category = below(bmi, cuts[0]) ? 0 : below(bmi, cuts[1]) ? 1 : below(bmi, cuts[2]) ? 2 : 3;
    const labels = ['Underweight range', 'Healthy weight range', 'Overweight range', 'Obesity range'];
    get('value').textContent = bmi.toFixed(1);
    get('category').textContent = labels[category];
    get('precision').textContent = `BMI before display rounding: ${bmi.toFixed(3)}. Categories use the unrounded calculation.`;
    get('thresholds').textContent = `Underweight: below 18.5 · Healthy weight: 18.5 to below ${cuts[1]} · Overweight: ${cuts[1]} to below ${cuts[2]} · Obesity: ${cuts[2]}+. ${lower ? 'Lower ethnicity-related thresholds selected.' : 'Standard adult thresholds selected; some ethnic backgrounds need lower thresholds.'}`;
    get('interpretation').textContent = [
      'Consider discussing your weight and nutrition with your GP, especially if your weight has fallen without trying. This screening result needs personal context.',
      'This is within the selected BMI reference range. It does not rule out health problems: BMI cannot distinguish fat from muscle or show where fat is carried.',
      'This is above the selected healthy-weight reference range. Your GP can put it in context with your waist measurement, health history and other checks.',
      'This falls within the selected obesity screening range. A diagnosis requires a fuller assessment. Your GP can discuss your health and support options with you.'
    ][category];
    const hM=height/100, refLow=18.5*hM*hM, refHigh=cuts[1]*hM*hM;
    get('reference-weight').textContent = `${refLow.toFixed(1)} kg to below ${refHigh.toFixed(1)} kg at your entered height, based only on the selected BMI reference thresholds.`;
    get('older').hidden = suitability !== 'older';
    const position = Math.min(100, Math.max(0, (bmi - 12) / 33 * 100));
    get('marker').style.left = `${position}%`;
    const bounds = [12, ...cuts, 45], colours = ['#88b8d2', '#abd0a8', '#e2bc78', '#d38e8c'];
    get('segments').replaceChildren(...colours.map((colour, i) => {
      const span = document.createElement('span'); span.style.flex = String(bounds[i + 1] - bounds[i]); span.style.background = colour; return span;
    }));
    const waist = num('waist') * (get('waist-unit').value === 'in' ? 2.54 : 1);
    let waistText = 'Add your waist measurement to explore this alongside BMI.';
    if (!below(bmi, 35)) waistText = 'Waist-to-height interpretation is not shown at BMI 35 or above. HSE recommends this additional check for adults with BMI below 35. Discuss your overall risk with your GP. [1]';
    else if (get('waist').value.trim() !== '') {
      if (!Number.isFinite(waist) || waist < 30 || waist > 300) {
        waistText = 'Check your waist measurement and units. This tool accepts 30–300 cm (or equivalent). Your BMI above is unchanged.';
      } else {
        const ratio = waist / height;
        const waistClass = ratio < .4 ? 'below the NICE central-adiposity reference range' : ratio < .5 ? 'within the NICE healthy central-adiposity range (0.40–0.49)' : ratio < .6 ? 'within the NICE increased central-adiposity range (0.50–0.59)' : 'within the NICE high central-adiposity range (0.60+)';
        waistText = `Your ratio is ${ratio.toFixed(3)}, ${waistClass}. Waist-to-height ratio is still a screening measure, not a diagnosis. [1, 2]`;
      }
    }
    get('waist-result').textContent = waistText;
    get('empty').hidden = true; get('output').hidden = false;
    announce(`BMI ${bmi.toFixed(1)}. ${labels[category]}. ${waistText}`);
  }
  function switchUnits() {
    const heightUnit = unit('height'), weightUnit = unit('weight');
    if (heightUnit !== lastHeightUnit) {
      const cm = lastHeightUnit === 'cm' ? num('cm') : (num('ft') * 12 + num('inch')) * 2.54;
      if (Number.isFinite(cm) && cm >= 100 && cm <= 250) {
        if (heightUnit === 'cm') get('cm').value = Number(cm.toFixed(6));
        else { const inches = Number((cm / 2.54).toFixed(6)); get('ft').value = Math.floor(inches / 12); get('inch').value = Number((inches % 12).toFixed(6)); }
      } else { get('cm').value = ''; get('ft').value = ''; get('inch').value = ''; }
      lastHeightUnit = heightUnit;
    }
    if (weightUnit !== lastWeightUnit) {
      const kg = lastWeightUnit === 'kg' ? num('kg') : (num('st') * 14 + num('lb')) * .45359237;
      if (Number.isFinite(kg) && kg >= 20 && kg <= 500) {
        if (weightUnit === 'kg') get('kg').value = Number(kg.toFixed(6));
        else { const pounds = Number((kg / .45359237).toFixed(6)); get('st').value = Math.floor(pounds / 14); get('lb').value = Number((pounds % 14).toFixed(6)); }
      } else { get('kg').value = ''; get('st').value = ''; get('lb').value = ''; }
      lastWeightUnit = weightUnit;
    }
    get('height-metric').hidden = heightUnit !== 'cm'; get('height-imperial').hidden = heightUnit === 'cm';
    get('weight-metric').hidden = weightUnit !== 'kg'; get('weight-imperial').hidden = weightUnit === 'kg';
    const waistUnit = get('waist-unit').value;
    if (waistUnit !== lastWaistUnit) {
      const value = num('waist');
      if (Number.isFinite(value)) get('waist').value = Number((value * (waistUnit === 'in' ? 1 / 2.54 : 2.54)).toFixed(6));
      lastWaistUnit = waistUnit;
    }
    get('waist-label').textContent = waistUnit === 'cm' ? '(cm)' : '(inches)';
  }
  form.addEventListener('submit', event => { event.preventDefault(); render(true); if (!get('output').hidden) get('result').focus(); });
  form.addEventListener('input', () => { switchUnits(); render(); });
  form.addEventListener('change', () => { switchUnits(); render(); });
  form.addEventListener('reset', () => { setTimeout(() => { lastHeightUnit = 'cm'; lastWeightUnit = 'kg'; lastWaistUnit = 'cm'; switchUnits(); get('waist').closest('details').open = false; render(); }, 0); });
  render();
})();
