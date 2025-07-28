// frontend/script.js
const form = document.getElementById('journal-form');
const entryTextarea = document.getElementById('journal-entry');
const responseCard = document.getElementById('response-card');
const responseText = document.getElementById('response-text');
const entriesList = document.getElementById('entries-list');

// Function to fetch and display all entries
const fetchEntries = async () => {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/journal/entries');
        const entries = await res.json();

        // Clear the current list
        entriesList.innerHTML = ''; 

        // Create and append a card for each entry
        entries.forEach(entry => {
            const entryCard = document.createElement('div');
            entryCard.className = 'entry-card';

            const entryDate = new Date(entry.created_date).toLocaleString();
            entryCard.innerHTML = `
                <p>${entry.text}</p>
                <small>${entryDate}</small>
            `;
            entriesList.appendChild(entryCard);
        });
    } catch (error) {
        console.error("Failed to fetch entries:", error);
    }
};

// The form submission logic (updated to refresh the list)
form.addEventListener('submit', async (event) => {
    event.preventDefault(); 
    
    const entry = entryTextarea.value;
    if (!entry) return;

    try {
        const res = await fetch('http://127.0.0.1:8000/api/journal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: entry }),
        });

        const data = await res.json();
        
        // Display the "saved" message
        responseText.textContent = data.llm_response;
        responseCard.classList.remove('hidden');

        entryTextarea.value = '';

        // --- IMPORTANT ---
        // Fetch and display the updated list of entries
        fetchEntries(); 

    } catch (error) {
        console.error("Failed to submit journal entry:", error);
    }
});

// --- IMPORTANT ---
// Fetch all entries when the page first loads
document.addEventListener('DOMContentLoaded', fetchEntries);