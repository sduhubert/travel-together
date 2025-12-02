//Creating event listeners to allow users to create new forum topics on the trip message board
//referenced Claude AI (Sonnet 4.5) to for parts of the event listener logic below
$(document).ready(function() {
    const newTopicButton = document.getElementById('new-topic-button');
    const newTopicInput = document.getElementById('new-forum-topic-input');
    const forumTopicInput = document.getElementById('forum-topic-input');
    const cancelButton = document.getElementById('cancel-new-forum-topic');
    const newTopic = document.querySelector('input[name="new-forum-topic"]');

    if (newTopicButton) {
        newTopicButton.addEventListener('click', function (e) {
            e.preventDefault();
            newTopicInput.style.display = 'block';
            forumTopicInput.value = ''; // clear value after event
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener('click', function (e) {
            e.preventDefault();
            newTopicInput.style.display = 'none';
            forumTopicInput.value = forumTopicInput.dataset.activeTopic;
            if (newTopic) {
                newTopic.value = '';
            }
        });
    }
});
