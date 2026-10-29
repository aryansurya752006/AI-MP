const form = document.querySelector("#listing-form");
const citySelect = document.querySelector("#city");
const neighbourhoodSelect = document.querySelector("#neighbourhood");
const submitButton = document.querySelector("#submit-button");
const errorBox = document.querySelector("#form-error");
const emptyResult = document.querySelector("#empty-result");
const priceResult = document.querySelector("#price-result");
const loadingResult = document.querySelector("#loading-result");
const priceAmount = document.querySelector("#price-amount");
const modelName = document.querySelector("#model-name");

let options;

function fillSelect(select, values, placeholder) {
  select.replaceChildren(new Option(placeholder, ""));
  for (const value of values) {
    select.add(new Option(value, value));
  }
  select.disabled = values.length === 0;
}

function updateNeighbourhoods() {
  const neighbourhoods = options?.neighbourhoods_by_city[citySelect.value] ?? [];
  fillSelect(neighbourhoodSelect, neighbourhoods, "Choose a neighbourhood");
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function setLoading(loading) {
  submitButton.disabled = loading || !options;
  submitButton.classList.toggle("is-loading", loading);
  submitButton.querySelector("span:first-child").textContent = loading
    ? "Calculating your estimate…"
    : "Estimate my nightly price";
  loadingResult.hidden = !loading;
  if (loading) {
    emptyResult.hidden = true;
    priceResult.hidden = true;
  }
}

async function loadOptions() {
  try {
    const response = await fetch("/api/options");
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Could not load the listing options.");
    }
    options = data;

    fillSelect(citySelect, data.cities, "Choose a city");
    fillSelect(document.querySelector("#property_type"), data.property_types, "Choose property type");
    fillSelect(document.querySelector("#room_type"), data.room_types, "Choose room type");
    fillSelect(document.querySelector("#bed_type"), data.bed_types, "Choose bed type");
    fillSelect(
      document.querySelector("#cancellation_policy"),
      data.cancellation_policies,
      "Choose cancellation policy",
    );
    citySelect.value = data.cities.includes("Boston") ? "Boston" : data.cities[0];
    updateNeighbourhoods();

    const amenities = document.querySelector("#amenities");
    amenities.replaceChildren();
    for (const [key, label] of Object.entries(data.amenities)) {
      const option = document.createElement("label");
      option.className = "amenity-option";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.name = "amenities";
      input.value = key;
      const check = document.createElement("span");
      check.className = "custom-check";
      check.setAttribute("aria-hidden", "true");
      const text = document.createElement("span");
      text.textContent = label;
      option.append(input, check, text);
      amenities.append(option);
    }

    modelName.textContent = data.model_name;
    document.querySelector("#model-note").textContent = data.note;
    if (Number.isFinite(data.test_mae_dollars)) {
      document.querySelector("#model-accuracy").textContent =
        `Model test MAE: $${data.test_mae_dollars.toFixed(2)}.`;
    }
    submitButton.disabled = false;
  } catch (error) {
    showError(error.message);
  }
}

citySelect.addEventListener("change", updateNeighbourhoods);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.hidden = true;
  const formData = new FormData(form);
  const payload = {
    city: formData.get("city"),
    neighbourhood: formData.get("neighbourhood"),
    property_type: formData.get("property_type"),
    room_type: formData.get("room_type"),
    bed_type: formData.get("bed_type"),
    cancellation_policy: formData.get("cancellation_policy"),
    accommodates: Number(formData.get("accommodates")),
    bathrooms: Number(formData.get("bathrooms")),
    bedrooms: Number(formData.get("bedrooms")),
    beds: Number(formData.get("beds")),
    cleaning_fee: form.elements.cleaning_fee.checked,
    instant_bookable: form.elements.instant_bookable.checked,
    amenities: formData.getAll("amenities"),
  };

  setLoading(true);
  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "The price estimate could not be calculated.");
    }
    priceAmount.textContent = new Intl.NumberFormat("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(data.predicted_price);
    modelName.textContent = data.model_name;
    emptyResult.hidden = true;
    priceResult.hidden = false;
  } catch (error) {
    showError(error.message);
    emptyResult.hidden = false;
    priceResult.hidden = true;
  } finally {
    setLoading(false);
  }
});

loadOptions();
