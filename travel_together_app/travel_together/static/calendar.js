//referenced ClaudeAI for support creating event listener for calendar, allowing users to click onto calendar to add events/meetups
document.addEventListener("DOMContentLoaded", function () {
  const calendarElement = document.getElementById("calendar");

  if (calendarElement) {
    const options = {
      initialView: "dayGridMonth",
      editable: true,
      selectable: true,
      events: '/trip/' + tripId + '/meetups',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,dayGridWeek,dayGridDay'
      },

      //calls the event listener so that the meetup area shows when the user clicks a date
      dateClick: function(info) {
        showMeetupArea(info.date)
      },

      eventClick: function(info) {
        let message = 'Location: ' + info.event.title + '\n';
        if (info.event.extendedProps.description) {
          message += 'Description: ' + info.event.extendedProps.description + '\n';
        }

        if (info.event.extendedProps.link) {
          actions += "\n\nPress OK to open "
          message += 'Link: ' + info.event.extendedProps.link + '\n';
          
          if(confirm(message)) {
            window.open(info.event.extendedProps.link, '_blank');
          } else if (confirm('Delete this meetup?')) {
            fetch('/trip/' + tripId + '/meetups/' + info.event.id, {
              method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
              if (data.success) {
                info.event.remove();
                alert('Meetup deleted!');
              }
            });
          } else {
            if (confirm(message + '\n\nDelete this meetup?')) {
              fetch('/trip' + tripId + '/meetups/' + info.event.id, {
                method: 'DELETE'
              })
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  info.event.remove();
                  alert('Meetup deleted!');
                }
              });
            }
          }
        }
      } 
    };

    
    if (typeof initialDateValue !== 'undefined' && initialDateValue) {
      options.initialDate = initialDateValue;
    }

    const calendar = new FullCalendar.Calendar(calendarElement, options);
    calendar.render();
    console.log("FullCalendar initialized successfully from external file.");

    window.tripCalendar = calendar;

    setupMeetupArea();
  }
});

function showMeetupArea(date){
  const meetupArea = document.getElementById('meetup-area');
  const dateInput = document.getElementById('meetup-date');

  const formattedDate = date.toISOString().split('T')[0];

  dateInput.value = formattedDate;
  meetupArea.style.display = 'flex';
}

function closeMeetupArea(){
  const meetupArea = document.getElementById('meetup-area');
  meetupArea.style.display = 'none';
  document.getElementById('meetup-form').reset();
}

function setupMeetupArea(){
  //Listener to close the meetup area when the cancel button is clicked
  document.getElementById('cancel-meetup-creation-button').addEventListener('click', closeMeetupArea);
  //Listner to close the meetup area when the background is clicked
  document.getElementById('meetup-area').addEventListener('click', function(e){
    if(e.target === this) {
      closeMeetupArea();
    }
  })

  //Listener to submit the meetup form
  document.getElementById('meetup-form').addEventListener('submit', function(e){
    e.preventDefault();

    const formData = new FormData(this);
    const data = {
      location: formData.get('location'),
      date: formData.get('date'),
      time: formData.get('time'),
      description: formData.get('description') || null,
      link: formData.get('link') || null
    };
    //assisted by ClaudeAI
    fetch('/trip/' + tripId + '/meetups',{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
      window.tripCalendar.refetchEvents();
      closeMeetupArea();
      alert('Meetup created!');
    } else {
      alert('Error creating meetup: ' + (data.error || 'Unknown error'));
    }
  })
  .catch(error => {
    alert('Error: ' + error);
  })
  })
}