#==============================================================================
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 - 2016 Tobias Röttger <toroettg@gmail.com>
#
# This file is part of SeriesMarker.
#
# SeriesMarker is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# SeriesMarker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SeriesMarker.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================

from PySide.QtCore import QSize

from seriesmarker.gui.model.decorated_node import DecoratedNode


class TreeNode(DecoratedNode):
    """Base class to store series data in a :class:`PySide.QtCore.QAbstractItemModel`."""

    def __init__(self, data, parent=None):
        """Initializes the node.

        :param model: The model the node has been added to.
        :type index: :class:`.QtCore.QAbstractItemModel`
        :param data: The data the node contains.
        :type data: :class:`object`
        :param parent: The node's parent in the tree.
        :type parent: :class:`.TreeNode`

        """
        super().__init__(scale=QSize(102, 150))

        self.parent = parent
        self.data = data
        self._children = []
        self._leaf_cache = None
        self._checked_cache = None

    @property
    def children(self):
        """Returns an immutable representation of the node's children.

        :return: The children of the node in a tuple of :class:`.TreeNode`.

        """
        return tuple(self._children)

    def child_count(self):
        """Returns the number of the node's children.

        :returns: The children's count.

        """
        return len(self._children)

    @property
    def leaf_count(self):
        """Returns the number of leaves in the branch of the node.

        .. note::

            Once counted, the number of leaves is cached for further usage.

        :returns: The count of nodes without children in the node's branch.

        """
        if self._leaf_cache == None:
            count = 1 if self.child_count() == 0 else 0
            for child in self._children:
                count = count + child.leaf_count
            self._leaf_cache = count
        return self._leaf_cache

    @leaf_count.setter
    def leaf_count(self, value):
        if self._leaf_cache is not None:
            self._leaf_cache += value

    @property
    def checked_count(self):
        """Returns the number of checked nodes in the branch of the node.

        The branch is traversed, beginning from the node to the leaf-level.
        All checked nodes are counted, including the starting node.

        .. note::

            Once counted, the number of checked nodes is cached for further usage.

        :returns: The count of checked nodes in the node's branch.

        """
        if self._checked_cache == None:
            count = 1 if self.checked() else 0
            for child in self._children:
                count += child.checked_count
            self._checked_cache = count
        return self._checked_cache

    @checked_count.setter
    def checked_count(self, value):
        """Sets the number of checked nodes in the branch of the node.

        Also sets the cache of checked nodes to the given value.

        :param value: The value to set the checked count to.
        :type value: :class:`int`

        """
        if self._checked_cache is not None:
            self._checked_cache = value

    def child(self, index):
        """Returns the node's child at the given index.

        :param index: The index of the child to return.
        :type index: :class:`int`

        :returns: The child :class:`.TreeNode` with the given index.

        """
        return self._children[index]

    def child_index(self):
        """Returns the index of the node in it's parent's children.

        :returns: The (integer) index of the node.

        """
        if self.parent:
            return self.parent._children.index(self)

        return None

    def append(self, node):
        """Adds a node to the current one's children.

        :param node: The node to add.
        :type node: :class:`.TreeNode`

        """
        self._children.append(node)
        self._adjust_caches(node.leaf_count, node.checked_count)

    def insert(self, index, node):
        """Inserts a node to the current one's children at a given position.

        :param index: The index where to insert the node.
        :type index: :class:`int`
        :param node: The node to insert.
        :type node: :class:`.TreeNode`

        """
        self._children.insert(index, node)
        self._adjust_caches(node.leaf_count, node.checked_count)

    def remove(self, index):
        """Removes a child at a given index from the node's children.

        :param index: The position of the child to remove.
        :type index: :class:`int`

        """
        node = self._children.pop(index)
        self._adjust_caches(-node.leaf_count, -node.checked_count)

    def _adjust_caches(self, delta_leaves, delta_checks):
        """Adjusts cached values according to given deltas.

        .. note::
            By calling this method, the caches of all parents of the node
            (including parent's parents) are also being adjusted.

        :param delta_leaves: Amount to adjust cached leaf counts by.
        :type delta_leaves: :class:`int`
        :param delta_checks: Amount to adjust cached check counts by.
        :type delta_checks: :class:`int`

        .. seealso ::
            :py:meth:`.leaf_count`
            :py:meth:`.checked_count`

        """
        if self._leaf_cache is not None and delta_leaves:
            self._leaf_cache += delta_leaves
        else:
            delta_leaves = 0  # Do not propagate beyond uninitialized nodes

        if self._checked_cache is not None and delta_checks:
            self._checked_cache += delta_checks
        else:
            delta_checks = 0  # Do not propagate beyond uninitialized nodes

        if self.parent and (delta_leaves or delta_checks):
            self.parent._adjust_caches(delta_leaves, delta_checks)

    def name(self):
        """Returns a string representation of the node's data.

        .. note::

            Derived classes should override this method to return
            an appropriate value.

        :returns: The string representation of the node's data.

        """
        return str(self.data)

    def checked(self):
        """Gets the checked state of the node.

        .. note::

            Derived classes have to define whatever the checked state
            describes and how it is determined.

        :returns: The boolean value of the checked state,
            or None if the state is undefined.

        """
        return None

    def check(self, state, origin=None):
        """Sets the checked state of the node.

        The checked state indicates whether or not an episode has been
        watched. When the state is set, the tree of the node is
        traversed upwards to its root, and the cached count of watched
        episodes in its branch is updated accordingly.

        :param state: The checked state to set.
        :type state: :class:`bool`
        :param origin: The node which initiated the check call. Used to
            determine when to traverse the tree upward.
        :type: :class:`.TreeNode`

        :returns: A (immutable) tuple of all changed nodes.

        .. seealso::

            :py:meth:`.checked`

        """
        changed = []
        total_changed = 0
        origin = self if origin is None else origin

        for child in self.children:
            count, result = child.check(state, origin)
            if result is not None:
                changed.append(result)
                total_changed += count
        if changed:
            self._checked_cache += total_changed
            if origin is self:
                parent = self.parent
                while parent and parent._checked_cache is not None:
                    parent._checked_cache += total_changed
                    parent = parent.parent
                return tuple(changed)
        return total_changed, tuple(changed)