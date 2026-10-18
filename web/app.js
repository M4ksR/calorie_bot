const tg = window.Telegram?.WebApp;

const loading = document.getElementById("loading");
const error = document.getElementById("error");
const errorText = document.getElementById("error-text");
const content = document.getElementById("content");
const retryButton = document.getElementById("retry-button");
const addFoodButton = document.getElementById("add-food-button");
const sheetBackdrop = document.getElementById("sheet-backdrop");
const addSheet = document.getElementById("add-sheet");
const sheetClose = document.getElementById("sheet-close");
const sheetTitle = document.getElementById("sheet-title");
const sheetEyebrow = document.getElementById("sheet-eyebrow");
const addMenu = document.getElementById("add-menu");
const savedFoodsScreen = document.getElementById("saved-foods-screen");
const weightScreen = document.getElementById("weight-screen");
const savedFoodsButton = document.getElementById("saved-foods-button");
const savedFoodsBack = document.getElementById("saved-foods-back");
const weightBack = document.getElementById("weight-back");
const savedFoodsList = document.getElementById("saved-foods-list");
const savedFoodsEmpty = document.getElementById("saved-foods-empty");
const weightInput = document.getElementById("weight-input");
const confirmAddFood = document.getElementById("confirm-add-food");

let selectedSavedFood = null;

if (tg) {
    tg.ready();
    tg.expand();
}

function roundValue(value) {
    return Math.round(Number(value) || 0);
}

function roundMacro(value) {
    return Math.round((Number(value) || 0) * 10) / 10;
}

function getProgress(eaten, daily) {
    daily = Number(daily) || 0;
    eaten = Number(eaten) || 0;

    if (daily <= 0) return 0;
    return Math.min((eaten / daily) * 100, 100);
}

function setText(id, value) {
    document.getElementById(id).textContent = value;
}

function setProgress(id, eaten, daily) {
    document.getElementById(id).style.width = `${getProgress(eaten, daily)}%`;
}

function showError(message) {
    loading.classList.add("hidden");
    content.classList.add("hidden");
    addFoodButton.classList.add("hidden");
    error.classList.remove("hidden");
    errorText.textContent = message;
}

function showContent() {
    loading.classList.add("hidden");
    error.classList.add("hidden");
    content.classList.remove("hidden");
    addFoodButton.classList.remove("hidden");
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            "X-Telegram-Init-Data": tg.initData
        }
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
}

function renderDashboard(data) {
    const daily = data.daily;
    const eaten = data.eaten;
    const left = data.left;

    const dailyCalories = roundValue(daily.calories);
    const eatenCalories = roundValue(eaten.calories);
    const leftCalories = roundValue(left.calories);
    const calorieProgress = getProgress(eaten.calories, daily.calories);

    setText("streak", roundValue(data.streak));
    setText("calories-eaten", eatenCalories);
    setText("calories-daily", dailyCalories);

    if (leftCalories >= 0) {
        setText("calories-left", `${leftCalories} ккал`);
        setText("calories-status", "Держим темп");
    }
    else {
        setText("calories-left", `${Math.abs(leftCalories)} ккал`);
        setText("calories-status", "Сверх нормы");
    }

    document.getElementById("calorie-ring").style.background = `conic-gradient(var(--accent) ${calorieProgress}%, var(--line) ${calorieProgress}% 100%)`;

    setText("protein-eaten", roundValue(eaten.protein));
    setText("protein-daily", roundValue(daily.protein));
    setProgress("protein-progress", eaten.protein, daily.protein);

    setText("fat-eaten", roundValue(eaten.fat));
    setText("fat-daily", roundValue(daily.fat));
    setProgress("fat-progress", eaten.fat, daily.fat);

    setText("carbs-eaten", roundValue(eaten.carbs));
    setText("carbs-daily", roundValue(daily.carbs));
    setProgress("carbs-progress", eaten.carbs, daily.carbs);
}

