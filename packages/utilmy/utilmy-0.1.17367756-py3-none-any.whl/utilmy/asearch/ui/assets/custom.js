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

    setTimeout(function() {
        document.querySelectorAll('textarea').forEach(el => {
            el.style.height = (el.scrollHeight) + 'px';

            el.addEventListener('input', () => {
                el.style.height = (el.scrollHeight) + 'px';
            });
        });

        document.getElementById("submit-button").onclick = function() {
            const chatOutput = document.getElementById("chat-output");
            const inputDot = document.getElementById("input_dot");
            

            if (inputDot) {
                inputDot.innerText = "Please wait a moment. Looking for answers... ";

                //const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
                //await sleep(10000);

                animateDots(inputDot, chatOutput);
            }
        };
    }, 300);
});






//------------------------------------------------------------------------------------
//------------------------ Print dot -------------------------------------------------
let dotAnimationInterval;

function animateDots(element, chatOutput) {
    if (!element) return;

    if (dotAnimationInterval) {
        clearInterval(dotAnimationInterval);
    }

    let dots = 0;
    dotAnimationInterval = setInterval(() => {
        element.innerText = '.'.repeat(dots);
        dots = (dots + 1) % 15;
        if (chatOutput.innerText) {
            stopDotAnimation();
            element.innerText = '';
        }
    }, 1000);
}

function stopDotAnimation() {
    if (dotAnimationInterval) {
        clearInterval(dotAnimationInterval);
        dotAnimationInterval = null;
    }
}



