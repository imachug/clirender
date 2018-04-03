class Node(object):
	container = False
	text_container = False

	def __init__(self, children=None, value=[], **kwargs):
		self.render_offset = (None, None)
		self.render_boundary_left_top = [None, None]
		self.render_boundary_right_bottom = [None, None]
		self.parent = None
		self.render_stretch = None

		self.inheritable = {}

		self._children = children
		self.value = value
		self._revoked = False
		self._completely_revoked = False
		self.cache_sizes = (None, None)
		self.cache_offset = (None, None)

	@property
	def children(self):
		return self._get_children(self._children)

	@children.setter
	def children(self, children):
		self._children = children

	def _get_children(self, old):
		from generator import Generator

		children = []
		for child in old:
			if isinstance(child, Generator):
				child.parent = self
				child.layout = self.layout
				generated = child.generate()

				for subchild in self._get_children(generated):
					if not hasattr(subchild, "generated_by"):
						subchild.generated_by = []
					subchild.generated_by.append(child)

					children.append(subchild)
			else:
				children.append(child)

		return children

	def render(self, dry_run=False):
		raise NotImplementedError

	def inherit(self, attr):
		node = self

		value = getattr(node, attr, None)
		try:
			while value.strip().lower() == "inherit":
				parent = node.parent
				if parent is None:
					return None

				value = getattr(parent, attr, None)
				if value is None:
					value = parent.inheritable.get(attr, None)

				# Bypass <Container>
				from container import Container
				if value is None and isinstance(parent, Container):
					value = "inherit"

				node = parent
		except AttributeError:
			pass

		try:
			if isinstance(value, Node) and value.strip().lower() == "inherit":
				return value.inherit(attr)
		except AttributeError:
			pass

		return value


	def renderChild(self, child, dry_run, offset, boundary_left_top, boundary_right_bottom, parent_width, parent_height, stretch, completely_revoked=True, plus_size=(0, 0)):
		child.cache_offset = child.render_offset

		child.render_offset = offset
		child.render_plus_size = plus_size
		child.render_boundary_left_top = boundary_left_top
		child.render_boundary_right_bottom = boundary_right_bottom
		child.render_stretch = stretch
		child.render_parent_width = parent_width
		child.render_parent_height = parent_height
		child.parent = self
		child.layout = self.layout
		child._completely_revoked = completely_revoked

		sizes = child.render(dry_run=dry_run)
		child.cache_sizes = sizes
		child.cache_offset = offset
		return sizes


	def getBoundaryBox(self):
		return dict(
			left=child.cache_offset[0],
			top=child.cache_offset[0],

			right=child.cache_offset[0] + child.cache_sizes[0],
			bottom=child.cache_offset[1] + child.cache_sizes[1],

			width=child.cache_sizes[0],
			height=child.cache_sizes[1]
		)