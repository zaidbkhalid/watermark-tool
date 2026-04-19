import customtkinter as ctk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WatermarkElite(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Watermark Elite v3.2 - Pro Controls")
        self.geometry("1200x850")

        # State Variables
        self.raw_image = None
        self.wm_color = (255, 255, 255, 180) # Increased default opacity
        self.font_path = "arial.ttf"

        self.setup_ui()

    def setup_ui(self):
        # Grid layout (2 columns: Sidebar and Main View)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="PRO EDITOR", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)

        # 1. Upload
        self.upload_btn = ctk.CTkButton(self.sidebar, text="Open Image", command=self.load_image, height=35)
        self.upload_btn.pack(pady=10, padx=20)

        # --- Controls Container ---
        self.controls_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.controls_frame.pack(expand=True, fill="both", padx=10)

        # 2. Text Content
        self.add_control_label("Text Content:")
        self.entry_var = ctk.StringVar(value="© My Brand")
        self.entry_var.trace_add("write", lambda *args: self.show_preview()) 
        self.entry = ctk.CTkEntry(self.controls_frame, textvariable=self.entry_var)
        self.entry.pack(fill="x", padx=15, pady=(0, 15))

        # 3. Color
        self.color_btn = ctk.CTkButton(self.controls_frame, text="Change Color", fg_color="transparent", 
                                      border_width=2, command=self.pick_color)
        self.color_btn.pack(fill="x", padx=15, pady=10)

        # 4. Size (NEW)
        self.size_label = ctk.CTkLabel(self.controls_frame, text="Size: 10%", anchor="w")
        self.size_label.pack(fill="x", padx=20, pady=(15, 0))
        # from 1% to 50% of image width
        self.size_slider = ctk.CTkSlider(self.controls_frame, from_=1, to=50, command=self.on_size_move)
        self.size_slider.set(10)
        self.size_slider.pack(fill="x", padx=15, pady=5)

        # 5. Rotation
        self.rot_label = ctk.CTkLabel(self.controls_frame, text="Rotation: 0°", anchor="w")
        self.rot_label.pack(fill="x", padx=20, pady=(15, 0))
        self.rot_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=360, command=self.on_rot_move)
        self.rot_slider.set(0)
        self.rot_slider.pack(fill="x", padx=15, pady=5)

        # 6. Position X (NEW)
        self.x_label = ctk.CTkLabel(self.controls_frame, text="X Position: 50%", anchor="w")
        self.x_label.pack(fill="x", padx=20, pady=(15, 0))
        # 0% (left) to 100% (right)
        self.x_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=100, command=self.on_pos_move)
        self.x_slider.set(50)
        self.x_slider.pack(fill="x", padx=15, pady=5)

        # 7. Position Y (NEW)
        self.y_label = ctk.CTkLabel(self.controls_frame, text="Y Position: 50%", anchor="w")
        self.y_label.pack(fill="x", padx=20, pady=(15, 0))
        # 0% (top) to 100% (bottom)
        self.y_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=100, command=self.on_pos_move)
        self.y_slider.set(50)
        self.y_slider.pack(fill="x", padx=15, pady=5)

        # 8. Export
        self.save_btn = ctk.CTkButton(self.sidebar, text="Export Result", fg_color="#2ecc71", 
                                     hover_color="#27ae60", command=self.save_image, height=40, font=("Arial", 14, "bold"))
        self.save_btn.pack(side="bottom", pady=30, padx=20, fill="x")

        # --- Main View ---
        self.main_view = ctk.CTkFrame(self, corner_radius=15, fg_color="#121212")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.preview_display = ctk.CTkLabel(self.main_view, text="Please upload an image")
        self.preview_display.pack(expand=True, fill="both", padx=15, pady=15)

    # --- UI Helper ---
    def add_control_label(self, text):
        lbl = ctk.CTkLabel(self.controls_frame, text=text, anchor="w", font=("Arial", 12, "bold"), text_color="#aaaaaa")
        lbl.pack(fill="x", padx=20, pady=(10, 0))

    # --- Interaction Logic (All Trigger Real-Time Refresh) ---
    def on_size_move(self, value):
        self.size_label.configure(text=f"Size: {int(value)}%")
        self.show_preview()

    def on_rot_move(self, value):
        self.rot_label.configure(text=f"Rotation: {int(value)}°")
        self.show_preview()

    def on_pos_move(self, value):
        # We update both labels regardless of which slider moved
        self.x_label.configure(text=f"X Position: {int(self.x_slider.get())}%")
        self.y_label.configure(text=f"Y Position: {int(self.y_slider.get())}%")
        self.show_preview()

    def pick_color(self):
        color = colorchooser.askcolor(title="Select Color")
        if color[1]:
            rgb = [int(x) for x in color[0]]
            # We keep the alpha (180) fixed for simplicity, though we could add an alpha slider too!
            self.wm_color = (rgb[0], rgb[1], rgb[2], 180)
            self.color_btn.configure(border_color=color[1], text_color=color[1])
            self.show_preview()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path:
            self.raw_image = Image.open(path).convert("RGBA")
            self.show_preview()

    def show_preview(self):
        if not self.raw_image:
            return

        # 1. Process at high speed (low resolution preview)
        # Max dimension 1200px for smooth performance
        preview_base = self.raw_image.copy()
        preview_base.thumbnail((1200, 1200))
        
        watermarked_preview = self.apply_logic(preview_base)
        
        # 2. Fit to the UI window size dynamically
        # Get width, but fallback if UI isn't drawn yet
        ui_w = self.main_view.winfo_width() - 40
        ui_h = self.main_view.winfo_height() - 40
        if ui_w < 10: ui_w, ui_h = 800, 600

        ratio = min(ui_w/watermarked_preview.width, ui_h/watermarked_preview.height)
        display_size = (int(watermarked_preview.width * ratio), int(watermarked_preview.height * ratio))
        
        img_tk = ctk.CTkImage(light_image=watermarked_preview, dark_image=watermarked_preview, size=display_size)
        self.preview_display.configure(image=img_tk, text="")

    def apply_logic(self, base_img):
        """The core engine: Creates text sticker, rotates it, and pastes it."""
        img_w, img_h = base_img.size
        
        # --- 1. Calculate Font Size ---
        # Size slider is % of image width
        size_pct = self.size_slider.get() / 100
        target_wm_width = img_w * size_pct
        
        # We use a dummy draw to find the right font size to hit that target width
        font_size = 10 
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except:
            font = ImageFont.load_default()

        text = self.entry_var.get()
        # Find font size iteratively (simple, reliable scaling)
        while font.getlength(text) < target_wm_width and font_size < 500:
            font_size += 2
            font = ImageFont.truetype(self.font_path, font_size)

        # --- 2. Create the Text "Sticker" ---
        # Draw on a separate small canvas just big enough for the text
        draw = ImageDraw.Draw(Image.new("RGBA", (1,1)))
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        
        # Add padding so rotation doesn't clip edges
        pad = int(max(tw, th) * 0.5)
        sticker_size = (tw + pad, th + pad)
        text_sticker = Image.new("RGBA", sticker_size, (255, 255, 255, 0))
        sticker_draw = ImageDraw.Draw(text_sticker)
        
        # Draw text in the center of the sticker
        sticker_draw.text((pad//2, pad//2), text, fill=self.wm_color, font=font)
        
        # --- 3. Rotate the Sticker ---
        rotated_sticker = text_sticker.rotate(self.rot_slider.get(), resample=Image.BICUBIC, expand=True)
        
        # --- 4. Calculate Position ---
        # Sliders are 0-100% of the image dimensions
        pct_x = self.x_slider.get() / 100
        pct_y = self.y_slider.get() / 100
        
        # We align the center of the rotated sticker with the calculated coordinate
        rw, rh = rotated_sticker.size
        final_x = int((img_w * pct_x) - (rw // 2))
        final_y = int((img_h * pct_y) - (rh // 2))
        
        # --- 5. Composite ---
        # Paste the transparent sticker onto a copy of the base image
        output = base_img.copy()
        output.alpha_composite(rotated_sticker, dest=(final_x, final_y))
        
        return output

    def save_image(self):
        if not self.raw_image:
            return
            
        # Process the ORIGINAL high-res image for export
        self.save_btn.configure(text="Processing...", state="disabled")
        self.update() # Force UI update

        final = self.apply_logic(self.raw_image)
        
        save_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                 filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
        if save_path:
            if save_path.endswith((".jpg", ".jpeg")):
                final = final.convert("RGB")
            final.save(save_path)
            messagebox.showinfo("Export Successful", f"Saved to: {os.path.basename(save_path)}")
        
        self.save_btn.configure(text="Export Result", state="normal")

if __name__ == "__main__":
    app = WatermarkElite()
    app.mainloop()