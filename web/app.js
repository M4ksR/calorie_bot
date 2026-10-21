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
const searchScreen = document.getElementById("search-screen");
const weightScreen = document.getElementById("weight-screen");
const aiScreen = document.getElementById("ai-screen");
const manualScreen = document.getElementById("manual-screen");
const savedFoodsButton = document.getElementById("saved-foods-button");
const searchFoodButton = document.getElementById("search-food-button");
const aiFoodButton = document.getElementById("ai-food-button");
const manualFoodButton = document.getElementById("manual-food-button");
const savedFoodsList = document.getElementById("saved-foods-list");
const savedFoodsEmpty = document.getElementById("saved-foods-empty");
const searchInput = document.getElementById("search-input");
const searchSubmit = document.getElementById("search-submit");
const searchInfo = document.getElementById("search-info");
const searchResults = document.getElementById("search-results");
const searchEmpty = document.getElementById("search-empty");
const searchMore = document.getElementById("search-more");
const weightBack = document.getElementById("weight-back");
const weightInput = document.getElementById("weight-input");
const confirmAddFood = document.getElementById("confirm-add-food");
const aiInput = document.getElementById("ai-input");
const aiEstimate = document.getElementById("ai-estimate");
const aiResults = document.getElementById("ai-results");
const aiAdd = document.getElementById("ai-add");
const manualName = document.getElementById("manual-name");
const manualWeight = document.getElementById("manual-weight");
const manualCalories = document.getElementById("manual-calories");
const manualProtein = document.getElementById("manual-protein");
const manualFat = document.getElementById("manual-fat");
const manualCarbs = document.getElementById("manual-carbs");
const manualAdd = document.getElementById("manual-add");

let selectedFood = null;
let selectedFoodMode = null;
let previousScreen = null;
let searchPage = 0;
let searchTotal = 0;
let searchQuery = "";
let estimatedFoods = [];

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
        const calories = Number(day.calories) || 0;
        const height = Math.max((calories / maxCalories) * 100, calories > 0 ? 4 : 0);

        const column = document.createElement("div");
        column.className = "chart-column";

        const value = document.createElement("div");
        value.className = "chart-value";
        value.textContent = roundValue(calories);

        const barArea = document.createElement("div");
        barArea.className = "chart-bar-area";

        const bar = document.createElement("div");
        bar.className = "chart-bar";
        bar.style.height = `${height}%`;

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
    [addMenu, savedFoodsScreen, searchScreen, weightScreen, aiScreen, manualScreen]
        .forEach(item => item.classList.add("hidden"));

    screen.classList.remove("hidden");
}

function setSheetHeader(eyebrow, title) {
    sheetEyebrow.textContent = eyebrow;
    sheetTitle.textContent = title;
}

function showMainAddMenu() {
    setSheetHeader("Добавление еды", "Что добавим?");
    showSheetScreen(addMenu);
}

function openAddSheet() {
    showMainAddMenu();
    addSheet.classList.remove("hidden");
    sheetBackdrop.classList.remove("hidden");
    addSheet.setAttribute("aria-hidden", "false");
    document.body.classList.add("sheet-open");
    tg?.HapticFeedback?.impactOccurred("light");
}

function closeAddSheet() {
    addSheet.classList.add("hidden");
    sheetBackdrop.classList.add("hidden");
    addSheet.setAttribute("aria-hidden", "true");
    document.body.classList.remove("sheet-open");
    selectedFood = null;
    selectedFoodMode = null;
    previousScreen = null;
}

function getSourceName(source) {
    const names = {
        magnit: "Магнит",
        lenta: "Лента",
        usda: "USDA",
        perek: "Perek"
    };

    return names[source] || "База";
}

function getSourceClass(source) {
    return `source-${source || "other"}`;
}

function createFoodRow(food, onClick, showSource=false) {
    const row = document.createElement("button");
    row.className = "saved-food-row";
    row.type = "button";

    const text = document.createElement("span");
    text.className = "saved-food-text";

    const name = document.createElement("strong");
    name.textContent = food.name;

    const meta = document.createElement("small");
    const brand = food.brand ? ` · ${food.brand}` : "";
    meta.textContent = `${roundValue(food.calories)} ккал / 100 г${brand}`;

    text.appendChild(name);
    text.appendChild(meta);

    if (showSource) {
        const source = document.createElement("span");
        source.className = `source-badge ${getSourceClass(food.source)}`;
        source.textContent = getSourceName(food.source);
        row.appendChild(source);
    }

    const arrow = document.createElement("span");
    arrow.className = "add-option-arrow";
    arrow.textContent = "›";

    row.appendChild(text);
    row.appendChild(arrow);
    row.addEventListener("click", onClick);

    return row;
}

function renderSavedFoods(data) {
    savedFoodsList.innerHTML = "";

    if (data.length === 0) {
        savedFoodsEmpty.classList.remove("hidden");
        return;
    }

    savedFoodsEmpty.classList.add("hidden");

    data.forEach(food => {
        savedFoodsList.appendChild(
            createFoodRow(food, () => openWeightScreen(food, "saved", savedFoodsScreen))
        );
    });
}

