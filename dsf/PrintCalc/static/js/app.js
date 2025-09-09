/**
 * JavaScript functionality for the Printing Cost Calculator
 * Enhances user experience with interactive features
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips if Bootstrap tooltips are available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            form.classList.add('was-validated');
        });
    });

    // Numeric input validation
    const numericInputs = document.querySelectorAll('input[type="number"]');
    numericInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            const min = parseFloat(this.min);
            const max = parseFloat(this.max);
            
            if (isNaN(value)) return;
            
            if (min !== undefined && value < min) {
                this.setCustomValidity('القيمة يجب أن تكون أكبر من أو تساوي ' + min);
            } else if (max !== undefined && value > max) {
                this.setCustomValidity('القيمة يجب أن تكون أقل من أو تساوي ' + max);
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // Enhanced modal functionality
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('show.bs.modal', function() {
            // Focus on first input when modal opens
            const firstInput = modal.querySelector('input, select, textarea');
            if (firstInput) {
                setTimeout(function() {
                    firstInput.focus();
                }, 150);
            }
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
            // Clear form validation states when modal closes
            const form = modal.querySelector('form');
            if (form) {
                form.classList.remove('was-validated');
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(function(input) {
                    input.setCustomValidity('');
                });
            }
        });
    });

    // Calculation form enhancements
    const calculationForm = document.getElementById('calculationForm');
    if (calculationForm) {
        // Real-time cost preview
        const printingPrices = calculationForm.querySelectorAll('input[name="printing_price_id"]');
        const addons = calculationForm.querySelectorAll('input[name="addons"]');
        const pageCount = parseInt(document.querySelector('[data-page-count]')?.dataset.pageCount || '0');
        
        function updateCostPreview() {
            const selectedPricing = calculationForm.querySelector('input[name="printing_price_id"]:checked');
            if (!selectedPricing || !pageCount) return;
            
            const pricePerUnit = parseFloat(selectedPricing.dataset.pricePerUnit || '0');
            const pagesPerUnit = parseInt(selectedPricing.dataset.pagesPerUnit || '1');
            const unitsNeeded = Math.ceil(pageCount / pagesPerUnit);
            let totalCost = unitsNeeded * pricePerUnit;
            
            // Add selected add-ons
            const selectedAddons = calculationForm.querySelectorAll('input[name="addons"]:checked');
            selectedAddons.forEach(function(addon) {
                totalCost += parseFloat(addon.dataset.price || '0');
            });
            
            // Update preview if element exists
            const preview = document.getElementById('costPreview');
            if (preview) {
                preview.innerHTML = `التكلفة المتوقعة: ${totalCost.toFixed(2)} جنيه`;
                preview.style.display = 'block';
            }
        }
        
        // Add data attributes for calculation
        printingPrices.forEach(function(radio) {
            const label = radio.nextElementSibling;
            if (label) {
                const text = label.textContent;
                const priceMatch = text.match(/(\d+\.?\d*)\s*جنيه/);
                const pagesMatch = text.match(/(\d+)\s*صفحات/);
                
                if (priceMatch) radio.dataset.pricePerUnit = priceMatch[1];
                if (pagesMatch) radio.dataset.pagesPerUnit = pagesMatch[1];
            }
            
            radio.addEventListener('change', updateCostPreview);
        });
        
        addons.forEach(function(checkbox) {
            const label = checkbox.nextElementSibling;
            if (label) {
                const text = label.textContent;
                const priceMatch = text.match(/(\d+\.?\d*)\s*جنيه/);
                if (priceMatch) checkbox.dataset.price = priceMatch[1];
            }
            
            checkbox.addEventListener('change', updateCostPreview);
        });
    }

    // Search functionality for tables
    function addTableSearch(tableId, searchInputId) {
        const table = document.getElementById(tableId);
        const searchInput = document.getElementById(searchInputId);
        
        if (!table || !searchInput) return;
        
        searchInput.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) { // Skip header row
                const row = rows[i];
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            }
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading states for forms
    function addLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;
        
        const originalText = submitBtn.innerHTML;
        
        form.addEventListener('submit', function() {
            if (form.checkValidity()) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading me-2"></span>جاري المعالجة...';
                
                // Re-enable after 5 seconds as fallback
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 5000);
            }
        });
    }
    
    // Apply loading states to all forms
    forms.forEach(addLoadingState);

    // Confirmation dialogs for dangerous actions
    const dangerousButtons = document.querySelectorAll('[data-confirm]');
    dangerousButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'هل أنت متأكد من هذا الإجراء؟';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });

    // Auto-save for forms (local storage)
    function setupAutoSave(form) {
        const formId = form.id;
        if (!formId) return;
        
        const saveKey = 'autosave_' + formId;
        
        // Load saved data
        const savedData = localStorage.getItem(saveKey);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(function(name) {
                    const field = form.querySelector(`[name="${name}"]`);
                    if (field && field.type !== 'password') {
                        if (field.type === 'checkbox' || field.type === 'radio') {
                            field.checked = data[name];
                        } else {
                            field.value = data[name];
                        }
                    }
                });
            } catch (e) {
                console.warn('Failed to restore auto-saved data:', e);
            }
        }
        
        // Save data on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (form.querySelector(`[name="${key}"]`).type !== 'password') {
                        data[key] = value;
                    }
                }
                
                localStorage.setItem(saveKey, JSON.stringify(data));
            });
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            if (form.checkValidity()) {
                localStorage.removeItem(saveKey);
            }
        });
    }

    // Apply auto-save to non-search forms
    forms.forEach(function(form) {
        if (!form.classList.contains('no-autosave') && form.method.toLowerCase() === 'post') {
            setupAutoSave(form);
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + / for search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[placeholder*="بحث"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modalInstance = bootstrap.Modal.getInstance(openModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
    });

    // Print functionality
    function addPrintButton() {
        const printBtn = document.getElementById('printResults');
        if (printBtn) {
            printBtn.addEventListener('click', function() {
                window.print();
            });
        }
    }
    addPrintButton();

    // Progressive enhancement - add features if supported
    if ('serviceWorker' in navigator) {
        // Service worker registration could go here for offline support
    }

    // Back button handling
    window.addEventListener('popstate', function(e) {
        // Handle back button navigation if needed
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.display = 'none';
        });
    });

    console.log('Printing Cost Calculator initialized successfully');
});

// Utility functions
window.PrintingCalculator = {
    // Format currency
    formatCurrency: function(amount) {
        return parseFloat(amount).toFixed(2) + ' جنيه';
    },
    
    // Calculate printing cost
    calculateCost: function(pages, pricePerUnit, pagesPerUnit) {
        const units = Math.ceil(pages / pagesPerUnit);
        return units * pricePerUnit;
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertAdjacentHTML('afterbegin', alertHtml);
        }
    }
};
