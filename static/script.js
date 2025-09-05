function loadCalendar() {
    let currentDate = new Date();
    const monthYearLabel = document.getElementById('month-year');
    const calendarGrid = document.querySelector('.calendar');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const modal = document.getElementById('schedule-modal');
    const modalTitle = document.getElementById('modal-title');
    const scheduleTitleInput = document.getElementById('schedule-title');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const startTimeInput = document.getElementById('start-time');
    const endTimeInput = document.getElementById('end-time');
    const saveButton = document.getElementById('save-button');
    const closeButton = document.getElementById('close-button');
    const completeButton = document.getElementById('complete-button');
    const deleteButton = document.getElementById('delete-button');

    let schedules = {};
    let editingSchedule = null;

    const loadSchedules = async () => {
        try {
            const response = await fetch('/schedules');
            schedules = await response.json();
            renderCalendar();
        } catch (error) {
            console.error('スケジュールの読み込みに失敗しました:', error);
        }
    };

    const renderCalendar = () => {
        calendarGrid.innerHTML = `
            <div class="day-name">日</div>
            <div class="day-name">月</div>
            <div class="day-name">火</div>
            <div class="day-name">水</div>
            <div class="day-name">木</div>
            <div class="day-name">金</div>
            <div class="day-name">土</div>
        `;
        
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        monthYearLabel.textContent = `${year}年 ${month + 1}月`;

        const firstDayOfMonth = new Date(year, month, 1).getDay();
        const lastDateOfMonth = new Date(year, month + 1, 0).getDate();

        for (let i = 0; i < firstDayOfMonth; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.classList.add('day', 'empty');
            calendarGrid.appendChild(emptyDay);
        }

        for (let i = 1; i <= lastDateOfMonth; i++) {
            const day = document.createElement('div');
            day.classList.add('day');
            const dayNumber = document.createElement('div');
            dayNumber.classList.add('day-number');
            dayNumber.textContent = i;
            day.appendChild(dayNumber);

            const formattedDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
            day.dataset.date = formattedDate;

            if (schedules[formattedDate]) {
                schedules[formattedDate].forEach(schedule => {
                    const scheduleItem = document.createElement('div');
                    scheduleItem.classList.add('schedule-item');
                    
                    const scheduleTitleDiv = document.createElement('div');
                    scheduleTitleDiv.classList.add('schedule-title');
                    scheduleTitleDiv.textContent = schedule.title;
                    
                    if (schedule.completed) {
                        scheduleTitleDiv.classList.add('completed');
                    }

                    scheduleItem.addEventListener('click', (event) => {
                        event.stopPropagation();
                        openEditModal(schedule, formattedDate);
                    });
                    
                    const scheduleTimeDiv = document.createElement('div');
                    scheduleTimeDiv.classList.add('schedule-time');
                    
                    const startDate = new Date(schedule.start_date);
                    const endDate = new Date(schedule.end_date);
                    
                    if (startDate.toDateString() === endDate.toDateString()) {
                        scheduleTimeDiv.textContent = `${schedule.start_time} - ${schedule.end_time}`;
                    } else {
                        scheduleTimeDiv.textContent = `(${schedule.start_date.substring(5)} - ${schedule.end_date.substring(5)})`;
                    }
                    
                    scheduleItem.appendChild(scheduleTitleDiv);
                    scheduleItem.appendChild(scheduleTimeDiv);
                    day.appendChild(scheduleItem);
                });
            }

            day.addEventListener('click', () => {
                const today = new Date().toISOString().split('T')[0];
                startDateInput.value = formattedDate;
                endDateInput.value = formattedDate;
                startTimeInput.value = '09:00';
                endTimeInput.value = '17:00';
                modalTitle.textContent = '新しい予定を登録';
                completeButton.style.display = 'none';
                deleteButton.style.display = 'none';
                editingSchedule = null;
                modal.style.display = 'flex';
            });

            calendarGrid.appendChild(day);
        }
    };

    const openEditModal = (schedule, date) => {
        editingSchedule = { ...schedule, date };
        modalTitle.textContent = '予定を編集';
        scheduleTitleInput.value = schedule.title;
        startDateInput.value = schedule.start_date;
        endDateInput.value = schedule.end_date;
        startTimeInput.value = schedule.start_time;
        endTimeInput.value = schedule.end_time;
        completeButton.style.display = 'block';
        deleteButton.style.display = 'block';
        modal.style.display = 'flex';
    };

    const saveSchedule = async () => {
        const title = scheduleTitleInput.value.trim();
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const startTime = startTimeInput.value;
        const endTime = endTimeInput.value;

        if (!title || !startDate || !endDate || !startTime || !endTime) {
            alert('タイトル、開始日、終了日、時間をすべて入力してください。');
            return;
        }

        try {
            if (editingSchedule) {
                // 編集
                await fetch('/schedules', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        old_title: editingSchedule.title,
                        new_title: title,
                        old_start_date: editingSchedule.start_date,
                        old_end_date: editingSchedule.end_date,
                        old_start_time: editingSchedule.start_time,
                        new_start_date: startDate,
                        new_end_date: endDate,
                        new_start_time: startTime,
                        new_end_time: endTime
                    })
                });
            } else {
                // 新規作成
                const payload = {
                    title: title,
                    start_date: startDate,
                    end_date: endDate,
                    start_time: startTime,
                    end_time: endTime
                };
                await fetch('/schedules', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }
            await loadSchedules();
            modal.style.display = 'none';
        } catch (error) {
            console.error('APIへの接続に失敗しました:', error);
        }
    };
    
    const deleteSchedule = async () => {
        if (!editingSchedule) return;

        try {
            await fetch('/schedules', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: editingSchedule.title,
                    start_date: editingSchedule.start_date,
                    end_date: editingSchedule.end_date,
                    start_time: editingSchedule.start_time
                })
            });
            await loadSchedules();
            modal.style.display = 'none';
        } catch (error) {
            console.error('スケジュールの削除に失敗しました:', error);
        }
    };
    
    completeButton.addEventListener('click', async () => {
        if (!editingSchedule) return;

        try {
            await fetch('/complete_schedule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    date: editingSchedule.date,
                    title: editingSchedule.title,
                    start_time: editingSchedule.start_time
                })
            });
            await loadSchedules();
            modal.style.display = 'none';
        } catch (error) {
            console.error('完了状態の更新に失敗しました:', error);
        }
    });

    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
        loadSchedules();
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
        loadSchedules();
    });

    saveButton.addEventListener('click', saveSchedule);
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    deleteButton.addEventListener('click', deleteSchedule);
    
    loadSchedules();
}
