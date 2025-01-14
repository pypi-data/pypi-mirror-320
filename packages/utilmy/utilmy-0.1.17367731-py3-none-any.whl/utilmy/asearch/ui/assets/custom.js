document.addEventListener('DOMContentLoaded', function() {

    var clipboard = new ClipboardJS('#copy-button', {
        text: function() {
            var chatOutput = document.getElementById('chat-output');
            return chatOutput ? chatOutput.innerText : '';
        }
    });

    clipboard.on('success', function(e) {
        alert('Copied to clipboard!');
    });

    clipboard.on('error', function(e) {
        alert('Failed to copy to clipboard.');
    });
});
