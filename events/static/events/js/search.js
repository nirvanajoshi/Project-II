// Wait until the page has fully loaded before running this code.
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('live-search-form');
    const results = document.getElementById('event-results');

    if (!form || !results) {
        // If the search form or results container is missing, do nothing.
        return;
    }

    // Use the URL from the results container or the form action.
    const targetUrl = results.dataset.targetUrl || form.action;
    let timeoutId;

    function fetchResults() {
        // Build a query string from the form data and make a request.
        const formData = new FormData(form);
        const queryString = new URLSearchParams(formData).toString();
        const url = `${targetUrl}?${queryString}`;

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Search request failed');
                }
                return response.text();
            })
            .then((html) => {
                // Replace the event list HTML with the updated search results.
                results.innerHTML = html;
            })
            .catch((error) => {
                console.error(error);
            });
    }

    form.addEventListener('submit', function (event) {
        // Prevent page reload when the search form is submitted.
        event.preventDefault();
        clearTimeout(timeoutId);
        fetchResults();
    });

    form.addEventListener('input', function () {
        // Wait a short time after typing before sending the search request.
        clearTimeout(timeoutId);
        timeoutId = setTimeout(fetchResults, 300);
    });
});
