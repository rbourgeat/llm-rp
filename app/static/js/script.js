var pollingInterval = 10;
var isRunning = false;
var rpStarted = false;
var modelLoading = 0;
var prompt = "";

function startExecution() {
    if (isRunning) return;
    isRunning = true;
    $('#start-button').prop('disabled', true);
    $.post('/execute', function(data) {
        pollOutput();
    });
}

function pollOutput() {
    $.get('/get_output', function(data) {
        var output = data.output;
        if (output && rpStarted) {
            prompt = prompt + output;
            if (prompt.length > 300)
                prompt = prompt.slice(output.length);
            $('#output').append(output);
            $('#output').scrollTop($('#output')[0].scrollHeight);
            if (modelLoading < 100) {
                var progressBar = document.querySelector('.progress');
                modelLoading = 100;
                progressBar.style.width = String(modelLoading) + '%';
            }
        }
        if (!rpStarted) {
            var progressBar = document.querySelector('.progress');
            modelLoading += 0.07;
            progressBar.style.width = String(modelLoading) + '%';
        }
        if (isRunning) {
            setTimeout(pollOutput, pollingInterval);
        }
        if (output.includes("===")) {
            rpStarted = true;
        }
    });
}


function sendInput() {
    var input = $('#input-command').val().trim();
    $('#input-command').val('');
    $.post('/send_input', {input: input});

    $.post('/generate_image', { prompt: prompt }, function(data) {
        if (data.error)
            return;
        var imageContainer = document.getElementById('image-container');
        var image = document.createElement('img');
        image.src = "/images/" + data.file_name;
        imageContainer.innerHTML = '';
        imageContainer.appendChild(image);
    })
}

function reloadPage() {
    location.reload();
}

$(document).ready(function() {
    $('#input-form').hide();
    $('#start-button').hide();

    $.get('/check_llama_cpp', function(data) {
        $('#start-button').show();
        $('#status-container').hide();
    });

    $('#start-button').click(function() {
        $(this).hide();
        $('#input-form').show();
        startExecution();
    });

    $('#input-form').submit(function(event) {
        event.preventDefault();
        sendInput();
    });

    $('#reload-button').click(function() {
        reloadPage();
    });
});
