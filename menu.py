# coding=utf-8
import json
import subprocess
import shlex


class Factory(object):
    @staticmethod
    def create(resource):
        raise NotImplementedError


class MenuFactory(Factory):
    @staticmethod
    def create(resource):
        json_array = json.load(open(resource))
        if "name" in json_array and "desc" in json_array and "root" in json_array:
            menu = Menu(json_array["name"], json_array["desc"])
            root = MenuItemFactory.create(json_array["root"])
            menu.add_root(root)
            return menu
        else:
            raise ValueError


class MenuItemFactory(Factory):
    @staticmethod
    def create(resource):
        if "name" in resource and "desc" in resource:
            if "children" in resource:
                branch = Branch(resource["name"], resource["desc"])
                for child in resource["children"]:
                    branch.add_child(MenuItemFactory.create(child))
                return branch
            elif "command" in resource and "command_type" in resource:
                leaf = Leaf(resource["name"], resource["desc"])
                leaf.set_action(resource["command"], resource["command_type"])
                return leaf
            else:
                raise ValueError
        else:
            raise ValueError


class Menu(object):
    def __init__(self, name, description):
        self.name = name
        self.desc = description
        self.root = MenuItem("Nothing", "Menu uninitialized")

    def add_root(self, root):
        self.root = root
        root.parent = None

    def get_len(self):
        return self.root.get_len()

    def get_depth(self):
        return self.root.get_depth()

    def get_strings(self):
        """
        returns a list of all strings in the tree
        :return: list of all strings
        """
        return self.root.get_strings() + [self.name, self.desc]


class MenuItem(object):
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.parent = None

    def get_len(self):
        raise NotImplementedError

    def get_depth(self):
        raise NotImplementedError

    def get_strings(self):
        return [self.name, self.desc]


class Branch(MenuItem):
    def __init__(self, name, desc):
        super(Branch, self).__init__(name, desc)
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def get_len(self):
        return sum([child.get_len() for child in self.children]) + 1

    def get_depth(self):
        return max([child.get_len() for child in self.children]) + 1

    def get_strings(self):
        strs = []
        for child in self.children:
            strs += child.get_strings()
        return strs + [self.name, self.desc]


class Leaf(MenuItem):
    def __init__(self, name, desc):
        super(Leaf, self).__init__(name, desc)
        self.command = ""
        self.command_type = None

    def set_action(self, action, command_type):
        self.command = action
        self.command_type = command_type

    def execute(self):
        if self.command_type == "read-output":
            result = subprocess.check_output(shlex.split(self.command))
            return result

        elif self.command_type == "execute":
            subprocess.Popen(shlex.split(self.command), stdin=None, stdout=None, stderr=None, close_fds=True)
        else:
            pass

    def get_len(self):
        return 1

    def get_depth(self):
        return 0


class MenuNavigator(object):
    def __init__(self, menu):
        self.current_node = menu.root
        self.selected_index = 0
        self._handlers = []

    def down(self, *args):
        if isinstance(self.get_selected(), Branch):
            self.current_node = self.get_selected()
            self.selected_index = 0
        elif isinstance(self.get_selected(), Leaf):
            return self.get_selected().execute()

    def left(self, *args):
        self.selected_index -= 1
        if self.selected_index < 0:
            self.selected_index = len(self.current_node.children) - 1

    def right(self, *args):
        self.selected_index += 1
        if self.selected_index >= len(self.current_node.children):
            self.selected_index = 0

    def get_selected(self):
        return self.current_node.children[self.selected_index]

    def up(self, *args):
        print "current", self.current_node.name
        if self.current_node.parent is not None:
            self.current_node = self.current_node.parent
            self.selected_index = 0
        print "current", self.current_node.name

