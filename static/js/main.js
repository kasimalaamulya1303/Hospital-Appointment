/**
 * AuraCare Hospital Portal - Interactive JavaScript
 * Implements:
 * 1. JavaScript Doctor Filtering by Department & Search (Cardiology, Pediatrics, Orthopedics, Neurology)
 * 2. Interactive Date & Time Slot Selector (Live booked vs available slot badges)
 * 3. Booking summary preview & validation
 */

document.addEventListener('DOMContentLoaded', function () {
    initDoctorFiltering();
    initSlotSelector();
    initDoctorModals();
});

// ==========================================================================
// 1. Doctor Filtering by Department & Live Search
// ==========================================================================
function initDoctorFiltering() {
    const deptPills = document.querySelectorAll('.dept-filter-pill');
    const searchInput = document.getElementById('doctorSearchInput');
    const doctorCards = document.querySelectorAll('.doctor-card-item');
    const noResultsMsg = document.getElementById('noDoctorsFound');
    const visibleCountSpan = document.getElementById('visibleDoctorCount');

    if (!doctorCards.length) return;

    let currentDept = 'All';
    let currentSearch = '';

    function applyFilter() {
        let visibleCount = 0;

        doctorCards.forEach(card => {
            const dept = card.getAttribute('data-department') || '';
            const name = (card.getAttribute('data-name') || '').toLowerCase();
            const spec = (card.getAttribute('data-specialization') || '').toLowerCase();

            const matchesDept = (currentDept === 'All' || dept.toLowerCase() === currentDept.toLowerCase());
            const matchesSearch = !currentSearch || name.includes(currentSearch) || spec.includes(currentSearch) || dept.toLowerCase().includes(currentSearch);

            if (matchesDept && matchesSearch) {
                card.style.display = 'block';
                card.classList.add('animate__fadeIn');
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (visibleCountSpan) {
            visibleCountSpan.textContent = visibleCount;
        }

        if (noResultsMsg) {
            noResultsMsg.style.display = (visibleCount === 0) ? 'block' : 'none';
        }
    }

    deptPills.forEach(pill => {
        pill.addEventListener('click', function () {
            deptPills.forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            currentDept = this.getAttribute('data-dept') || 'All';
            applyFilter();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            currentSearch = this.value.trim().toLowerCase();
            applyFilter();
        });
    }
}

// ==========================================================================
// 2. Interactive Date/Time Slot Selection
// ==========================================================================
function initSlotSelector() {
    const doctorSelect = document.getElementById('id_doctor');
    const dateInput = document.getElementById('id_date');
    const slotSelect = document.getElementById('id_time_slot');
    const slotGridContainer = document.getElementById('slotGridContainer');
    const slotLoadingSpinner = document.getElementById('slotLoadingSpinner');
    const slotHelpText = document.getElementById('slotHelpText');

    // Summary Elements
    const summaryDoctor = document.getElementById('summaryDoctor');
    const summaryDate = document.getElementById('summaryDate');
    const summarySlot = document.getElementById('summarySlot');
    const summaryFee = document.getElementById('summaryFee');

    if (!doctorSelect || !dateInput || !slotGridContainer) return;

    // Default time slots list as fallback
    const defaultSlots = [
        '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
        '11:00 AM', '11:30 AM', '02:00 PM', '02:30 PM',
        '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM'
    ];

    function updateSummary() {
        if (summaryDoctor) {
            const selectedOpt = doctorSelect.options[doctorSelect.selectedIndex];
            summaryDoctor.textContent = selectedOpt && selectedOpt.value ? selectedOpt.text : 'Please select doctor';
            if (summaryFee && selectedOpt && selectedOpt.getAttribute('data-fee')) {
                summaryFee.textContent = '$' + selectedOpt.getAttribute('data-fee');
            }
        }
        if (summaryDate) {
            summaryDate.textContent = dateInput.value || 'Please select date';
        }
        if (summarySlot) {
            summarySlot.textContent = slotSelect.value || 'Please select time slot';
        }
    }

    async function fetchAndUpdateSlots() {
        const doctorId = doctorSelect.value;
        const selectedDate = dateInput.value;

        updateSummary();

        if (!doctorId || !selectedDate) {
            slotGridContainer.innerHTML = '';
            if (slotHelpText) {
                slotHelpText.innerHTML = '<span class="text-muted"><i class="bi bi-info-circle me-1"></i>Select both a Doctor and Date above to load real-time slot availability.</span>';
            }
            return;
        }

        if (slotLoadingSpinner) slotLoadingSpinner.classList.remove('d-none');
        if (slotHelpText) slotHelpText.innerHTML = '';

        try {
            const response = await fetch(`/api/available-slots/?doctor_id=${doctorId}&date=${selectedDate}`);
            const data = await response.json();

            if (slotLoadingSpinner) slotLoadingSpinner.classList.add('d-none');

            if (data.error) {
                slotGridContainer.innerHTML = `<div class="alert alert-warning py-2 mb-0">${data.error}</div>`;
                return;
            }

            const allSlots = data.all_slots || defaultSlots;
            const bookedSlots = new Set(data.booked_slots || []);
            const currentlySelected = slotSelect.value;

            slotGridContainer.innerHTML = '';

            let hasAvailable = false;

            allSlots.forEach(slot => {
                const isBooked = bookedSlots.has(slot);
                const isSelected = (slot === currentlySelected && !isBooked);

                if (!isBooked) hasAvailable = true;

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `slot-btn ${isBooked ? 'disabled' : ''} ${isSelected ? 'selected' : ''}`;
                btn.setAttribute('data-slot', slot);

                btn.innerHTML = `
                    <span class="slot-time"><i class="bi bi-clock me-1"></i>${slot}</span>
                    <span class="slot-status">${isBooked ? '<i class="bi bi-x-circle me-1"></i>Booked' : '<i class="bi bi-check-circle me-1"></i>Available'}</span>
                `;

                if (isBooked) {
                    btn.disabled = true;
                    btn.title = 'This slot is already booked for this doctor on the selected date.';
                } else {
                    btn.addEventListener('click', function () {
                        // Deselect other slots
                        document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                        this.classList.add('selected');

                        // Set value in the underlying form select
                        slotSelect.value = slot;
                        updateSummary();
                    });
                }

                slotGridContainer.appendChild(btn);
            });

            if (!hasAvailable) {
                if (slotHelpText) {
                    slotHelpText.innerHTML = '<div class="alert alert-warning py-2 mb-0 mt-2"><i class="bi bi-exclamation-triangle-fill me-1"></i>All slots are booked for this doctor on this date. Please choose another date.</div>';
                }
            } else {
                if (slotHelpText) {
                    slotHelpText.innerHTML = `<small class="text-success"><i class="bi bi-check2-all me-1"></i>${allSlots.length - bookedSlots.size} slots available for booking.</small>`;
                }
            }

        } catch (err) {
            console.error('Error fetching slots:', err);
            if (slotLoadingSpinner) slotLoadingSpinner.classList.add('d-none');
            if (slotGridContainer) {
                slotGridContainer.innerHTML = '<div class="alert alert-secondary py-2">Unable to load slot availability. You can still select a slot from the dropdown list.</div>';
            }
        }
    }

    doctorSelect.addEventListener('change', fetchAndUpdateSlots);
    dateInput.addEventListener('change', fetchAndUpdateSlots);

    // Initial check if fields are pre-filled (e.g. from doctor profile redirect)
    if (doctorSelect.value && dateInput.value) {
        fetchAndUpdateSlots();
    } else {
        updateSummary();
    }
}

// ==========================================================================
// 3. Doctor Details Modal
// ==========================================================================
function initDoctorModals() {
    const modalElement = document.getElementById('doctorDetailModal');
    if (!modalElement) return;

    modalElement.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        if (!button) return;

        const name = button.getAttribute('data-doc-name') || '';
        const dept = button.getAttribute('data-doc-dept') || '';
        const spec = button.getAttribute('data-doc-spec') || '';
        const qual = button.getAttribute('data-doc-qual') || '';
        const fee = button.getAttribute('data-doc-fee') || '';
        const days = button.getAttribute('data-doc-days') || '';
        const bio = button.getAttribute('data-doc-bio') || '';
        const docId = button.getAttribute('data-doc-id') || '';

        modalElement.querySelector('#modalDocName').textContent = name;
        modalElement.querySelector('#modalDocDept').textContent = dept;
        modalElement.querySelector('#modalDocSpec').textContent = spec;
        modalElement.querySelector('#modalDocQual').textContent = qual;
        modalElement.querySelector('#modalDocFee').textContent = '$' + fee;
        modalElement.querySelector('#modalDocDays').textContent = days;
        modalElement.querySelector('#modalDocBio').textContent = bio;

        const bookBtn = modalElement.querySelector('#modalBookBtn');
        if (bookBtn) {
            bookBtn.href = `/book-appointment/?doctor=${docId}`;
        }
    });
}
