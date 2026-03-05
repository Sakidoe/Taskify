<script>
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher(); // Create an event dispatcher

    function closeForm() {
        dispatch("close");
    }
    let showTaskBox = true; // Controls the visibility of the task box

    let checked = false;
    let allTags = [
        { name: 'school', checked: false },
        { name: 'work', checked: false },
        { name: 'tag', checked: false },
        { name: 'personal', checked: false },
        { name: 'tag', checked: false },
        { name: 'tag', checked: false }
    ];

    let priorityTags = [
        { name: 'low', checked: false },
        { name: 'medium', checked: false },
        { name: 'high', checked: false }
    ];

    // let userID = "jon";
    export let userID;
    let selectedTags = [];
    let taskName = "";
    let taskDescription = "";
    let taskDate = "";
    let taskLocation = "";
    let taskStartTime = "";
    let taskEndTime = "";
    let taskColor = "";
    let taskLabel = "";
    let priorityOptions = ['low', 'medium', 'high'];
    let selectedPriority = ''; 
    let feedback = "";

    async function createTask() {
        selectedTags = allTags
            .filter((t) => t.checked)
            .map((t) => t.name);

        const payload = {
            user_id: userID,
            task_name: taskName,
            task_description: taskDescription,
            task_tags: selectedTags,
            task_priority: selectedPriority,
            task_date: taskDate,
            task_start_time: taskStartTime,
            task_end_time: taskEndTime,
            task_location: taskLocation,
            task_color: taskColor,
            task_label: taskLabel
        };

        try {
            const res = await fetch("http://localhost:8000/create_task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            if (data.success) {
                feedback = "Task created successfully";
                resetTaskBox();
                showTaskBox = false; // Hide the task box after submission

                // Emit the custom event to notify the parent
                dispatch("taskCreated");
            } else {
                feedback = "Unexpected response: " + JSON.stringify(data);
            }
        } catch (err) {
            feedback = "Error: " + err.message;
        }
    }

    function resetTaskBox() {
        taskName = "";
        taskDescription = "";
        taskDate = "";
        allTags.forEach((t) => (t.checked = false));
        selectedTags = [];
        selectedPriority = '';
        taskStartTime = "";
        taskEndTime = "";
        taskLocation = "";
        taskColor = "";
        taskLabel = "";
    }
</script>

<style>
    input, textarea, label{
        font-family: Playfair Display;
        font-size: 16px;
        font-weight: 400;
    }
    .blur {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(217, 217, 217, 0.80);
        z-index: 1;
    }
    .close {
        position: absolute;
        top: 8px;
        right: 8px;
        text-decoration: none;
    }
    .closeButton {
        all: unset; 
        cursor: pointer;
    }
    .background {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        height: 60vh;
        width: 60%;
        background-color: white;
        display: flex;
        flex-direction: column;
        padding: 32px;
        border: 1px solid #687D31CC;
        z-index: 2;
    }

    .inputBox {
        display: block;
        width: 100%;              
        padding: 16px;
        background-color: #687D31CC;
        border: none;
        border-radius: 8px;
        box-sizing: border-box;
    }
    input::placeholder {
        color: white;          
    }
    input {
        color: white;
    }
    textarea::placeholder {
        color: white;
    }
    .commentBox {
        display: block;
        margin-top: 16px;
        margin-bottom: 16px;
        width: 100%; 
        height: 30%;             
        padding: 16px;
        background-color: #687D31CC;
        border: none;
        border-radius: 8px;
        box-sizing: border-box;
        color: white;
    }

    .tagContainer {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        margin: 8px;
    }
    .tagItem {
        flex: 1;
    }
    .tagLabel{
        margin: 0px;
    }

    .buttonContainer {
        position: absolute;
        width: 20%;
        bottom: 16px;
        right: 16px;
        padding: 16px;
        margin-top: 16px;
    }
    .submitButton {
        display: block;
        width: 100%;
        padding: 16px;
        background-color: #687D31CC;
        border: none;
        border-radius: 8px;
        color: white;
        cursor: pointer;
        font-size: 16px;
        font-weight: 400;
        font-style: normal;
    }
    
    .timeContainer {
        display:flex;
        flex-direction: row;
        width: 50%;
    }
    #date {
        /* height: 50%; */
        width: 50%;
        margin-right: 8px;
        background-color: white;
        border: 2px solid #687D31CC;
        border-radius: 8px;
        box-sizing: border-box;
        color: black;
    }
    #timeStart, #timeEnd {
        width: 50%;
        /* height: 50%; */
        margin-right: 8px;
        margin-left: 8px;
        background-color: white;
        border: 2px solid #687D31CC;
        border-radius: 8px;
        box-sizing: border-box;
        color: black;
    }

    .locationContainer input {
        display: flex;
        flex-direction: row;
        width: 50%;
        margin-top: 16px;
    }
    #location {
        padding: 16px;
        background-color: white;
        border: 2px solid #687D31CC;
        border-radius: 8px;
        box-sizing: border-box;
        color: black;
    }
    #location::placeholder {
        color: #8B8B8B;
    }
