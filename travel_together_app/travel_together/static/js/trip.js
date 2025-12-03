//Creating event listeners to allow users to create new forum topics on the trip message board
//referenced Claude AI (Sonnet 4.5) to for parts of the event listener logic below
//referenced ChatGpt for the messageForm function, preventing the app from breaking when the 'add forum' button is clicked but input is left null
$(document).ready(function() {
    const newTopicButton = document.getElementById('new-topic-button');
    const newTopicInput = document.getElementById('new-forum-topic-input');
    const forumTopicInput = document.getElementById('forum-topic-input');
    const cancelButton = document.getElementById('cancel-new-forum-topic');
    const newTopic = document.querySelector('input[name="new_forum_topic"]');
    const messageForm = document.querySelector("form[action$='/message']");

    if (newTopicButton) {
        newTopicButton.addEventListener('click', function (e) {
            e.preventDefault();
            newTopicInput.style.display = 'block';
            forumTopicInput.value = '';
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener('click', function (e) {
            e.preventDefault();
            newTopicInput.style.display = 'none';
            forumTopicInput.value = forumTopicInput.dataset.activeTopic;
            if (newTopic) newTopic.value = '';
        });
    }

    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            // Only block submission if:
            // 1. new-topic box is visible
            // 2. new-topic field is empty
            if (newTopicInput.style.display === 'block' &&
                newTopic.value.trim() === '') 
            {
                e.preventDefault();
                alert("Please enter a new forum topic name or click Cancel.");
            }
        });
    }
});

