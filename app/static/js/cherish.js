document.addEventListener("DOMContentLoaded", () => {

    const forms = document.querySelectorAll(".cherish-form");

    forms.forEach(form => {

        form.addEventListener("submit", async function(event) {

            event.preventDefault();

            const button = form.querySelector(".cherish-button");
            const icon = button.querySelector(".cherish-icon");
            const text = button.querySelector(".cherish-text");

            button.disabled = true;

            try {

                const response = await fetch(form.action, {
                    method: "POST"
                });

                const data = await response.json();

                if (data.cherished) {

                    icon.textContent = "💛";

                } else {

                    icon.textContent = "🤍";

                }

                if (data.count === 0) {

                    text.textContent = "Cherish";

                } else {

                    text.textContent = data.count;

                }

            } catch (error) {

                console.error("Cherish Error:", error);

            } finally {

                button.disabled = false;

            }

        });

    });

});