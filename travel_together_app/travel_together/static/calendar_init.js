//referenced ClaudeAI for support creating event listener for calendar, allowing users to click onto calendar to add events/meetups
document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");

  if (calendarEl) {
    const options = {
      initialView: "dayGridMonth",
      events: [
        { title: "Trip Start", date: initialDateValue },
        { title: "Example Event", date: "2025-12-05" }
      ],
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,dayGridWeek,dayGridDay'
      }
    };
    
    if (typeof initialDateValue !== 'undefined' && initialDateValue) {
      options.initialDate = initialDateValue;
    }

    const calendar = new FullCalendar.Calendar(calendarEl, options);
    calendar.render();
    console.log("FullCalendar initialized successfully from external file.");
  }
});