//referenced ClaudeAI for support creating event listener for calendar, allowing users to click onto calendar to add events/meetups
document.addEventListener("DOMContentLoaded", function () {
  const calendarElement = document.getElementById("calendar");
  var trip_readonly = $('#calendar').data("readonly");

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
        console.log(trip_readonly);
        if(trip_readonly == "False") {
          showMeetupArea(info.date);
        }
      },


      eventClick: function(info) {
        const popup = document.getElementById("existing-meetup-popup");

        document.getElementById("detail-location").textContent = info.event.title;
        document.getElementById("detail-start").textContent = info.event.start;
        document.getElementById("detail-description").textContent = info.event.extendedProps.description || "None";

        const eventLink = document.getElementById("detail-link");
        const openLinkButton = document.getElementById("open-link");
        
        //if link exists, show it and make it link to source, else do not show and remove link functionality
        if(info.event.extendedProps.link) {
          eventLink.textContent = info.event.extendedProps.link;
          eventLink.href = info.event.extendedProps.link;
          openLinkButton.style.display = "inline-block";
        } else {
          eventLink.textContent = "No Link";
          eventLink.removeAttribute("href");
          openLinkButton.style.display = "none";
        }

        popup.style.display = "flex";

        //open link on click
        openLinkButton.onclick = function() {
          window.open(info.event.extendedProps.link, "_blank");
        }

        //make delete event button work
        document.getElementById("delete-event").onclick = function() {
          if (!confirm("Deleting an event is final. Please confirm that you want to delete the event.")) return;

          fetch('/trip/' + tripId + '/meetups/' + info.event.id, {
            method: 'DELETE'
          })
          .then(r => r.json())
          .then(data => {
            if (data.success) {
              info.event.remove();
              alert("Meetup successfully deleted.");
              popup.style.display = "none";
            }
          })
        }

        //make event close from button
        document.getElementById("close-event").onclick = function() {
          popup.style.display = "none"
        }

        //make event close from clicking elsewhere on screen
        popup.onclick = function(e) {
          if (e.target === popup) popup.style.display = "none";
        };
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

  //fixing the timezone offset, otherwise meetups will schedule for one day earlier than you clicked
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());

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

  //Listener to close the meetup area when the background is clicked
  document.getElementById('meetup-area').addEventListener('click', function(e){
    if(e.target === this) {
      closeMeetupArea();
    }
  });

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
    });
  });
}