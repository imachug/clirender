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
		self._cached_children = None
		self.value = value

	@property
	def children(self):
		if self._cached_children is None:
			self._cached_children = self._get_children(self._children)

		return self._cached_children

	@children.setter
	def children(self, children):
		self._children = children

	def _get_children(self, old):
		from generator import Generator

		children = []
		for child in old:
			if isinstance(child, Generator):
				children += self._get_children(child.generate())
			else:
				children.append(child)

		return children

	def render(self, layout, dry_run=False):
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


	def renderChild(self, layout, child, dry_run, offset, boundary_left_top, boundary_right_bottom, stretch):
		child.render_offset = offset
		child.render_boundary_left_top = boundary_left_top
		child.render_boundary_right_bottom = boundary_right_bottom
		child.render_stretch = stretch
		child.parent = self

		return child.render(layout, dry_run=dry_run)