async function openSavedFoods() {
    setSheetHeader("Добавление еды", "Сохранённые");
    showSheetScreen(savedFoodsScreen);
    savedFoodsList.innerHTML = "";
    savedFoodsEmpty.classList.add("hidden");

    try {
        const data = await apiRequest("/api/saved-foods");
        renderSavedFoods(data);
    }
    catch (err) {
        console.error(err);
        tg?.showAlert?.("Не удалось загрузить сохранённые продукты.");
        showMainAddMenu();
    }
}

function updateFoodPreview() {
    if (!selectedFood) return;

    const weight = Number(weightInput.value) || 0;
    const coef = weight / 100;

    setText("preview-calories", `${roundValue(selectedFood.calories * coef)} ккал`);
    setText("preview-protein", `${roundMacro(selectedFood.protein * coef)} г`);
    setText("preview-fat", `${roundMacro(selectedFood.fat * coef)} г`);
    setText("preview-carbs", `${roundMacro(selectedFood.carbs * coef)} г`);
    confirmAddFood.disabled = weight <= 0;
}

function openWeightScreen(food, mode, fromScreen) {
    selectedFood = food;
    selectedFoodMode = mode;
    previousScreen = fromScreen;

    setSheetHeader(mode === "saved" ? "Сохранённый продукт" : getSourceName(food.source), "Укажи вес");
    setText("selected-food-name", food.name);
    setText("selected-food-base", `${roundValue(food.calories)} ккал / 100 г`);
    weightInput.value = food.weight && Number(food.weight) > 0 ? roundValue(food.weight) : 100;
    showSheetScreen(weightScreen);
    updateFoodPreview();
    setTimeout(() => weightInput.focus(), 100);
}

async function addSelectedFood() {
    if (!selectedFood) return;

    const weight = Number(weightInput.value);
    if (!Number.isFinite(weight) || weight <= 0) return;

    confirmAddFood.disabled = true;
    confirmAddFood.textContent = "Добавляю...";

    try {
        if (selectedFoodMode === "saved") {
            await apiRequest(`/api/saved-foods/${selectedFood.id}/add`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({weight})
            });
        }
        else {
            await apiRequest("/api/products/add", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    name: selectedFood.name,
                    weight,
                    calories: selectedFood.calories,
                    protein: selectedFood.protein,
                    fat: selectedFood.fat,
                    carbs: selectedFood.carbs
                })
            });
        }

        tg?.HapticFeedback?.notificationOccurred("success");
        closeAddSheet();
        await refreshData();
    }
    catch (err) {
        console.error(err);
        tg?.HapticFeedback?.notificationOccurred("error");
        tg?.showAlert?.("Не удалось добавить продукт.");
    }
    finally {
        confirmAddFood.disabled = false;
        confirmAddFood.textContent = "Добавить в дневник";
    }
}

function renderSearchProducts(products, append=false) {
    if (!append) searchResults.innerHTML = "";

    products.forEach(food => {
        searchResults.appendChild(
            createFoodRow(food, () => openWeightScreen(food, "search", searchScreen), true)
        );
    });
}

async function runSearch(reset=true) {
    const query = searchInput.value.trim();
    if (!query) return;

    if (reset) {
        searchPage = 0;
        searchQuery = query;
        searchResults.innerHTML = "";
        searchEmpty.classList.add("hidden");
        searchMore.classList.add("hidden");
    }

    searchSubmit.disabled = true;
    searchSubmit.textContent = "...";

    try {
        const data = await apiRequest(`/api/products?query=${encodeURIComponent(searchQuery)}&page=${searchPage}`);
        searchTotal = data.total;

        renderSearchProducts(data.products, !reset);

        if (searchTotal === 0) {
            searchInfo.classList.add("hidden");
            searchEmpty.classList.remove("hidden");
            searchMore.classList.add("hidden");
            return;
        }

        searchEmpty.classList.add("hidden");
        searchInfo.classList.remove("hidden");
        searchInfo.textContent = data.source === "perek"
            ? `Perek · найдено ${searchTotal}`
            : `Найдено ${searchTotal}`;

        const loaded = searchResults.children.length;
        if (data.source === "local" && loaded < searchTotal) searchMore.classList.remove("hidden");
        else searchMore.classList.add("hidden");
    }
    catch (err) {
        console.error(err);
        tg?.showAlert?.("Не удалось выполнить поиск.");
    }
    finally {
        searchSubmit.disabled = false;
        searchSubmit.textContent = "Найти";
    }
}

function openSearch() {
    setSheetHeader("База продуктов", "Поиск продукта");
    showSheetScreen(searchScreen);
    setTimeout(() => searchInput.focus(), 100);
}

function parseAiFoods() {
    const lines = aiInput.value.split("\n").map(line => line.trim()).filter(Boolean);
    const foods = [];

    for (const line of lines) {
        const separator = line.lastIndexOf(" - ");
        if (separator === -1) return null;

        const name = line.slice(0, separator).trim();
        const weightText = line.slice(separator + 3).replace(",", ".").replace(/[^0-9.]/g, "");
        const weight = Number(weightText);

        if (!name || !Number.isFinite(weight) || weight <= 0) return null;
        foods.push({name, weight});
    }

    return foods.length ? foods : null;
}

