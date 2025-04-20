document.getElementById('prompt').addEventListener('input', function(e) {
    const prompt = e.target.value;
    const imageFile = document.getElementById('image').files[0];

    const formData = new FormData();
    formData.append('text_prompt', prompt);
    if (imageFile) {
        formData.append('image', imageFile);
    }

    fetch('/process_prompt/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('llm-response').innerText = data.agent_response;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('llm-response').innerText = 'Error: ' + error;
    });
});
