var pollingInterval = 10;
var isRunning = false;
var rpStarted = false;
var modelLoading = 0;
var prompt = "";
var mode = "";

function startExecution() {
    if (isRunning) return;
    isRunning = true;
    $.post('/execute', {mode: mode} , function(data) {
        pollOutput();
    });
    document.getElementById("button-container").remove();
    $('#input-command').prop('disabled', true);
    $('#input-command').val('Generating response...');
    $('#send-button').prop('disabled', true);
    $('#send-button').val('🔒');
}

function pollOutput() {
    $.get('/get_output', function(data) {
        var output = data.output;
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
        if (output && rpStarted && output !== "[EOS]") {
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
        if (output === "[EOS]" && rpStarted) {
            $('#input-command').prop('disabled', false);
            $('#input-command').val('');
            $('#send-button').prop('disabled', false);
            $('#send-button').val('Send');
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
    });
}

function sendInput() {
    var input = $('#input-command').val().trim();
    $('#input-command').val('Generating response...');
    $('#input-command').prop('disabled', true);
    $('#send-button').prop('disabled', true);
    $('#send-button').val('🔒');
    $.post('/send_input', {input: input});
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

    $('#start-button-random').click(function() {
        $(this).hide();
        $('#input-form').show();
        mode = "random";
        startExecution();
    });

    $('#start-button-custom').click(function() {
        $(this).hide();
        $('#input-form').show();
        mode = "custom";
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
