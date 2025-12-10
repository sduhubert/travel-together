//Creating event listeners to allow users to create new forum topics on the trip message board
//referenced Claude AI (Sonnet 4.5) to for parts of the event listener logic below
//referenced ChatGpt for the messageForm function, preventing the app from breaking when the 'add forum' button is clicked but input is left null
$(document).ready(function () {
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
            $(".send-message-area").attr("placeholder", "Enter your first message for the new topic...")
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener('click', function (e) {
            e.preventDefault();
            newTopicInput.style.display = 'none';
            forumTopicInput.value = forumTopicInput.dataset.activeTopic;
            if (newTopic) newTopic.value = '';
            $(".send-message-area").attr("placeholder", "What's on your mind?")
        });
    }

    if (messageForm) {
        messageForm.addEventListener('submit', function (e) {
            // Only block submission if:
            // 1. new-topic box is visible
            // 2. new-topic field is empty
            if (newTopicInput.style.display === 'block' && newTopic.value.trim() === '') {
                newTopicInput.style.display = 'none';
                forumTopicInput.value = forumTopicInput.dataset.activeTopic;
                if (newTopic) {
                    newTopic.value = '';
                }
                $(".send-message-area").attr("placeholder", "What's on your mind?")
            }
        });
    }

    // Open trip participants popup
    $(".open-members-popup").click(function () {
        $("#members-popup").fadeIn();
        $("body").css("overflow", "hidden");
    });

    // Open join requests popup
    $("#open-join-requests-popup").click(function () {
        $("#join-requests-popup").fadeIn();
        $("body").css("overflow", "hidden");
    });

    // Close popup by clicking X
    $(".popup .close").click(function () {
        $(this).closest(".popup").fadeOut();
        $("body").css("overflow", "auto");
    });

    // Close popup by clicking outside of it
    $(".popup").click(function (e) {
        if (e.target === this) {
            $(this).closest(".popup").fadeOut();
            $("body").css("overflow", "auto");
        }
    });

    // Close popup by clicking outside of it
    $(".popup").click(function (e) {
        if (e.target === this) {
            $(this).closest(".popup").fadeOut();
            $("body").css("overflow", "auto");
        }
    });

    scrollChatToBottom();
});

function scrollChatToBottom() {
    var chatBox = $('.messages-container');
    chatBox.scrollTop(chatBox[0].scrollHeight);
}
