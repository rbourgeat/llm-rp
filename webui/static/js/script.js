var pollingInterval = 10;
var isRunning = false;

function startExecution() {
    if (isRunning) return;
    isRunning = true;
    $('#start-button').prop('disabled', true);
    $.post('/execute', {command: './llama.cpp/main -m llama.cpp/models/WizardLM-13B-V1.0-Uncensored/ggml-model-q4_0.bin -ngl 1 --repeat_penalty 1.1 --color -i -f prompts/RolePlayV1.txt -r "USER: "'}, function(data) {
        // Script started successfully
        pollOutput();
    });
}

function pollOutput() {
    $.get('/get_output', function(data) {
        var output = data.output;
        if (output) {
            $('#output').append(output);
            $('#output').scrollTop($('#output')[0].scrollHeight);
        }
        if (isRunning) {
            setTimeout(pollOutput, pollingInterval);
        }
    });
}

function sendInput() {
    var input = $('#input-command').val().trim();
    $('#input-command').val('');
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
