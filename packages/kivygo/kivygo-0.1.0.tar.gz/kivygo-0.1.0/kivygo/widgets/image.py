
from kivy.properties import ListProperty, ColorProperty
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.uix.image import Image

from kivy.core.image import Image as CoreImage
import tempfile

import svgwrite
import io

# from reportlab.graphics import renderPM
from reportlab.lib.colors import red, green

from PIL import Image as PILImage


Builder.load_string("""

<GoImage>:
	canvas:
		Clear:
		Color:
			rgba: self._color
		RoundedRectangle:
			pos: self.pos
			size: self.size
			radius: root.radius
			texture: root.texture

	fit_mode: "fill"

""")


class GoImage(Image):

	radius = ListProperty([0]*4)
	_color = ColorProperty([0]*4)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._color = self.color
		Clock.schedule_once(self.texture_update)

	def on_color(self, *args):
		self._color = self.color

	def set_texture_from_resource(self, resource):
		if not resource:
			self._clear_core_image()
			return None
		
		if not resource.endswith(".svg"):
			return super().set_texture_from_resource(resource)
	
		if self._coreimage:
			self._coreimage.unbind(on_texture=self._on_tex_change)

		file = tempfile.NamedTemporaryFile(mode='+wb', suffix=".png")
		try:
			self.svg_to_png(self.source, file)
		except ValueError:
			pass

		file.seek(0)
		self._coreimage = image = self.get_kivy_image_from_bytes(file.read(), 'png')
		image.bind(on_texture=self._on_tex_change)
		self.texture = image.texture

	
	def get_kivy_image_from_bytes(self, image_bytes, file_extension):
		# Return a Kivy image set from a bytes variable
		buf = io.BytesIO(image_bytes)
	
		image = CoreImage(
			buf, ext=file_extension,
			mipmap=self.mipmap,
			anim_delay=self.anim_delay,
			keep_data=self.keep_data,
			nocache=self.nocache
		)
		return image

	def svg_to_png(path, fp):
		"""
		Alternativa para converter SVG para PNG usando svgwrite para rasterização simples.
		"""
		try:
			# Carregar o SVG com svgwrite (manipulação básica)
			dwg = svgwrite.Drawing(path)
			
			# Exportar para string SVG
			svg_string = dwg.tostring()
			
			# Converter SVG para PNG com Pillow (simples para SVGs estáticos)
			img = PILImage.open(io.BytesIO(svg_string.encode()))
			img.save(fp, format="PNG")
		except Exception as e:
			print(f"Erro ao processar SVG: {e}")

