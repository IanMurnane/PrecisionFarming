from PIL import Image, ImageTk, ImageDraw, UnidentifiedImageError
import tkinter as tk
import os

# Define the path to your image folder
image_folder = "pics"

# Retrieve the list of image files from the folder
image_files = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".jpg")]

# Calculate the size of each tile
tile_width = 224
tile_height = 224

# Calculate the number of rows and columns
num_rows = 1
num_columns = 1

# Calculate the total screen size
screen_width = num_columns * tile_width
screen_height = num_rows * tile_height

# Create the main Tkinter window
window = tk.Tk()
window.title("Click to Update Target or Delete - Arrows to change page")
window.geometry(f"{screen_width}x{screen_height}")

# Keep track of the current page index
current_page = 0


def display_page():
    global disposables

    # Clear the previous images and labels
    for element in disposables:
        element.destroy()
    disposables.clear()

    # Calculate the starting and ending index for the current page
    start_index = current_page * (num_rows * num_columns)
    end_index = start_index + (num_rows * num_columns)

    # Iterate over the image files for the current page and display them in tiles
    for i, image_file in enumerate(image_files[start_index:end_index]):
        # Extract the coordinates from the image file name
        filename = os.path.basename(image_file)
        x, y, _ = filename.split("_")
        x = int(x)
        y = int(y)

        try:
            # Open the image file
            image = Image.open(image_file)

            # Resize the image to the tile size
            image = image.resize((tile_width, tile_height))

            # Draw a small light green circle at the specified coordinates
            draw = ImageDraw.Draw(image)
            circle_radius = 5
            circle_color = (144, 238, 144)  # Light green color
            circle_center = (x, y)
            draw.ellipse([(circle_center[0] - circle_radius, circle_center[1] - circle_radius),
                          (circle_center[0] + circle_radius, circle_center[1] + circle_radius)],
                         fill=circle_color)

            # Convert the image to Tkinter-compatible format
            photo = ImageTk.PhotoImage(image)
            photo_images.append(photo)  # Add the PhotoImage to the list
        except (OSError, UnidentifiedImageError):
            # Create a black tile if image loading fails
            photo = ImageTk.PhotoImage(Image.new("RGB", (tile_width, tile_height), color="black"))
            photo_images.append(photo)  # Add the PhotoImage to the list

        # Calculate the position of the current tile
        row = i // num_columns
        column = i % num_columns

        # Create a label to display the image
        label = tk.Label(window, image=photo)
        label.image = photo  # Keep a reference to the image to prevent it from being garbage collected

        # Bind the click event to the label
        label.bind("<Button-1>", lambda event, index=i: rename_image(event, index))

        # Position the label in the window
        label.grid(row=row, column=column)

        # Create and display the trash icon label for each image
        # Replace "trash_icon.png" with the path to your trash icon image
        trash_icon_image = Image.open("trash_icon.png")
        trash_icon_image = trash_icon_image.resize((18, 18))  # Resize the trash icon image as desired
        trash_icon_photo = ImageTk.PhotoImage(trash_icon_image)
        trash_icon_label = tk.Label(label, image=trash_icon_photo, bg="white")
        # Keep a reference to the image to prevent it from being garbage collected
        trash_icon_label.image = trash_icon_photo
        trash_icon_label.place(relx=0.92, rely=0.05, anchor="ne")
        trash_icon_label.bind("<Button-1>", lambda event, index=i: delete_image(event, index))
        disposables.append(trash_icon_label)

        # Store the label in a list for later removal
        disposables.append(label)

    # Display the page number
    total_pages = (len(image_files) + (num_rows * num_columns) - 1) // (num_rows * num_columns)
    page_text = f"Page {current_page + 1} of {total_pages}"
    page_label = tk.Label(window, text=page_text, font=("Arial", 12), bg="white")
    page_label.place(relx=0.98, rely=0.98, anchor="se")
    disposables.append(page_label)


def rename_image(event, i):
    global image_files

    index = current_page * num_columns * num_rows + i
    image_file = image_files[index]  # Get the image file path

    # Get the click coordinates relative to the image
    x = event.x
    y = event.y

    # Extract the base name and extension from the image file path
    base_name, extension = os.path.splitext(image_file)

    # Find the index of the last underscore in the base name
    last_underscore_index = base_name.rfind("_")

    if last_underscore_index != -1:
        # Extract the part of the base name before the last underscore
        base_without_coords = base_name[last_underscore_index:]

        # Create the new file name by adding the new coordinates
        new_filename = f"{x}_{y}{base_without_coords}{extension}"

        # Rename the image file
        try:
            new_file_path = os.path.join(image_folder, new_filename)
            os.rename(image_file, new_file_path)

            # Update the image file path in the image_files list
            image_files[index] = new_file_path

            # Refresh the displayed page to update the dot position
            display_page()
        except FileNotFoundError:
            print("FileNotFound")


def delete_image(event, index):
    global image_files

    # Remove the image label and trash icon label from the window
    disposables[index].destroy()
    disposables[index+1].destroy()

    # Delete the image file from the file system
    image_file = image_files[current_page * num_columns * num_rows + index]  # Get the image file path
    try:
        os.remove(image_file)
        del image_files[current_page * num_columns * num_rows + index]  # Remove the file path from the list
        display_page()
    except FileNotFoundError:
        pass


def on_keypress(event):
    global current_page

    if event.keysym == "Right":
        # Move to the next page if available
        if current_page < len(image_files) // (num_rows * num_columns):
            current_page += 1
            display_page()
    elif event.keysym == "Left":
        # Move to the previous page if available
        if current_page > 0:
            current_page -= 1
            display_page()


# Bind the keypress event to the window
window.bind("<Key>", on_keypress)

# List to store image labels and references for later removal
disposables = []

# List to store PhotoImage references
photo_images = []

# Display the initial page
display_page()

# Start the Tkinter event loop
window.mainloop()
