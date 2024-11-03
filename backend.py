from typing import Union
from fastapi import FastAPI
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from io import BytesIO
from fastapi.responses import StreamingResponse
import numpy as np

app = FastAPI()
batch_points = []


def generate_random_points(num_points=1000, batches=100):
    """Generate 3D points incrementally within a unit sphere."""
    batch_size = num_points // batches
    for _ in range(batches):
        for _ in range(batch_size):
            # Spherical coordinates to ensure points are within a sphere
            u = random.uniform(0, 1)
            theta = random.uniform(0, 2 * np.pi)
            phi = random.uniform(0, np.pi)

            r = u ** (1 / 3)  # Cube root to make points uniform in volume
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)

            batch_points.append((x, y, z))
        yield batch_points


# Create animated GIF of the 3D points
def plot_points_animated(point_generator):
    global batch_points
    batch_points = []
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])

    inside_scatter = ax.scatter([], [], [], color='red')
    outside_scatter = ax.scatter([], [], [], color='blue')

    def update(batch_points):
        inside_x, inside_y, inside_z = [], [], []
        outside_x, outside_y, outside_z = [], [], []
        for x, y, z in batch_points:
            if x ** 2 + y ** 2 + z ** 2 <= 1:
                inside_x.append(x)
                inside_y.append(y)
                inside_z.append(z)
            else:
                outside_x.append(x)
                outside_y.append(y)
                outside_z.append(z)

        inside_scatter._offsets3d = (inside_x, inside_y, inside_z)
        outside_scatter._offsets3d = (outside_x, outside_y, outside_z)
        return inside_scatter, outside_scatter

    ani = animation.FuncAnimation(fig, update, frames=point_generator, interval=50, repeat=True)
    filename = "anim.gif"
    # Save the animation to a GIF file
    ani.save(filename, writer="pillow", fps=15)
    plt.close(fig)
    return filename
# Endpoint to return the animated plot
@app.get("/plot")
async def get_plot(num_points: int = 1000):
    global batch_points
    batch_points = []
    point_generator = generate_random_points(num_points)
    gif_file = plot_points_animated(point_generator)
    # Open the GIF file in binary mode and stream it
    return StreamingResponse(open(gif_file, "rb"), media_type="image/gif")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/1012/1")
def read_root():
    return {"secret": "1287492ujfskdn@#$T$WGRFSV"}


@app.get("/items/{a}/{b}")
def read_item(a: int, b: int, q: Union[str, None] = None):
    return {"solutie": a + b, "q": q}