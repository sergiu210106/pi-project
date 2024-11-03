import reflex as rx
from rxconfig import config
import httpx  # For making GET requests to the FastAPI server
import base64


class State(rx.State):
    count: int = 0
    plot_url: str = ""  # To store the fetched plot image URL
    points: int = 0

    def increment(self):
        self.count += 1

    def set_end(self, value: list[int]):
        self.points = value[0] * 100

    async def fetch_data(self):
        """Function to fetch data from the server."""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/1012/1")
            if response.status_code == 200:
                print("Data fetched successfully:", response.json())
                self.count = response.json()['secret']
            else:
                print("Failed to fetch data:", response.status_code)
                self.count = "Failed to fetch"

    async def decrement(self):
        await self.fetch_data()

    async def fetch_plot(self):
        """Fetch the plot image from the FastAPI server."""
        async with httpx.AsyncClient() as client:

            response = await client.get("http://localhost:8000/plot?a=" + str(self.points))
            if response.status_code == 200:
                print("Plot fetched successfully.")
                # Encode the bytes to a base64 string
                encoded_image = base64.b64encode(response.content).decode('utf-8')
                self.plot_url = f"data:image/png;base64,{encoded_image}"
            else:
                print("Failed to fetch plot:", response.status_code)
                self.plot_url = ""  # Reset plot URL if fetch fails


def index():
    return rx.vstack(
        rx.hstack(
            rx.button(
                "Decrement",
                color_scheme="ruby",
                on_click=State.decrement,
            ),
            rx.heading(State.count, font_size="2em"),
            rx.button(
                "Increment",
                color_scheme="grass",
                on_click=State.increment,
            ),
            spacing="4",
        ),
        rx.button(
            "Fetch Plot",
            color_scheme="blue",
            on_click=State.fetch_plot,  # Fetch plot on button click
        ),
        # Display the plot image if available
        rx.heading(State.points, font_size="2em"),
        rx.slider(on_value_commit=State.set_end),
        rx.cond(
            State.plot_url,
            rx.image(src=State.plot_url, width="500px"),
            rx.text("No plot available"),
        ),
        width="100%",
    )


app = rx.App()
app.add_page(index)