function renderTodayFoods(data) {
    const foodList = document.getElementById("food-list");
    const foodEmpty = document.getElementById("food-empty");

    foodList.innerHTML = "";
    setText("food-count", `${data.length} позиций`);

    if (data.length === 0) {
        foodEmpty.classList.remove("hidden");
        return;
    }

    foodEmpty.classList.add("hidden");

    data.forEach(food => {
        const card = document.createElement("article");
        card.className = "food-card";

        const info = document.createElement("div");
        info.className = "food-info";

        const name = document.createElement("strong");
        name.textContent = food.name;

        const weight = document.createElement("span");
        weight.textContent = `${roundValue(food.weight)} г`;

        const calories = document.createElement("strong");
        calories.className = "food-calories";
        calories.textContent = `${roundValue(food.calories)} ккал`;

        const actions = document.createElement("div");
        actions.className = "food-actions";

        const deleteButton = document.createElement("button");
        deleteButton.className = "food-delete";
        deleteButton.type = "button";
        deleteButton.textContent = "×";
        deleteButton.setAttribute("aria-label", `Удалить ${food.name}`);
        deleteButton.addEventListener("click", () => deleteFood(food, deleteButton));

        actions.appendChild(calories);
        actions.appendChild(deleteButton);
        info.appendChild(name);
        info.appendChild(weight);
        card.appendChild(info);
        card.appendChild(actions);
        foodList.appendChild(card);
    });
}

function getDayLabel(dateString) {
    const date = new Date(`${dateString}T00:00:00`);
    return new Intl.DateTimeFormat("ru-RU", {weekday: "short"})
        .format(date)
        .replace(".", "");
}

function renderWeekly(data) {
    const chart = document.getElementById("weekly-chart");
    chart.innerHTML = "";

    const maxCalories = Math.max(...data.map(day => Number(day.calories) || 0), 1);

    data.forEach(day => {
        const calories = roundValue(day.calories);
        const height = calories === 0 ? 3 : Math.max((calories / maxCalories) * 100, 8);

        const column = document.createElement("div");
        column.className = "chart-column";

        const value = document.createElement("div");
        value.className = "chart-value";
        value.textContent = calories;

        const barArea = document.createElement("div");
        barArea.className = "chart-bar-area";

        const bar = document.createElement("div");
        bar.className = "chart-bar";
        bar.style.height = `${height}%`;
        bar.title = `${day.date}: ${calories} ккал`;

        const label = document.createElement("div");
        label.className = "chart-label";
        label.textContent = getDayLabel(day.date);

        barArea.appendChild(bar);
        column.appendChild(value);
        column.appendChild(barArea);
        column.appendChild(label);
        chart.appendChild(column);
    });
}

function showSheetScreen(screen) {
    addMenu.classList.add("hidden");
    savedFoodsScreen.classList.add("hidden");
    weightScreen.classList.add("hidden");
    screen.classList.remove("hidden");
}

function openAddSheet() {
    selectedSavedFood = null;
    sheetEyebrow.textContent = "Добавление еды";
    sheetTitle.textContent = "Что добавим?";
    showSheetScreen(addMenu);
    sheetBackdrop.classList.remove("hidden");
    addSheet.classList.remove("hidden");
    addSheet.setAttribute("aria-hidden", "false");
    document.body.classList.add("sheet-open");
    tg?.HapticFeedback?.impactOccurred("light");
}

function closeAddSheet() {
    sheetBackdrop.classList.add("hidden");
    addSheet.classList.add("hidden");
    addSheet.setAttribute("aria-hidden", "true");
    document.body.classList.remove("sheet-open");
}

function renderSavedFoods(data) {
    savedFoodsList.innerHTML = "";

    if (data.length === 0) {
        savedFoodsEmpty.classList.remove("hidden");
        return;
    }

    savedFoodsEmpty.classList.add("hidden");

    data.forEach(food => {
        const row = document.createElement("button");
        row.className = "saved-food-row";
        row.type = "button";

        const info = document.createElement("div");
        const name = document.createElement("strong");
        const macros = document.createElement("span");
        const arrow = document.createElement("b");

        name.textContent = food.name;
        macros.textContent = `${roundValue(food.calories)} ккал · Б ${roundMacro(food.protein)} · Ж ${roundMacro(food.fat)} · У ${roundMacro(food.carbs)}`;
        arrow.textContent = "›";

        info.appendChild(name);
        info.appendChild(macros);
        row.appendChild(info);
        row.appendChild(arrow);
        row.addEventListener("click", () => openWeightScreen(food));
        savedFoodsList.appendChild(row);
    });
}

async function openSavedFoods() {
    sheetEyebrow.textContent = "Добавление еды";
    sheetTitle.textContent = "Сохранённые";
    showSheetScreen(savedFoodsScreen);
    savedFoodsList.innerHTML = "";
    savedFoodsEmpty.classList.add("hidden");

    try {
        const data = await apiRequest("/api/saved-foods");
        renderSavedFoods(data);
    }
    catch (err) {
        console.error(err);
        tg?.HapticFeedback?.notificationOccurred("error");
        tg?.showAlert?.("Не удалось загрузить сохранённые продукты.");
        showSheetScreen(addMenu);
    }
}

