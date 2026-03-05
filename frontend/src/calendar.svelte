<script lang="ts">
    import './calendar.css';
    import Notes_Modal from './Notes_Modal.svelte';
    import Tasks_Modal from './Tasks_Modal.svelte';
    import Add_Task_Modal from './Add_Task_Modal.svelte';
    let show_note_modal = $state(false);
    let openTaskTitle: string | null = $state(null);
    let show_tasks_modal = $state(false);
    let add_tasks_modal = $state(false);
    let add_task_date: string | null = $state(null);
  
    let properties = $props();
    let user = properties.user;
    let profile_picture = properties.profile_picture;

    let today = new Date();
    let curDay = today.getDate();
    let month = today.getMonth();
    let year = today.getFullYear();
    let weekday = today.getDay();
    let Months = ["Janurary", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    let monthString = Months[month];

    let current_viewing_day = $state(curDay);
    let current_viewing_month = $state(month);
    let current_viewing_year = $state(year);

    let firstDay = new Date(year, month, 1);
    let firstWeekday = firstDay.getDay();
    let weekdays = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    let weekdays_spelled_out = ['SUN', 'MON', 'TUES', 'WEDS', 'THURS', 'FRI', 'SAT'];
    let firstWeekdayString = weekdays[firstWeekday];
    let previousMonth = month - 1;
    let previousMonthString = Months[previousMonth];
    let numDaysInPreviousMonth = null;
    if (previousMonth == 0 || previousMonth == 2 || previousMonth == 4 || previousMonth == 6 || previousMonth == 7 || previousMonth == 9 || previousMonth == 11) {
        numDaysInPreviousMonth = 31;
    } else if (previousMonth == 1) {
        numDaysInPreviousMonth = 28;
    } else {
        numDaysInPreviousMonth = 30;
    }

    let numDaysInCurMonth = null;
    if (month == 0 || month == 2 || month == 4 || month == 6 || month == 7 || month == 9 || month == 11) {
        numDaysInCurMonth = 31;
    } else if (month == 1) {
        numDaysInCurMonth = 28;
    } else {
        numDaysInCurMonth = 30;
    }
    let numPaddingDays = 0;
    if (firstWeekday != 0) {
        numPaddingDays = firstWeekday - 1;
    }
    let paddingArray = Array.from({length: numPaddingDays}, (_, i) => numDaysInPreviousMonth - (numPaddingDays - i - 1));
    let daysArray = Array.from({length: numDaysInCurMonth}, (_, i) => i + 1);
    let allDaysArray = [...paddingArray, ...daysArray];
    const chunckedDays: any[] = [];
    for (let i = 0; i < allDaysArray.length; i += 7) {
        chunckedDays.push(allDaysArray.slice(i, i + 7));
    }
    if (chunckedDays.at(-1).length < 7) {
        let numPadding = 7 - chunckedDays.at(-1).length;
        for (let i = 1; i < numPadding + 1; i++) {
            chunckedDays.at(-1).push(i);
        }
    }
    let mainCalendarDays = chunckedDays.slice();
    if (mainCalendarDays.length != 6) {
        let lastDay = mainCalendarDays.at(-1).at(-1);
        if (lastDay == 30 || lastDay == 31 || lastDay == 28) {
            mainCalendarDays.push([1, 2, 3, 4, 5, 6, 7]);
        } else {
            mainCalendarDays.push([lastDay + 1, lastDay + 2, lastDay + 3, lastDay + 4, lastDay + 5, lastDay + 6, lastDay + 7]);
        }
    }

    type Task = {
        task_description: string;
        task_location: string;
        task_color: string;
        task_label: string;
        task_start_time: string;
        task_end_time: string;
        task_date: string;
        task_tags: string[];
        task_priority: string;
    };

    type Note = {
        note_description: string;
    }

    type TaskWithMeta = {
        title: string;
        details: Task;
        start: number;
        end: number;
        slot: number;
        totalSlots: number;
    };


    function parseTime(timeStr: string): number {
        const [h, m] = timeStr.split(':').map(Number);
		return h + m / 60;
    }

    function getPositionedTasks(tasks: Record<string, Task>, weekDate: string): TaskWithMeta[] {
        const result: TaskWithMeta[] = [];

        // Filter by date
        let dayTasks = Object.entries(tasks)
            .filter(([_, t]) => t.task_date === weekDate)
            .map(([title, details]) => ({
                title,
                details,
                start: parseTime(details.task_start_time),
                end: parseTime(details.task_end_time),
                slot: 0,
                totalSlots: 1
            }))
            .sort((a, b) => a.start - b.start);

        // Assign slots for overlapping tasks
        for (let i = 0; i < dayTasks.length; i++) {
            let current = dayTasks[i];
            let overlaps = [current];

            for (let j = i + 1; j < dayTasks.length; j++) {
                if (dayTasks[j].start < current.end) {
                    overlaps.push(dayTasks[j]);
                } else break;
            }

            // Assign horizontal slots
            overlaps.forEach((task, idx) => {
                task.slot = idx;
                task.totalSlots = overlaps.length;
            });

            // Skip over grouped overlaps
            i += overlaps.length - 1;
            result.push(...overlaps);
        }

        return result;
    }

    async function getTasks(user: string): Promise<Record<string, Task>> {
        return await fetch("http://localhost:8000/get_tasks/" + user, {
            method: "GET",
            headers: {'Content-Type': 'application/json'}
        })
        .then(response => response.json())
        .then(data => {
            return data.tasks;
        })
        .catch(error => {
            console.error("error getting tasks", error);
        });
    }

    async function getNotes(user: string): Promise<Record<string, Note>> {
        return await fetch("http://localhost:8000/get_notes/" + user, {
            method: "GET",
            headers: {'Content-Type': 'application/json'}
        })
        .then(response => response.json())
        .then(data => {
            return data.notes;
        })
        .catch(error => {
            console.error("error getting notes", error);
        });
    }

    function delete_note(note_title: string) {
        fetch("http://localhost:8000/delete_note", { 
            method: "POST", 
            body: JSON.stringify({
                user_id: user, 
                note_title: note_title
            }), 
            headers: {'Content-Type': 'application/json'}
        });
        delete notes[note_title];
        notes = {...notes};
    }

    function delete_task(task_title: string | null) {
        if (task_title != null) {
            fetch("http://localhost:8000/delete_task", {
                method: "POST",
                body: JSON.stringify({
                    user_id: user,
                    task_title: task_title
                }),
                headers: {'Content-Type': 'application/json'}
            });
            
            delete tasks[task_title];
            tasks = {...tasks};
            all_task_tags = Object.assign({});
            for (const [taskname, details] of Object.entries(tasks)) {
                let date = details.task_date.split('/');
                if (Number(date[1]) <= curDay + 3 && Number(date[1]) >= curDay) {
                    upcoming.push(taskname);
                }
                let tags = details.task_tags;
                for (let i = 0; i < tags.length; i++) {
                    if (tags[i] in all_task_tags) {
                        all_task_tags[tags[i]] += 1;
                    } else {
                        all_task_tags[tags[i]] = 1;
                    }
                    total_tags += 1;
                }
            }
            all_task_tags = {...all_task_tags};
            upcoming = {...upcoming};
            show_tasks_modal = false; 
            openTaskTitle = null;
            add_tasks_modal = false;
        }
    }

    function add_note(note_title: string, note_description: string) {
        fetch("http://localhost:8000/create_note", {
            method: "POST",
            body: JSON.stringify({
                user_id: user,
                note_title: note_title,
                note: note_description
            }),
            headers: {'Content-Type': 'application/json'}
        });
        notes[note_title] = {
            note_description: note_description
        };
        notes = {...notes};
        note_description_text_input = '';
        note_title_text_input = '';
    }

    function add_task(task_title: string | null, task_description: string, task_location: string, task_color: string, task_label: string, task_start_time: string, task_end_time: string, task_date: string | null, task_tags: string[], task_priority: string) {
        if (task_title != null && task_date != null) {
            fetch("http://localhost:8000/create_task", {
                method: "POST",
                body: JSON.stringify({
                    user_id: user,
                    task_name: task_title,
                    task_description: task_description,
                    task_location: task_location,
                    task_color: task_color,
                    task_label: task_label,
                    task_start_time: task_start_time,
                    task_end_time: task_end_time,
                    task_date: task_date,
                    task_tags: task_tags,
                    task_priority: task_priority
                }),
                headers: {'Content-Type': 'application/json'}
            });
            let task_tags_array = [];
            task_tags_array.push(task_tags);
            tasks[task_title] = {
                task_description: task_description,
                task_location: task_location,
                task_color: task_color,
                task_label: task_label,
                task_start_time: task_start_time,
                task_end_time: task_end_time,
                task_date: task_date,
                task_tags: task_tags_array,
                task_priority: task_priority
            }
            tasks = {...tasks};
            for (let i = 0; i < task_tags_array.length; i++) {
                if (task_tags_array[i] in all_task_tags) {
                    all_task_tags[task_tags_array[i]] += 1;
                } else {
                    all_task_tags[task_tags_array[i]] = 1;
                }
            }
            all_task_tags = {... all_task_tags}
            task_title_text_input  = '';
            task_description_text_input = '';
            task_location_text_input = '';
            task_color_text_input = '';
            task_label_text_input = '';
            task_start_time_text_input = '';
            task_end_time_text_input = '';
            task_tags_text_input = [''];
            task_priority_text_input = '';
            show_tasks_modal = false; 
            openTaskTitle = null;
            add_tasks_modal = false;
            add_tasks_modal = false;
            add_task_date = null;
        }
    }

    let note_title_text_input = $state('');
    let note_description_text_input = $state('');

    let task_title_text_input = $state('');
    let task_description_text_input = $state('');
    let task_location_text_input = $state('');
    let task_color_text_input = $state('');
    let task_label_text_input = $state('');
    let task_start_time_text_input = $state('');
    let task_end_time_text_input = $state('');
    let task_priority_text_input = $state('');
    let task_tags_text_input = $state(['']);


    let calendar_view = $state(1);

    let tasks: Record<string, Task> | undefined = $state();
    let notes: Record<string, Note> | undefined = $state();
    let upcoming: any[] = [];
    let loading = $state(true);
    let all_task_tags: Record<string, number> = $state({});
    let total_tags = 0;
    async function setup(user: string) {
        tasks = await getTasks(user);
        notes = await getNotes(user);
        for (const [taskname, details] of Object.entries(tasks)) {
            let date = details.task_date.split('/');
            if (Number(date[1]) <= curDay + 3 && Number(date[1]) >= curDay) {
                upcoming.push(taskname);
            }
            let tags = details.task_tags;
            for (let i = 0; i < tags.length; i++) {
                if (tags[i] in all_task_tags) {
                    all_task_tags[tags[i]] += 1;
                } else {
                    all_task_tags[tags[i]] = 1;
                }
                total_tags += 1;
            }
        }
        loading = false;
    }
        
    today = new Date();
    let day = today.getDay();
    let weekDates = [];
    for (let i = 0; i < 7; i++) {
        let date = new Date(today);
        date.setDate(today.getDate() - day + i);
        let formatted = `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;
        weekDates.push(formatted);
    }

    let times = ['12:00', '1:00', '2:00', '3:00', '4:00', '5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00', '12:00', '1:00', '2:00', '3:00', '4:00', '5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00']

    setup(user);
</script>

<style>

</style>


{#if loading}
    <p>Loading...</p>
{:else}
    <main>
        <div class="calendar">
            <div class="side-bar">
                <div class="name">
                    <img class="profile-picture" src={profile_picture} alt="profile picture from google account"/>
                    <h3 class="user-name">{user}</h3>
                </div>
                <div class="upcoming-events">
                    <h3>Upcoming Events</h3>
                    {#each upcoming as event}
                        <p class="task-name">{event}</p>
                        {#if Number(tasks[event].task_date.split('/')[1]) - curDay == 0}
                            <p class="due-date">Due Today</p>
                        {:else}
                            {#if Number(tasks[event].task_date.split('/')[1]) - curDay == 1}
                                <p class="due-date">Due in {Number(tasks[event].task_date.split('/')[1]) - curDay} day</p>
                            {:else}
                                <p class="due-date">Due in {Number(tasks[event].task_date.split('/')[1]) - curDay} days</p>
                            {/if}
                        {/if}
                    {/each}
                </div>
                <div class="mini-calendar">
                    <h3 class="month-year">{monthString}, {year}</h3>
                    {#each weekdays as day}
                        <label class="weekday-label">{day}</label>
                    {/each}
                    {#each chunckedDays as week, weekIndex}
                        <div class="weeks">
                            {#each week as day}
                                {#if Math.floor(day / 10) == 0}
                                    {#if weekIndex >= chunckedDays.length - 1}
                                        <label class="single-digit-day-next-month">{day}</label>
                                    {:else}
                                        {#if day == curDay}
                                            <label class="curday-single-digit"><span class="circular-background">{day}</span></label>
                                        {:else}
                                            <label class="single-digit-day">{day}</label>
                                        {/if}
                                    {/if}
                                {:else}
                                    {#if weekIndex <= 1}
                                        {#if day > 20}
                                            <label class="previous-month-days">{day}</label>
                                        {:else if day == curDay}
                                            <label class="curday"><span class="circular-background">{day}</span></label>
                                        {:else}
                                            <label class="weekday-number">{day}</label>
                                        {/if}
                                    {:else}
                                        {#if day == curDay}
                                            <label class="curday">{day}</label>
                                        {:else}
                                            <label class="weekday-number">{day}</label>
                                        {/if}
                                    {/if}
                                {/if}
                            {/each}
                        <!-- <br> -->
                        </div>
                    {/each}
                    </div>
                <div class="breakdown">
                    <h3 class="time-breakdown-inside">Time Breakdown</h3>
                    {#each Object.entries(all_task_tags) as [tag, num]}
                        <p>{tag}: {num}</p>
                    {/each}
                </div>
                <div class="notes">
                    <h3>Notes</h3>
                    {#each Object.entries(notes) as [title, note]}
                        <h4>{title}:</h4>
                        <p>{note.note_description || note}</p>
                        <div class="resolve-div"><button class="resolve-note-btn" onclick={() => delete_note(title)}>Resolve</button></div>
                    {/each}
                    <br>
                    <button class="note-button" onclick={(() => (show_note_modal = true))}>Add Note</button>
                    {#if show_note_modal}
                        <Notes_Modal bind:show_note_modal>
                            {#snippet header()}
                                <h2>Add Note</h2>
                            {/snippet}
                            <div class="note-container">   
                                <input class="note-title" placeholder="Note Title" bind:value={note_title_text_input} />
                                <input class="note-contents" placeholder="Note Contents" bind:value={note_description_text_input} />
                                <!-- <button onclick={() => {add_note(note_title_text_input, note_description_text_input); show_note_modal = false}}>Submit</button> -->
                            </div>
                            <button class="note-submit-btn" onclick={() => {add_note(note_title_text_input, note_description_text_input); show_note_modal = false}}>Submit</button>
                            <button class="close-button" onclick={() => show_note_modal = false}>Close</button>
                            
                        </Notes_Modal>
                    {/if}
                </div>
            </div>


            <div class="main-calendar-exclude">
                <div class="calendar-header">
                    <h2 class = "month-year">{monthString}, {year}</h2>
                    <div class="date-buttons">
                        <button class="indv-date-buttons" class:curr_tab={calendar_view === 1} onclick={() => calendar_view = 1}>Month</button>
                        <button class="indv-date-buttons" class:curr_tab={calendar_view === 2} onclick={() => calendar_view = 2}>Week</button>
                        <button class="indv-date-buttons" class:curr_tab={calendar_view === 3} onclick={() => calendar_view = 3}>Day</button>
                    </div>
                </div>
                <div class="main-calendar">
                    <!-- <div class = "week-headings-only"> -->
                    {#if calendar_view == 1}
                    <div class = "week-headings-only">
                        {#each Array(7) as _, index (index)}
                            {#if weekday == index}
                                <div class="week-headings" style="--background_color: rgba(104, 125, 49, .8)">
                                    <h3 class = "weekdays">{weekdays_spelled_out[index]}</h3>
                                </div>
                            {:else}
                                <div class="week-headings" style="--row_index: {1}; --col_index: {index + 1}">
                                    <h3 class = "weekdays">{weekdays_spelled_out[index]}</h3>
                                </div>
                            {/if}
                        {/each}
                    </div>
                    {/if}                    
                    {#if calendar_view == 1}
                        <div class="calendar-dates">
                            {#each Array(5) as _, row (row)}
                                {#each Array(7) as _, col (col)}
                                    {#if row == 0}
                                        {#if mainCalendarDays[row][col] > 8}
                                            <div class="calendar-box" style="--row_index: {row + 1}; --col_index: {col + 1}" onclick={(() => {add_task_date = String(month) + '/' + mainCalendarDays[row][col] + '/' + String(year); add_tasks_modal = true})}>
                                                <p class="main-calendar-previous-or-next-month-days">{mainCalendarDays[row][col]}</p>
                                                {#each Object.entries(tasks) as [title, details]}
                                                    {#if Number(details.task_date.split('/')[0]) == month && Number(details.task_date.split('/')[1]) == mainCalendarDays[row][col] && Number(details.task_date.split('/')[2]) == year}
                                                        <p class="calendar-task-month-page" style="--background_color: {details.task_color}; --text_color: white" onclick={() => {openTaskTitle = title; show_tasks_modal = true;}}>{title}</p>
                                                    {/if}
                                                {/each}
                                            </div>
                                        {:else}
                                            <div class="calendar-box" style="--row_index: {row + 1}; --col_index: {col + 1}" onclick={(() => {add_task_date = String(month + 1) + '/' + mainCalendarDays[row][col] + '/' + String(year); add_tasks_modal = true})}>
                                                <p class="main-calendar-days">{mainCalendarDays[row][col]}</p>
                                                {#each Object.entries(tasks) as [title, details]}
                                                    {#if Number(details.task_date.split('/')[0]) == month + 1 && Number(details.task_date.split('/')[1]) == mainCalendarDays[row][col] && Number(details.task_date.split('/')[2]) == year}
                                                        <p class="calendar-task-month-page" style="--background_color: {details.task_color}; --text_color: white" onclick={() => {openTaskTitle = title; show_tasks_modal = true;}}>{title}</p>
                                                    {/if}
                                                {/each}
                                            </div>
                                        {/if}
                                    {:else if row >= 4}
                                            {#if mainCalendarDays[row][col] < 15}
                                                <div class="calendar-box" style="--row_index: {row + 1}; --col_index: {col + 1}" onclick={(() => {add_task_date = String(month + 2) + '/' + mainCalendarDays[row][col] + '/' + String(year); add_tasks_modal = true})}>
                                                    <p class="main-calendar-previous-or-next-month-days">{mainCalendarDays[row][col]}</p>
                                                    {#each Object.entries(tasks) as [title, details]}
                                                        {#if Number(details.task_date.split('/')[0]) == month + 2 && Number(details.task_date.split('/')[1]) == mainCalendarDays[row][col] && Number(details.task_date.split('/')[2]) == year}
                                                            <p class="calendar-task-month-page" style="--background_color: {details.task_color}; --text_color: white" onclick={() => {openTaskTitle = title; show_tasks_modal = true;}}>{title}</p>
                                                        {/if}
                                                    {/each}
                                                </div>
                                            {:else}
                                                <div class="calendar-box" style="--row_index: {row + 1}; --col_index: {col + 1}" onclick={(() => {add_task_date = String(month + 1) + '/' + mainCalendarDays[row][col] + '/' + String(year); add_tasks_modal = true})}>
                                                    <p class="main-calendar-days">{mainCalendarDays[row][col]}</p>
                                                    {#each Object.entries(tasks) as [title, details]}
                                                        {#if Number(details.task_date.split('/')[0]) == month + 1 && Number(details.task_date.split('/')[1]) == mainCalendarDays[row][col] && Number(details.task_date.split('/')[2]) == year}
                                                            <p class="calendar-task-month-page" style="--background_color: {details.task_color}; --text_color: white" onclick={() => {openTaskTitle = title; show_tasks_modal = true;}}>{title}</p> 
                                                        {/if}
                                                    {/each}
                                                </div>
                                            {/if}
                                    {:else}
                                        <div class="calendar-box" style="--row_index: {row + 1}; --col_index: {col + 1}" onclick={(() => {add_task_date = String(month + 1) + '/' + mainCalendarDays[row][col] + '/' + String(year); add_tasks_modal = true})}>
                                            <p class="main-calendar-days">{mainCalendarDays[row][col]}</p>
                                            {#each Object.entries(tasks) as [title, details]}
                                                {#if Number(details.task_date.split('/')[0]) == month + 1 && Number(details.task_date.split('/')[1]) == mainCalendarDays[row][col] && Number(details.task_date.split('/')[2]) == year}
                                                    <p class="calendar-task-month-page" style="--background_color: {details.task_color}; --text_color: white" onclick={() => {openTaskTitle = title; show_tasks_modal = true;}}>{title}</p>
                                                {/if}
                                            {/each}
                                        </div>          
                                    {/if}
                                {/each}
                            {/each}
                        </div>                
                    {:else if calendar_view == 2}
                        <div class="calendar-grid">
                            <!-- Weekday Headings -->
                            {#each weekDates as weekAndDate, index}
                                <div class="calendar-cell heading"
                                    style="
                                        grid-row: 1;
                                        grid-column: {index + 2};
                                    ">
                                    <h3 class="week-header">{weekAndDate.split('/')[1]} {weekdays_spelled_out[index]}</h3>
                                </div>
                            {/each}

                            <!-- Time Labels (1st column) -->
                            {#each times as time, index}
                                <div class="calendar-cell time-label day-times"
                                    style="
                                        grid-row: {index + 2};
                                        grid-column: 1;
                                    ">
                                    <p>{time}</p>
                                </div>
                            {/each}
                            

                            <!-- Task Blocks -->
                            {#each weekDates as weekAndDate, index}
                                <div class="week-add-task-box" style="--col: {index + 2}" onclick={() => {add_task_date = String(month + 1) + '/' + weekAndDate.split('/')[1] + '/' + String(year); add_tasks_modal = true}}></div>
                                {#each getPositionedTasks(tasks, weekAndDate) as task}
                                    <div
                                        class="calendar-task-week-page"
                                        style="
                                            grid-row-start: {task.start + 2};
                                            grid-row-end: {task.end + 2};
                                            grid-column-start: {index + 2};
                                            grid-column-end: {index + 3};
                                            background-color: {task.details.task_color};
                                            transform: translateX({(task.slot / task.totalSlots) * 100}%);
                                            width: {100 / task.totalSlots}%;
                                        "
                                        onclick={() => {
                                            openTaskTitle = task.title;
                                            show_tasks_modal = true;
                                        }}>
                                        <p>{task.title}</p>
                                    </div>
                                {/each}
                                
                            {/each}
                        </div>
                        <!-- {/each} -->
                    {:else if calendar_view == 3}
                        <!-- <div class="day-headings-only">
                            <h3 class="day-box">
                                {#each Object.entries(tasks) as [title, details]}
                                    {#if Number(details.task_date.split('/')[0]) == current_viewing_month + 1 && Number(details.task_date.split('/')[1]) == current_viewing_day && Number(details.task_date.split('/')[2]) == current_viewing_year}
                                        <p class="calendar-task-day-page" style="--background_color: {details.task_color}; --text_color: white" onclick={() => {openTaskTitle = title; show_tasks_modal = true;}}>{title}</p>
                                    {/if}
                                {/each}
                            </h3>
                        </div> -->
                        <div class="day-calendar-grid" onclick={() => {add_task_date = String(month + 1) + '/' + current_viewing_day + '/' + String(year); add_tasks_modal = true}}>
                            <!-- Weekday Heading -->
                            <div class="day-header">{current_viewing_day} {weekdays_spelled_out[weekday]}</div>

                            {#each times as time, index}
                                <div class="calendar-cell time-label day-times" style="grid-row: {index + 2};">{time}</div>
                            {/each}

                            {#each getPositionedTasks(tasks, weekDates[weekday]) as task}
                                <div
                                class="calendar-task-day-page"
                                style="
                                    grid-row-start: {task.start + 2};
                                    grid-row-end: {task.end + 2};
                                    background-color: {task.details.task_color};
                                    transform: translateX({(task.slot / task.totalSlots) * 100}%);
                                    width: {100 / task.totalSlots}%;
                                "
                                onclick={() => {
                                    openTaskTitle = task.title;
                                    show_tasks_modal = true;
                                }}>
                                <p>{task.title}</p>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            </div>
        </div>
        {#if show_tasks_modal && openTaskTitle}
            {#key openTaskTitle}    
                <Tasks_Modal bind:show_tasks_modal bind:openTaskTitle bind:add_tasks_modal>
                    {#snippet header()}
                    <!-- <h2>Add a Task</h2> -->
                    {/snippet}
                    {@const details = tasks[openTaskTitle]}
                    <div class="task-container">
                        <!-- <h4>Task Title</h4> -->
                        <input class="task-title" placeholder="Task Title" bind:value={openTaskTitle}/>
                        <!-- <h4>Task Label</h4> -->
                        <input class="task-label" placeholder="Add Label" bind:value={details.task_label}/>
                        <!-- <h4>Task Date</h4> -->

                        <input class="task-tag" placeholder="Add Tag" bind:value={details.task_tags}/>

                            <span class="time-elements">
                            <img src="/clock.svg" alt="Clock Icon" class="clock-icon"/>
                            <input class="task-date" placeholder="Date" bind:value={details.task_date}/>
                            <span>:</span>
                            <input class="start-time" placeholder="Start Time" bind:value={details.task_start_time}/>
                            <span>-</span>
                            <input class="end-time" placeholder="End Time" bind:value={details.task_end_time}/>  
                            </span>
                
                        <!-- <h4>Task Description</h4> -->
                            <span class="notes-elements">
                            <img src="/notes.svg" alt="Notes Icon" class="notes-icon"/>
                            <span>Notes</span>
                            <input class="task-description" placeholder="Add Description" bind:value={details.task_description}/>
                            </span>
                        
                        <!-- <h4>Task Location</h4> -->
                        <span class="location-elements">
                            <img src="/location.svg" alt="Location Icon" class="location-icon"/>
                            <span>Location</span>
                            <input class="location-description" placeholder="Add Location" bind:value={details.task_location}/>
                        </span>

                        <span class="task-color-elements">
                            <img src="/color_picker.svg" alt="Color Icon" class="color-icon"/>
                            <span>Add Color</span>
                            <input class="color-picker" placeholder="Enter Color" bind:value={details.task_color}/>
                        </span>
                        <!-- <h4>Task Color</h4> -->
                        <div class="priority-container">
                            <img src="/priority.svg" alt="Priority Icon" class ="priority-icon"/>
                            <h4 class="priority-name">Task Priority</h4>
                            <input class="prioirty-input" placeholder="Enter Priority" bind:value={details.task_priority}/>
                        </div>
                        <!-- <h4 class=>Task Priority</h4>
                        <input bind:value={details.task_priority}/> -->
                        <button class="submit-button" onclick={() => add_task(openTaskTitle, details.task_description, details.task_location, details.task_color, details.task_label, details.task_start_time, details.task_end_time, details.task_date, details.task_tags, details.task_priority)}>Submit</button>
                        <button class="close-button" onclick={() => {show_tasks_modal = false; openTaskTitle = null; add_tasks_modal = false;}}>Close</button>
                        <button class="delete-button" onclick={() => delete_task(openTaskTitle)}>Delete</button>
                    </div>
                </Tasks_Modal>
            {/key}
        {/if}
        {#if add_tasks_modal && add_task_date && !show_tasks_modal}
            {#key add_task_date}
                <Add_Task_Modal bind:add_tasks_modal bind:add_task_date>
                    {#snippet header()}
                        <!-- <h2>Add a Task</h2> -->
                    {/snippet}
                    <div class="task-container">
                        <!-- <h4>Task Title</h4> -->
                        <input class="task-title" placeholder="Task Title" bind:value={task_title_text_input}/>
                        <!-- <h4>Task Label</h4> -->
                        <input class="task-label" placeholder="Add Label" bind:value={task_label_text_input}/>
                        <!-- <h4>Task Date</h4> -->

                        <input class="task-tag" placeholder="Add Tag" bind:value={task_tags_text_input}/>

                            <span class="time-elements">
                            <img src="/clock.svg" alt="Clock Icon" class="clock-icon"/>
                            <input class="task-date" placeholder="Date" bind:value={add_task_date}/>
                            <span>:</span>
                            <input class="start-time" placeholder="Start Time" bind:value={task_start_time_text_input}/>
                            <span>-</span>
                            <input class="end-time" placeholder="End Time" bind:value={task_end_time_text_input}/>  
                            </span>
                
                        <!-- <h4>Task Description</h4> -->
                            <span class="notes-elements">
                            <img src="/notes.svg" alt="Notes Icon" class="notes-icon"/>
                            <span>Notes</span>
                            <input class="task-description" placeholder="Add Description" bind:value={task_description_text_input}/>
                            </span>
                        
                        <!-- <h4>Task Location</h4> -->
                        <span class="location-elements">
                            <img src="/location.svg" alt="Location Icon" class="location-icon"/>
                            <span>Location</span>
                            <input class="location-description" placeholder="Add Location" bind:value={task_location_text_input}/>
                        </span>

                        <span class="task-color-elements">
                            <img src="/color_picker.svg" alt="Color Icon" class="color-icon"/>
                            <span>Add Color</span>
                            <input class="color-picker" placeholder="Enter Color" bind:value={task_color_text_input}/>
                        </span>
                        <!-- <h4>Task Color</h4> -->
        
                        <!-- <h4>Task Priority</h4>-->

                        <span class="priority-elements">
                            <img src="priority.svg" alt="Priority Icon" class="priority-icon"/>
                            <span>Priority</span>
                            <input class = "priority" placeholder="Enter Priority" bind:value={task_priority_text_input}/>
                        </span>
                        
                        <button class="submit-button" onclick={() => add_task(task_title_text_input, task_description_text_input, task_location_text_input, task_color_text_input, task_label_text_input, task_start_time_text_input, task_end_time_text_input, add_task_date, task_tags_text_input, task_priority_text_input)}>Submit</button>
                        <button class="close-button" onclick={() => add_tasks_modal = false}>Close</button>
                        
                        <!-- <button onclick={() => dialog.close()}>Close</button> -->
                    </div>
                </Add_Task_Modal>
            {/key}
        {/if}
    </main>
{/if}