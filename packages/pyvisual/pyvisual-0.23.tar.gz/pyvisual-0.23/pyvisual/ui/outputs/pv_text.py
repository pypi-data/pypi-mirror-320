from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase
import re
from kivy.core.text import Label as CoreLabel


class PvText(AnchorLayout):
    def __init__(self, container,text="Hello" ,x=50, y=50,
                 font="Roboto", font_size=20, font_color=(0.4, 0.4, 0.4, 1),
                 bold=False, italic=False, underline=False, strikethrough=False,
                 bg_color=(0, 0, 0, 0),box_width=200,text_alignment="left",
                 is_visible=True, opacity=1, tag=None,multiline=False, **kwargs):
        # Ensure box_width and rect_height have default values
        box_width = box_width or 200
        rect_height = font_size+5 or 50

        super().__init__(anchor_x="center", anchor_y="center", size_hint=(None, None),
                         size=(box_width, rect_height), pos=(x, y),**kwargs)
        self.container = container
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.bg_color = bg_color
        self.box_width = box_width
        self.rect_height = rect_height
        self.is_visible = is_visible
        self.tag = tag
        self.text_alignment = text_alignment
        self.font = font
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough
        self.opacity = opacity
        self.multiline = multiline


        # Apply markup to the text
        self.text = self.apply_markup(self.text)

        # Register font if a file path is provided
        if font and font.endswith(('.ttf', '.otf')):
            LabelBase.register(name="CustomFont", fn_regular=font)
            self.font_name = "CustomFont"
        else:
            self.font_name = font

        # Wrap text if multiline is enabled
        # if self.multiline:
        self.text, self.rect_height = self.wrap_text(self.text, self.box_width)

        # Update widget height dynamically
        self.size = (self.box_width, self.rect_height)
        # Add the background rectangle
        with self.canvas.before:
            self.bg_color_instruction = Color(*self.bg_color)  # Background color
            self.rectangle = Rectangle(size=(self.box_width, self.rect_height), pos=self.pos)



        # Add the label
        self.label = Label(
            text=self.text,
            font_size=self.font_size,
            color=self.font_color,
            size_hint=(None, None),
            size=(self.box_width, self.rect_height),
            halign=self.text_alignment,
            valign="middle",
            font_name=self.font_name,
            markup=True,  # Enable Kivy markup tags,
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.update_label_text_alignment()
        self.bind(pos=self._update_canvas, size=self._update_canvas)

        if container:
            self.add_widget(self.label)
            self.container.add_widget(self)
        else:
            self.add_widget(self.label)



        # Add the widget to the container

        # Set initial is_visible
        self.set_visibility(self.is_visible)
        self.bind(opacity=self._on_opacity)
        self.opacity = opacity  # Trigger the opacity bindinge canvas to update

    def _update_canvas(self, *args):
        # Update button background
        self.rectangle.pos = self.pos
        self.rectangle.size = self.size
    def apply_markup(self, text):
        """Apply markup styles (bold, italic, underline, strikethrough) to text."""
        if self.strikethrough:
            text = f"[s]{text}[/s]"
        if self.underline:
            text = f"[u]{text}[/u]"
        if self.italic:
            text = f"[i]{text}[/i]"
        if self.bold:
            text = f"[b]{text}[/b]"
        return text

    def wrap_text(self, text, max_width):
        """
        Wrap text into multiple lines based on the box width.
        If multiline is False, ensure the text fits within one line.
        """
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            label = CoreLabel(text=test_line, font_size=self.font_size, font_name=self.font)
            label.refresh()
            if label.texture.size[0] <= max_width:
                current_line = test_line
            else:
                if self.multiline:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Truncate the text to fit within one line
                    current_line = current_line.strip()
                    break

        if current_line:
            lines.append(current_line)
        #
        if not self.multiline:
            # For single-line text, return only the first line
            return text, self.font_size

        # Calculate the height required for all lines
        line_height = self.font_size + 10  # Adjust line spacing
        total_height = len(lines) * line_height

        return "\n".join(lines), total_height

    def update_label_text_alignment(self):
        """Recalculate text alignment for the label."""
        self.label.text_size = (self.box_width, None if not self.multiline else self.rect_height)
        self.label.halign = self.text_alignment
        self.label.valign = "middle"

    def set_text(self, text):
        """Update the text."""
        self.text = text
        self.label.text = self.apply_markup(self.text)

    def set_font_size(self, font_size):
        """Update the font size of the text."""
        self.font_size = font_size
        self.label.font_size = self.font_size

    def set_font_color(self, font_color):
        """Update the text color."""
        self.font_color = font_color
        self.label.color = self.font_color

    def set_bg_color(self, bg_color):
        """Update the background color."""
        self.bg_color = bg_color
        self.bg_color_instruction.rgba = self.bg_color

    def set_text_alignment(self, text_alignment):
        """Update the text text_alignment (left, right, center)."""
        self.text_alignment = text_alignment
        self.update_label_text_alignment()

    def set_rect_size(self, box_width, rect_height):
        """Update the size of the rectangle."""
        self.box_width = box_width
        self.rect_height = rect_height
        self.rectangle.size = (self.box_width, self.rect_height)
        self.label.size = (self.box_width, self.rect_height)
        self.update_label_text_alignment()

    def set_visibility(self, is_visible):
        """Show or hide the text and rectangle."""
        if is_visible:
            self.opacity = 1
            self.canvas.opacity = 1
        else:
            self.opacity = 0
            self.canvas.opacity = 0

        self.is_visible = is_visible

    def set_box_width(self, box_width):
        """Update the width of the box."""
        self.box_width = box_width
        self.rectangle.size = (self.box_width, self.rect_height)
        self.label.size = (self.box_width, self.rect_height)
        self.update_label_text_alignment()

    def set_font_name(self, font_name):
        """Update the custom font."""
        self.font = font_name
        self.label.font_name = self.font

    def set_strikethrough(self, strikethrough):
        """Enable or disable strikethrough for the text."""
        self.strikethrough = strikethrough
        self.label.text = self.apply_markup(self.text)

    def set_underline(self, underline):
        """Enable or disable underline for the text."""
        self.underline = underline
        self.label.text = self.apply_markup(self.text)

    def set_italic(self, italic):
        """Enable or disable italic for the text."""
        self.italic = italic
        self.label.text = self.apply_markup(self.text)

    def set_bold(self, bold):
        """Enable or disable bold for the text."""
        self.bold = bold
        self.label.text = self.apply_markup(self.text)

    def get_text(self):
        # Remove markup tags like [b] and [/b]
        clean_text = re.sub(r'\[/?[a-zA-Z]+\]', '', self.text)
        return clean_text

    def _on_opacity(self, instance, value):
        """Update the canvas opacity when the widget's opacity changes."""
        self.opacity = value
        self.canvas.opacity = value

    def set_opacity(self,opacity):
        self.opacity = opacity
        self.canvas.opacity = opacity

    def add_to_layout(self, layout):
        """Add the image to a layout."""
        if self.parent is not None:
            self.parent.remove_widget(self)
        layout.add_widget(self)


if __name__ == "__main__":
    import pyvisual as pv

    window = pv.PvWindow(height=400,width=700)

    # Create a text with background
    # text_bg = PvText(
    #     container=window, x=100, y=249, text="Text", font_size=40, font_color=(0, 0, 0, 1),
    #     bg_color=(1, 0, 0, 1), text_alignment="left", box_width=300, is_visible=True, tag="text1",
    #     opacity=1
    # )

    text_multi = "Hello, this is a long piece of text that will wrap to the next line if it exceeds the box width."
    text_bg = PvText(
        container=window, x=50, y=200, text=text_multi, font_size=20, font_color=(0, 0, 0, 1),
        bg_color=(1, 0, 0, 1), text_alignment="left", box_width=300, is_visible=True, tag="text1",
        opacity=1, multiline=True
    )

    window.show()
