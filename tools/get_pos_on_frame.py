import cv2
import tkinter as tk
from PIL import Image, ImageTk

def get_image_position(video_file):
    def on_click(event):
        x, y = event.x, event.y
        position_label.config(text=f"Position: ({x}, {y})")
        window.position = (x, y)

    # Load the video and get the first frame
    cap = cv2.VideoCapture(video_file)
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cap.release()

    # Create the Tkinter window
    window = tk.Tk()
    window.title("Select Image Position")

    # Display the video frame
    frame_image = Image.fromarray(frame)
    frame_photo = ImageTk.PhotoImage(frame_image)
    frame_label = tk.Label(window, image=frame_photo)
    frame_label.bind("<Button-1>", on_click)
    frame_label.pack()

    # Display the position label
    position_label = tk.Label(window, text="Position: Not selected")
    position_label.pack()

    # Add a button to confirm the position and close the window
    confirm_button = tk.Button(window, text="Confirm", command=window.quit)
    confirm_button.pack()

    # Run the Tkinter event loop
    window.position = None
    window.mainloop()

    # Get the selected position and close the window
    position = window.position
    window.destroy()

    return position

# Example usage
video_file = "./templates/closing_empty.mp4"
# image = make_image()
position = get_image_position(video_file)
print(position)
# output_video = overlay_image_on_video(video_file, image, position)
# output_video.write_videofile("output_video.mp4", codec='libx264', audio_codec='aac')
