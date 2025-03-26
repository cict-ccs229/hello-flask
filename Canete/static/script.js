document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    const suggestionsBox = document.getElementById("suggestions");
    const diseaseInfo = document.getElementById("diseaseInfo");

    searchInput.addEventListener("input", async function () {
        const query = searchInput.value.trim();
        
        if (query.length === 0) {
            suggestionsBox.classList.add("hidden");
            diseaseInfo.classList.add("hidden");
            return;
        }

        try {
            const response = await fetch(`/search?q=${query}`);
            const diseases = await response.json();

            suggestionsBox.innerHTML = "";
            diseaseInfo.innerHTML = "";
            
            if (diseases.length > 0) {
                suggestionsBox.classList.remove("hidden");
                
                diseases.forEach(disease => {
                    const li = document.createElement("li");
                    li.innerHTML = `
                        <span>${disease.primary_name}</span>
                    `;
                    li.classList.add("p-2", "cursor-pointer", "hover:bg-gray-200");

                    li.addEventListener("click", () => {
                        displayDisease(disease);
                        searchInput.value = disease.primary_name;
                        suggestionsBox.classList.add("hidden");
                    });

                    suggestionsBox.appendChild(li);
                });
            } else {
                suggestionsBox.classList.add("hidden");
            }
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    });

    function displayDisease(disease) {
        diseaseInfo.innerHTML = `
            <h2 class="text-xl font-bold">${disease.primary_name}</h2>
            <p><strong>Synonyms:</strong> ${disease.synonyms.join(", ") || "None"}</p>
            <p><strong>ICD-10 Codes:</strong> ${disease.icd10cm.map(icd => `${icd.code} - ${icd.name}`).join(", ") || "None"}</p>
            <p><strong>Is Procedure:</strong> ${disease.is_procedure ? "Yes" : "No"}</p>
            <p><strong>More Info:</strong> ${disease.info_links.length > 0 ? `<a href="${disease.info_links[0][0]}" target="_blank" class="text-blue-500 underline">${disease.info_links[0][1]}</a>` : "N/A"}</p>
        `;
        diseaseInfo.classList.remove("hidden");
    }
});