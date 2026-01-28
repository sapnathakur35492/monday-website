document.addEventListener('DOMContentLoaded', () => {
    // Initialize dragula for all kanban content containers
    const containers = Array.from(document.querySelectorAll('.kanban-content'));
    
    if (containers.length === 0) return;

    const drake = dragula(containers, {
        revertOnSpill: true
    });

    drake.on('drop', (el, target, source, sibling) => {
        // Collect Data
        const itemId = el.dataset.itemId;
        const newStatus = target.closest('.kanban-column').dataset.status;
        const previousStatus = source.closest('.kanban-column').dataset.status;
        const newGroupId = null; // Kanban usually ignores Groups, or requires specific logic if we group by "Group" instead of "Status"

        // Find new position
        // In this simple implementation, we just append or use index.
        const newPosition = Array.from(target.children).indexOf(el);

        // Optimistic UI Update (Already handled by dragula visually)
        
        // Send API Request
        fetch('/app/api/update-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                itemId: itemId,
                newStatus: newStatus !== previousStatus ? newStatus : null,
                newPosition: newPosition
            })
        })
        .then(response => {
            if (!response.ok) {
                // Revert on failure
                drake.cancel(true);
                alert('Failed to update status.');
            } else {
                // If status changed, we might need to update the card color/badge visually if it depends on data
                // For now, dragula handled the move.
                
                // Trigger confetti if moved to "Done"
                if (newStatus === 'Done' && previousStatus !== 'Done') {
                    confetti({
                        particleCount: 100,
                        spread: 70,
                        origin: { y: 0.6 }
                    });
                }
            }
        })
        .catch(err => {
            console.error(err);
            drake.cancel(true);
        });
    });

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
