"""
Hello World, but with more meat.
"""

import wx
import threading
import sys
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

class SceneGraph(wx.Panel, DirectObject):
    def refresh(self):
        if base.geom:
            self.buildings = None
            self.streets = None
            self.props = None
            self.previous = {}
            self.tree.DeleteAllItems()
            root = self.tree.AddRoot(base.geom.getName())
            self.recursiveAdd(root, base.geom)
            self.tree.Expand(root)

    def recursiveAdd(self, parent, node):
        #new_parent = None
        forced = False
        for n in node.getChildren():
            try:
                if forced:
                    raise ValueError()
                int(n.getName())
                self.recursiveAdd(parent, n)
            except ValueError as e:
                name = n.getName()
                if name.endswith('_DNARoot'):
                    name += "_" + str(hash(n))
                    n.setTag('clickable', bytes(1))
                    n.setCollideMask(BitMask32.bit(2))
                if self.previous.get(name):
                    parent = self.previous[name]
                    if name in ['buildings', 'props', 'streets']:
                        self.recursiveAdd(parent, n)
                        continue
                item = self.tree.AppendItem(parent, name)
                if not self.previous.get(name):
                    self.previous[name] = item
                self.tree.SetPyData(item, ('node', n))
                if forced:
                    item = parent
                self.recursiveAdd(item, n)

    def onSelect(self, event):
        item = event.GetItem()
        item = self.tree.GetItemData(item)
        if item:
            item = item[1]
            base.lvlEditor.selectItem(item)

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.accept('graph-refresh', self.refresh)
        sizer = wx.BoxSizer(wx.VERTICAL)
        #t = wx.StaticText(self, -1, "This is a PageOne object", (20,20))
        self.tree = wx.TreeCtrl(self, 1)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelect, self.tree)
        sizer.Add(self.tree, 1, wx.BOTTOM|wx.EXPAND, 25)
        parent.SetSizer(sizer)

class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageTwo object", (40,40))

class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageThree object", (60,60))

class ExternalPanel(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        #wx.Frame.__init__(self, *args, **kw)
        wx.Frame.__init__(self, None, title='External', size=(500, 700))
        # ensure the parent's __init__ is called

    def createPanel(self):
        #super(ExternalPanel, self).__init__(None, title='hi')
        # create a panel in the frame
        pnl = wx.Panel(self)
        nb = wx.Notebook(pnl)
        p1 = SceneGraph(nb)
        p2 = PageTwo(nb)
        p3 = PageThree(nb)

        nb.AddPage(p1, "Scene Graph")
        nb.AddPage(p2, "2")
        nb.AddPage(p3, "3")

        # put some text with a larger bold font on it
        #st = wx.StaticText(pnl, label="Hello World!")
        #font = st.GetFont()
        #font.PointSize += 10
        #font = font.Bold()
        #st.SetFont(font)

        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 1, wx.EXPAND)
        pnl.SetSizer(sizer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to Funny Farm!")
        #messenger.send('CUCK')
        #self.show()
        #app.MainLoop()


    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        loadItem = fileMenu.Append(-1, "&Load...\tCtrl-L",
                "Load a DNA file!")
        saveItem = fileMenu.Append(0, "&Save...\tCTRL-S",
                "Save a DNA file!")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnLoad, loadItem)
        self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        sys.exit(0)


    def OnLoad(self, event):
        with wx.FileDialog(self, "Open DNA file", wildcard="DNA files (*.dna)|*.dna", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            messenger.send('load-dna', [pathname])
            wx.MessageBox("Loaded %s!" % pathname)

    def OnSave(self, event):
        with wx.FileDialog(self, "Save DNA file", wildcard="DNA files (*.dna)|*.dna", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            messenger.send('save-dna', [pathname])
            wx.MessageBox("Saved to %s!" % pathname)


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a broken code store product.",
                      "About Funny Farm Level Editor",
                      wx.OK|wx.ICON_INFORMATION)
