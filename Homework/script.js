var domain = ''; //change it to your domain
var hwapiDomain = `hwapi.${domain}`; //change it to localhost:8000 if testing on local
var HomeworkApiLink = `https://${hwapiDomain}/items/all`; //might need to change to http if testing on local

function getTodayDate() {
  const now = new Date();
  const utc8Offset = 8 * 60; // 8 hours in minutes
  const utc8Date = new Date(now.getTime() + utc8Offset * 60 * 1000);
  const dateString = utc8Date.toISOString().split('T')[0];
  console.log('getTodayDateUTC8:', dateString); // Log UTC+8 date
  return dateString;
}

function getNearestFutureDate(items) {
  const today = getTodayDate();
  const futureDates = [...new Set(
    items
      .map(item => item.DueDate)
      .filter(date => date && date >= today)
  )];
  futureDates.sort();
  return futureDates[0] || null;
}

function fetchHomework(jsonFile) {
  fetch(jsonFile)
    .then(response => {
      if (!response.ok) throw new Error("Couldn't load JSON file");
      return response.json();
    })
    .then(async data => {
      const params = new URLSearchParams(window.location.search);
      let dateParam = params.get('date');

      // ⛑️ Guard against missing param and avoid redirect loop
      if (!dateParam) {
        const newParams = new URLSearchParams({ date: 'ALL' });
        window.location.href = window.location.pathname + '?' + newParams.toString();
        return;
      }

      // 🧠 Filter based on param
      const filteredData = dateParam === 'ALL'
        ? data
        : data.filter(item => item.DueDate === dateParam);

      await renderHomework(filteredData);

      // 🎯 Scroll to today if homework exists, else next upcoming
      if (dateParam === 'ALL') {
        const today = getTodayDate();
        const hasTodayHomework = data.some(item => item.DueDate === today);

        let targetDate;
        if (hasTodayHomework) {
          targetDate = today;
        } else {
          targetDate = getNearestFutureDate(data);
        }

        if (targetDate) {
          const targetId = `day-${targetDate.replace(/-/g, '')}`;
          const targetBlock = document.getElementById(targetId);
          if (targetBlock) {
            targetBlock.scrollIntoView({ behavior: 'smooth' });
          }
        }
      }
    })
    .catch(error => {
      console.error("Fetch error:", error);
      document.getElementById('homework').innerText = "Error loading homework data.";
    });
}

// Helper to get/set calendar info in localStorage
function getCachedCalendar(date) {
  const key = `calendar_${date}`;
  const cached = localStorage.getItem(key);
  if (!cached) return null;
  try {
    return JSON.parse(cached);
  } catch {
    return cached;
  }
}
function setCachedCalendar(date, data) {
  const key = `calendar_${date}`;
  localStorage.setItem(key, JSON.stringify(data));
}

async function renderHomework(items) {
  const container = document.getElementById('homework');
  container.innerHTML = '';

  if (!Array.isArray(items) || items.length === 0) {
    container.innerHTML = '<p>No homework found 💤</p>';
    return;
  }

  const validItems = items.filter(item => item.DueDate && item.Subject && item.Homework);

  // 🔢 Sort items by DueDate ascending
  validItems.sort((a, b) => new Date(a.DueDate) - new Date(b.DueDate));

  // 👨‍🏫 Group items by date and subject
  const grouped = {};
  validItems.forEach(item => {
    const { DueDate, Subject } = item;
    if (!grouped[DueDate]) grouped[DueDate] = {};
    if (!grouped[DueDate][Subject]) grouped[DueDate][Subject] = [];
    grouped[DueDate][Subject].push(item);
  });

  // 📅 Render grouped homework (without calendar info)
  for (const [dueDate, subjects] of Object.entries(grouped)) {
    const dateBlock = document.createElement('div');
    const blockId = `day-${dueDate.replace(/-/g, '')}`;
    dateBlock.id = blockId;

    // Calendar placeholder
    const header = document.createElement('h3');
    header.textContent = `Due: ${dueDate} - Loading...`;
    header.classList.add('clickable-date');
    header.style.cursor = 'pointer';
    header.addEventListener('click', () => {
      window.location.href = `?date=${dueDate}`;
    });
    dateBlock.appendChild(header);

    for (const [subject, entries] of Object.entries(subjects)) {
      const subjectBlock = document.createElement('div');
      subjectBlock.innerHTML = `<h4>${subject}</h4>`;
      const ul = document.createElement('ul');

      entries.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `
          ${item.Homework}<br>
          ${item.CreatedAt ? `<p id="ExInfo">ID: ${item.id} Created: ${item.CreatedAt}</p>` : ''}
          ${item.LastUpdate ? `<span class="watermark">Last Update: ${item.LastUpdate}</span>` : ''}
        `;
        ul.appendChild(li);
      });

      subjectBlock.appendChild(ul);
      dateBlock.appendChild(subjectBlock);
    }

    container.appendChild(dateBlock);

    // 🗓️ Check localStorage before fetching calendar info
    const cached = getCachedCalendar(dueDate);
    if (cached) {
      let calendarText = 'Holiday';
      if (Array.isArray(cached) && cached.length > 0) {
        calendarText = cached.join(', ');
      } else if (typeof cached === 'string') {
        calendarText = cached;
      }
      header.textContent = `Due: ${dueDate} - ${calendarText}`;
    } else {
      fetchCalendar(`${HomeworkApiLink}/calendar/${dueDate}`)
        .then(calendarRaw => {
          let calendarArr;
          try {
            calendarArr = JSON.parse(calendarRaw);
          } catch {
            calendarArr = [calendarRaw];
          }
          setCachedCalendar(dueDate, calendarArr);
          let calendarText = 'Holiday';
          if (Array.isArray(calendarArr) && calendarArr.length > 0) {
            calendarText = calendarArr.join(', ');
          } else if (typeof calendarRaw === 'string') {
            calendarText = calendarRaw;
          }
          header.textContent = `Due: ${dueDate} - ${calendarText}`;
        })
        .catch(() => {
          header.textContent = `Due: ${dueDate} - Holiday`;
        });
    }
  }
}

// Hook up the date form
function setupDateForm() {
  const form = document.getElementById('date-form');
  const input = document.getElementById('date');

  if (!form || !input) return;

  form.addEventListener('submit', event => {
    event.preventDefault();
    const selectedDate = input.value;
    if (!selectedDate) return;
    window.location.href = `?date=${selectedDate}`;
  });
}

function fetchCalendar(url) {
  return fetch(url)
    .then(response => {
      if (!response.ok) throw new Error("Couldn't load file");
      return response.text();
    });
}
document.addEventListener('DOMContentLoaded', () => {
  fetchHomework(`${HomeworkApiLink}`);
  setupDateForm();
});
