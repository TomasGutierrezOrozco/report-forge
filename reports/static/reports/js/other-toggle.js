document.addEventListener('DOMContentLoaded', initOtherToggles);
document.addEventListener('htmx:afterSettle', initOtherToggles);

function initOtherToggles() {
    // Map of select field name to its corresponding custom field name
    const toggleMap = {
        'platform': 'custom_platform',
        'operating_system': 'custom_operating_system',
        'vulnerability_type': 'custom_vulnerability_type',
        'exploit_type': 'custom_exploit_type',
        'flag_type': 'custom_flag_type'
    };

    for (const [selectName, customName] of Object.entries(toggleMap)) {
        const selects = document.querySelectorAll(`select[name="${selectName}"]`);
        const customInputs = document.querySelectorAll(`input[name="${customName}"]`);

        if (selects.length > 0 && customInputs.length > 0) {
            selects.forEach((select, index) => {
                const customInput = customInputs[index];
                if (!customInput) return;

                // Find the wrapper (usually a div containing the label and input)
                const customWrapper = customInput.closest('div.mb-3') || customInput.parentElement;

                const toggleVisibility = () => {
                    const value = select.value.toLowerCase();
                    if (value === 'other') {
                        customWrapper.style.display = 'block';
                        customInput.required = true;
                    } else {
                        customWrapper.style.display = 'none';
                        customInput.required = false;
                        customInput.value = '';
                    }
                };

                // Initial check
                toggleVisibility();

                // Listen for changes
                select.addEventListener('change', toggleVisibility);
            });
        }
    }
}