function updateFoodPreview() {
    if (!selectedSavedFood) return;

    const weight = Number(weightInput.value) || 0;
    const coef = weight / 100;

    setText("preview-calories", `${roundValue(selectedSavedFood.calories * coef)} ккал`);
    setText("preview-protein", `${roundMacro(selectedSavedFood.protein * coef)} г`);
    setText("preview-fat", `${roundMacro(selectedSavedFood.fat * coef)} г`);
    setText("preview-carbs", `${roundMacro(selectedSavedFood.carbs * coef)} г`);
    confirmAddFood.disabled = weight <= 0;
}

function openWeightScreen(food) {
    selectedSavedFood = food;
    sheetEyebrow.textContent = "Сохранённый продукт";
    sheetTitle.textContent = "Укажи вес";
    setText("selected-food-name", food.name);
    setText("selected-food-base", `${roundValue(food.calories)} ккал / 100 г`);
    weightInput.value = 100;
    showSheetScreen(weightScreen);
    updateFoodPreview();
    setTimeout(() => weightInput.focus(), 120);
}

async function addSelectedFood() {
    if (!selectedSavedFood) return;

    const weight = Number(weightInput.value);
    if (!Number.isFinite(weight) || weight <= 0) return;

    confirmAddFood.disabled = true;
    confirmAddFood.textContent = "Добавляю...";

    try {
        await apiRequest(`/api/saved-foods/${selectedSavedFood.id}/add`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({weight})
        });

        tg?.HapticFeedback?.notificationOccurred("success");
        closeAddSheet();
        await refreshData();
    }
    catch (err) {
        console.error(err);
        tg?.HapticFeedback?.notificationOccurred("error");
        tg?.showAlert?.("Не удалось добавить продукт. Попробуй ещё раз.");
    }
    finally {
        confirmAddFood.disabled = false;
        confirmAddFood.textContent = "Добавить в дневник";
    }
}

function askDelete(foodName) {
    const message = `Удалить «${foodName}» из дневника?`;

    if (tg?.showConfirm) {
        return new Promise(resolve => tg.showConfirm(message, resolve));
    }

    return Promise.resolve(window.confirm(message));
}

async function deleteFood(food, button) {
    const confirmed = await askDelete(food.name);
    if (!confirmed) return;

    button.disabled = true;

    try {
        await apiRequest(`/api/today-foods/${food.id}`, {method: "DELETE"});
        tg?.HapticFeedback?.notificationOccurred("success");
        await refreshData();
    }
    catch (err) {
        console.error(err);
        button.disabled = false;
        tg?.HapticFeedback?.notificationOccurred("error");
        tg?.showAlert?.("Не удалось удалить запись. Попробуй ещё раз.");
    }
}

async function refreshData() {
    const [dashboard, weekly, todayFoods] = await Promise.all([
        apiRequest("/api/dashboard"),
        apiRequest("/api/weekly"),
        apiRequest("/api/today-foods")
    ]);

    renderDashboard(dashboard);
    renderWeekly(weekly);
    renderTodayFoods(todayFoods);
}

async function loadData() {
    loading.classList.remove("hidden");
    error.classList.add("hidden");
    content.classList.add("hidden");
    addFoodButton.classList.add("hidden");

    if (!tg || !tg.initData) {
        showError("Открой эту страницу как Mini App внутри Telegram.");
        return;
    }

    try {
        await refreshData();
        showContent();
    }
    catch (err) {
        console.error(err);
        showError("Сервер не принял данные Telegram или временно недоступен.");
    }
}

retryButton.addEventListener("click", loadData);
addFoodButton.addEventListener("click", openAddSheet);
sheetClose.addEventListener("click", closeAddSheet);
sheetBackdrop.addEventListener("click", closeAddSheet);
savedFoodsButton.addEventListener("click", openSavedFoods);
savedFoodsBack.addEventListener("click", () => {
    sheetEyebrow.textContent = "Добавление еды";
    sheetTitle.textContent = "Что добавим?";
    showSheetScreen(addMenu);
});
weightBack.addEventListener("click", openSavedFoods);
weightInput.addEventListener("input", updateFoodPreview);
confirmAddFood.addEventListener("click", addSelectedFood);
document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !addSheet.classList.contains("hidden")) closeAddSheet();
});

loadData();
