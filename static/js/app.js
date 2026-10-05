/**
 * Flavour Fusion - Interactive Frontend Features
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Quick Ingredient Tag Buttons
    const ingredientsInput = document.getElementById('ingredients-input');
    const presetTags = document.querySelectorAll('.preset-tag');
    
    if (ingredientsInput && presetTags.length > 0) {
        presetTags.forEach(tag => {
            tag.addEventListener('click', () => {
                const tagValue = tag.getAttribute('data-tag');
                let currentVal = ingredientsInput.value.trim();
                
                if (!currentVal) {
                    ingredientsInput.value = tagValue;
                } else {
                    // Check if already in input
                    const existingList = currentVal.split(',').map(item => item.strip ? item.strip().toLowerCase() : item.trim().toLowerCase());
                    if (!existingList.includes(tagValue.toLowerCase())) {
                        ingredientsInput.value = `${currentVal}, ${tagValue}`;
                    }
                }
                
                // Visual feedback effect
                tag.style.transform = 'scale(0.95)';
                setTimeout(() => tag.style.transform = 'none', 150);
            });
        });
    }

    // 2. Recommendation Search Form Loading Spinner
    const searchForm = document.getElementById('recommendation-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    if (searchForm && loadingOverlay) {
        searchForm.addEventListener('submit', (e) => {
            if (searchForm.checkValidity()) {
                loadingOverlay.classList.remove('hidden');
            }
        });
    }
});

// 3. Explainable AI Score Accordion Toggle Helper
function toggleAccordion(button) {
    const accordionCard = button.closest('.explainable-ai-card');
    if (!accordionCard) return;
    
    const content = accordionCard.querySelector('.accordion-content');
    const icon = button.querySelector('.accordion-icon');
    
    if (content) {
        content.classList.toggle('hidden');
        if (icon) {
            icon.classList.toggle('fa-chevron-up');
            icon.classList.toggle('fa-chevron-down');
        }
    }
}