</style>

<main>
    {#if showTaskBox}
    <div class="blur">
        <div class="background">
            <div class="close">
                <button
                    class="closeButton"
                    type="button"
                    on:click={() => {
                        console.log('Close button clicked');
                        resetTaskBox();
                        showTaskBox = false; // Hide the task box on close
                        closeForm
                    }}
                >
                    X
                </button>
            </div>
            <input
                class="inputBox"
                type="text"
                placeholder="enter task name here"
                bind:value={taskName}
                required
            />
            <textarea
                class="commentBox"
                placeholder="enter any comments, or task description"
                bind:value={taskDescription}
                required
            />
            <h3 class="tagLabel">tags:</h3>
            <div class="tagContainer">
                {#each allTags.slice(0,3) as tag}
                    <div class="tagItem">
                        <label>
                            <input
                                type="checkbox"
                                bind:checked={tag.checked}
                                on:change={() => {
                                    if (tag.checked) {
                                        selectedTags.push(tag.name);
                                    } else {
                                        selectedTags = selectedTags.filter(
                                            (t) => t !== tag.name
                                        );
                                    }
                                }}
                            />
                            {tag.name}
                        </label>
                    </div>
                {/each}
            </div>
            <div class="tagContainer">
                {#each allTags.slice(3) as tag}
                    <div class="tagItem">
                        <label>
                            <input
                                type="checkbox"
                                bind:checked={tag.checked}
                                on:change={() => {
                                    if (tag.checked) {
                                        selectedTags.push(tag.name);
                                    } else {
                                        selectedTags = selectedTags.filter(
                                            (t) => t !== tag.name
                                        );
                                    }
                                }}
                            />
                            {tag.name}
                        </label>
                    </div>
                {/each}
            </div>
            <h3 class="tagLabel" >priority:</h3>
            <div class="tagContainer">
                {#each priorityTags as tag}
                    <div class="tagItem">
                        <label>
                            <input
                                class="tagItem"
                                type="radio"
                                value={tag.name}
                                bind:group={selectedPriority}
                                on:change={() => {
                                    if (tag.checked) {
                                        selectedTags.push(tag.name);
                                    } else {
                                        selectedTags = selectedTags.filter(
                                            (t) => t !== tag.name
                                        );
                                    }
                                }}
                            />
                            {tag.name}
                        </label>
                    </div>
                {/each}
            </div>
            <div class="timeContainer">
                <input
                    class="inputBox"
                    id = "date"
                    type="date"
                    placeholder="enter due date here"
                    bind:value={taskDate}
                    required
                />
                <input
                    class="inputBox"
                    id = "timeStart"
                    type="time"
                    placeholder="enter start time here"
                    bind:value={taskStartTime}
                    required
                />
                <p>-</p>
                <input
                    class="inputBox"
                    id = "timeEnd"
                    type="time"
                    placeholder="enter end time here"
                    bind:value={taskEndTime}
                    required
                />
            </div>
            <div class="locationContainer">
                <input
                    class="inputBox"
                    id="location"
                    type="text"
                    placeholder="Add Location"
                    bind:value={taskLocation}
                />

            </div>
            <div class="buttonContainer">
                <button
                    class="submitButton"
                    type="button"
                    on:click={() => {
                        console.log('Task submitted with tags:', selectedTags);
                        createTask();
                        showTaskBox = false; // Hide the task box after submission
                        closeForm();
                    }}
                    disabled={!taskName}
                >
                    Submit
                </button>
            </div>
        </div>
    </div>
    {/if}
</main>