function renderAiResults(data) {
    aiResults.innerHTML = "";

    data.forEach(food => {
        const card = document.createElement("article");
        card.className = "ai-result-card";

        const top = document.createElement("div");
        top.className = "ai-result-top";

        const name = document.createElement("strong");
        name.textContent = food.name;

        const weight = document.createElement("span");
        weight.textContent = `${roundValue(food.weight)} г`;

        const macros = document.createElement("small");
        macros.textContent = `${roundValue(food.calories)} ккал · Б ${roundMacro(food.protein)} · Ж ${roundMacro(food.fat)} · У ${roundMacro(food.carbs)}`;

        top.appendChild(name);
        top.appendChild(weight);
        card.appendChild(top);
        card.appendChild(macros);
        aiResults.appendChild(card);
    });
}

function openAiFood() {
    setSheetHeader("Быстрый режим", "Подсчёт AI");
    showSheetScreen(aiScreen);
    estimatedFoods = [];
    aiResults.innerHTML = "";
    aiResults.classList.add("hidden");
    aiAdd.classList.add("hidden");
}

async function estimateAiFoods() {
    const foods = parseAiFoods();
    if (!foods) {
        tg?.showAlert?.("Формат: название - вес. Каждый продукт с новой строки.");
        return;
    }

    aiEstimate.disabled = true;
    aiEstimate.textContent = "Считаю...";

    try {
        estimatedFoods = await apiRequest("/api/ai-food/estimate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({foods})
        });

        renderAiResults(estimatedFoods);
        aiResults.classList.remove("hidden");
        aiAdd.classList.remove("hidden");
    }
    catch (err) {
        console.error(err);
        tg?.showAlert?.("AI сейчас не смог рассчитать КБЖУ. Попробуй позже.");
    }
    finally {
        aiEstimate.disabled = false;
        aiEstimate.textContent = "Рассчитать";
    }
}

async function addAiFoods() {
    if (!estimatedFoods.length) return;

    aiAdd.disabled = true;
    aiAdd.textContent = "Добавляю...";

    try {
        await apiRequest("/api/ai-food/add", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({foods: estimatedFoods})
        });

        tg?.HapticFeedback?.notificationOccurred("success");
        closeAddSheet();
        await refreshData();
    }
    catch (err) {
        console.error(err);
        tg?.showAlert?.("Не удалось добавить продукты.");
    }
    finally {
        aiAdd.disabled = false;
        aiAdd.textContent = "Добавить всё в дневник";
    }
}

function openManualFood() {
    setSheetHeader("Своя еда", "Добавить вручную");
    showSheetScreen(manualScreen);
}

async function addManualFood() {
    const data = {
        name: manualName.value.trim(),
        weight: Number(manualWeight.value),
        calories: Number(manualCalories.value),
        protein: Number(manualProtein.value),
        fat: Number(manualFat.value),
        carbs: Number(manualCarbs.value)
    };

    if (!data.name || !Number.isFinite(data.weight) || data.weight <= 0 ||
        !Number.isFinite(data.calories) || !Number.isFinite(data.protein) ||
        !Number.isFinite(data.fat) || !Number.isFinite(data.carbs)) {
        tg?.showAlert?.("Заполни название, вес и все значения КБЖУ.");
        return;
    }

    manualAdd.disabled = true;
    manualAdd.textContent = "Добавляю...";

    try {
        await apiRequest("/api/manual-food", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        tg?.HapticFeedback?.notificationOccurred("success");
        closeAddSheet();
        await refreshData();

        manualName.value = "";
        manualWeight.value = "";
        manualCalories.value = "";
        manualProtein.value = "";
        manualFat.value = "";
        manualCarbs.value = "";
    }
    catch (err) {
        console.error(err);
        tg?.showAlert?.("Не удалось добавить еду.");
    }
    finally {
        manualAdd.disabled = false;
        manualAdd.textContent = "Добавить в дневник";
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
        tg?.showAlert?.("Не удалось удалить запись.");
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
searchFoodButton.addEventListener("click", openSearch);
aiFoodButton.addEventListener("click", openAiFood);
manualFoodButton.addEventListener("click", openManualFood);
document.querySelectorAll("[data-back-menu]").forEach(button => button.addEventListener("click", showMainAddMenu));
weightBack.addEventListener("click", () => {
    if (previousScreen) showSheetScreen(previousScreen);
    else showMainAddMenu();
});
weightInput.addEventListener("input", updateFoodPreview);
confirmAddFood.addEventListener("click", addSelectedFood);
searchSubmit.addEventListener("click", () => runSearch(true));
searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") runSearch(true);
});
searchMore.addEventListener("click", async () => {
    searchPage += 1;
    await runSearch(false);
});
aiEstimate.addEventListener("click", estimateAiFoods);
aiAdd.addEventListener("click", addAiFoods);
manualAdd.addEventListener("click", addManualFood);
document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !addSheet.classList.contains("hidden")) closeAddSheet();
});

loadData();
