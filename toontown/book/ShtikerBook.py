from panda3d.core import *
from libotp import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer

class ShtikerBook(DirectFrame):
    notify = directNotify.newCategory('ShtikerBook')

    def __init__(self):
        DirectFrame.__init__(self, relief=None, sortOrder=DGG.BACKGROUND_SORT_INDEX)
        keybinds = settings['keybinds'][base.getCurrentDevice()]
        self.shtiker = keybinds['shtiker']
        self.option = keybinds['options']
        self.initialiseoptions(ShtikerBook)
        self.pages = []
        self.pageTabs = []
        self.currPage = 1
        self.currPageTab = 1
        self.pageTabFrame = DirectFrame(parent=self, relief=None, pos=(0.93, 1, 0.575), scale=1.25)
        self.pageTabFrame.hide()
        self.isOpen = 0
        self.__obscured = 0
        self.__shown = 0
        self.esc = False
        self.hide()
        self.setPos(0, 0, 0.1)

    def enter(self):
        if self.isOpen:
            return
        self.isOpen = 1
        base.localAvatar.exitOpenBook()
        base.localAvatar.enterReadBook()
        base.playSfx(self.openSound)
        base.disableMouse()
        base.render.hide()
        base.setBackgroundColor(0.05, 0.15, 0.4)
        self.__setButtonVisibility()
        self.show()
        self.showPageArrows()
        self.pageTabFrame.show()
        if self.esc:
            self.setPage(self.pages[0])
        else:
            self.setPage(self.pages[self.currPage])
        keybinds = settings['keybinds'][base.getCurrentDevice()]
        self.shtiker = keybinds['shtiker']
        self.option = keybinds['options']
        self.accept(self.shtiker, self.close)
        self.accept(self.option, self.close)
        self.turn_right = keybinds['turn_right']
        self.turn_left = keybinds['turn_left']
        self.accept(self.turn_right, self.rightArrow)
        self.accept(self.turn_left, self.leftArrow)

    def exit(self):
        if not self.isOpen:
            return
        self.isOpen = 0
        base.playSfx(self.closeSound)
        self.pages[self.currPage].exit()
        base.render.show()
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        gsg = base.win.getGsg()
        if gsg:
            base.render.prepareScene(gsg)
        self.hide()
        self.hideButton()
        self.pageTabFrame.hide()
        self.ignore(self.shtiker)
        self.ignore(self.option)
        self.ignore(self.turn_right)
        self.ignore(self.turn_left)

    def load(self):
        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        self['image'] = bookModel.find('**/big_book')
        self['image_scale'] = (2, 1, 1.5)
        self.resetFrameSize()
        self.bookOpenButton = DirectButton(image=(bookModel.find('**/BookIcon_CLSD'), bookModel.find('**/BookIcon_OPEN'), bookModel.find('**/BookIcon_RLVR')), relief=None, pos=(-0.158, 0, 0.17), parent=base.a2dBottomRight, scale=0.305, command=self.open)
        self.bookCloseButton = DirectButton(image=(bookModel.find('**/BookIcon_OPEN'), bookModel.find('**/BookIcon_CLSD'), bookModel.find('**/BookIcon_RLVR2')), relief=None, pos=(-0.158, 0, 0.17), parent=base.a2dBottomRight, scale=0.305, command=self.close)
        self.bookOpenButton.hide()
        self.bookCloseButton.hide()
        self.nextArrow = DirectButton(parent=self, relief=None, image=(bookModel.find('**/arrow_button'), bookModel.find('**/arrow_down'), bookModel.find('**/arrow_rollover')), scale=(0.1, 0.1, 0.1), pos=(0.838, 0, -0.661), command=self.rightArrow)
        self.prevArrow = DirectButton(parent=self, relief=None, image=(bookModel.find('**/arrow_button'), bookModel.find('**/arrow_down'), bookModel.find('**/arrow_rollover')), scale=(-0.1, 0.1, 0.1), pos=(-0.838, 0, -0.661), command=self.leftArrow)
        bookModel.removeNode()
        self.openSound = base.loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_open.ogg')
        self.closeSound = base.loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_delete.ogg')
        self.pageSound = base.loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_turn.ogg')
        return

    def unload(self):
        loader.unloadModel('phase_3.5/models/gui/stickerbook_gui')
        self.destroy()
        self.bookOpenButton.destroy()
        del self.bookOpenButton
        self.bookCloseButton.destroy()
        del self.bookCloseButton
        self.nextArrow.destroy()
        del self.nextArrow
        self.prevArrow.destroy()
        del self.prevArrow
        for page in self.pages:
            page.unload()
        del self.pages
        for pageTab in self.pageTabs:
            pageTab.destroy()
        del self.pageTabs
        del self.currPageTab
        del self.openSound
        del self.closeSound
        del self.pageSound

    def addPage(self, page, pageName = 'Page'):
        pageIndex = 0
        self.pages.append(page)
        pageIndex = len(self.pages) - 1
        page.setBook(self)
        page.setPageName(pageName)
        page.reparentTo(self)
        self.addPageTab(page, pageIndex, pageName)

    def addPageTab(self, page, pageIndex, pageName = 'Page'):
        tabIndex = len(self.pageTabs)

        def goToPage():
            messenger.send('wakeup')
            if self.currPage != pageIndex:
                base.playSfx(self.pageSound)
                self.setPage(page)

        yOffset = 0.07 * pageIndex
        iconGeom = None
        iconImage = None
        iconScale = 1
        iconColor = Vec4(1)
        buttonPressedCommand = goToPage
        extraArgs = []
        if pageName == TTLocalizer.OptionsPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/switch')
            iconModels.detachNode()
        elif pageName == TTLocalizer.ToonPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/district')
            iconScale = (0.8, 1, 1)
            iconModels.detachNode()
        elif pageName == TTLocalizer.MapPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/compass')
            iconModels.detachNode()
        elif pageName == TTLocalizer.InventoryPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            iconGeom = iconModels.find('**/inventory_cup_cake')
            iconScale = 7
            iconModels.detachNode()
        elif pageName == TTLocalizer.QuestPageToonTasks:
            iconModels = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
            iconGeom = iconModels.find('**/questCard')
            iconScale = 0.9
            iconModels.detachNode()
        elif pageName == TTLocalizer.TrackPageShortTitle:
            iconGeom = iconModels = loader.loadModel('phase_3.5/models/gui/filmstrip')
            iconScale = 1.1
            iconColor = Vec4(0.7, 0.7, 0.7, 1)
            iconModels.detachNode()
        elif pageName == TTLocalizer.SuitPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/gui_gear')
            iconModels.detachNode()
        elif pageName == TTLocalizer.FishPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/fish')
            iconModels.detachNode()
        elif pageName == TTLocalizer.GardenPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/gardenIcon')
            iconModels.detachNode()
        elif pageName == TTLocalizer.DisguisePageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/disguise2')
            iconColor = Vec4(0.7, 0.7, 0.7, 1)
            iconModels.detachNode()
        elif pageName == TTLocalizer.NPCFriendPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/playingCard')
            iconImage = iconModels.find('**/card_back')
            iconGeom = iconModels.find('**/logo')
            iconScale = 0.22
            iconModels.detachNode()
        elif pageName == TTLocalizer.KartPageTitle:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/kartIcon')
            iconModels.detachNode()
        elif pageName == TTLocalizer.GolfPageTitle:
            iconModels = loader.loadModel('phase_6/models/golf/golf_gui')
            iconGeom = iconModels.find('**/score_card_icon')
            iconModels.detachNode()
        elif pageName == TTLocalizer.EventsPageName:
            iconModels = loader.loadModel('phase_4/models/parties/partyStickerbook')
            iconGeom = iconModels.find('**/Stickerbook_PartyIcon')
            iconModels.detachNode()
        elif pageName == TTLocalizer.PhotoPageTitle:
            iconGeom = iconModels = loader.loadModel('phase_4/models/minigames/photogame_filmroll')
            iconScale = (1.9, 1.5, 1.5)
            iconModels.detachNode()
        elif pageName == TTLocalizer.NewsPageName:
            iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
            iconGeom = iconModels.find('**/tt_t_gui_sbk_newsPageTab')
            iconModels.detachNode()
            buttonPressedCommand = self.goToNewsPage
            extraArgs = [page]
        if pageName == TTLocalizer.OptionsPageTitle:
            pageName = TTLocalizer.OptionsTabTitle
        pageTab = DirectButton(parent=self.pageTabFrame, relief=DGG.RAISED, frameSize=(-0.575,
         0.575,
         -0.575,
         0.575), borderWidth=(0.05, 0.05), text=('',
         '',
         pageName,
         ''), text_align=TextNode.ALeft, text_pos=(1, -0.2), text_scale=TTLocalizer.SBpageTab, text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), image=iconImage, image_scale=iconScale, geom=iconGeom, geom_scale=iconScale, geom_color=iconColor, pos=(0, 0, -yOffset), scale=0.06, command=buttonPressedCommand, extraArgs=extraArgs)
        self.pageTabs.insert(pageIndex, pageTab)
        return

    def setPage(self, page, enterPage = True):
        if self.currPage is not None:
            self.pages[self.currPage].exit()
        self.currPage = self.pages.index(page)
        self.setPageTabIndex(self.currPage)
        if enterPage:
            self.showPageArrows()
            page.enter()
        return

    def setPageTabIndex(self, pageTabIndex):
        if self.currPageTab is not None and pageTabIndex != self.currPageTab:
            self.pageTabs[self.currPageTab]['relief'] = DGG.RAISED
        self.currPageTab = pageTabIndex
        self.pageTabs[self.currPageTab]['relief'] = DGG.SUNKEN
        return

    def rightArrow(self):
        base.playSfx(self.pageSound)
        if self.currPage == self.pages.index(self.pages[-1]):
            self.setPage(self.pages[0])
        else:
            self.setPage(self.pages[self.currPage + 1])

    def leftArrow(self):
        base.playSfx(self.pageSound)
        self.setPage(self.pages[self.currPage - 1])

    def showPageArrows(self):
        if self.currPage == 0:
            self.prevArrow.hide()
            self.nextArrow.show()
        elif self.currPage == len(self.pages) - 1:
            self.prevArrow.show()
            self.nextArrow.hide()
        else:
            self.prevArrow.show()
            self.nextArrow.show()

    def obscureButton(self, obscured):
        self.__obscured = obscured
        self.__setButtonVisibility()

    def isObscured(self):
        return self.__obscured

    def showButton(self):
        self.__shown = 1
        self.__setButtonVisibility()
        self.accept(self.shtiker, self.open)
        self.accept(self.options, self.open, [True])

    def hideButton(self):
        self.__shown = 0
        self.__setButtonVisibility()
        self.ignore(self.shtiker)
        self.ignore(self.options)

    def __setButtonVisibility(self):
        if self.isOpen:
            self.bookOpenButton.hide()
            self.bookCloseButton.show()
        elif self.__shown:
            self.bookOpenButton.show()
            self.bookCloseButton.hide()
        else:
            self.bookOpenButton.hide()
            self.bookCloseButton.hide()

    def open(self, esc=False):
        self.esc = esc
        base.localAvatar.disable()
        base.localAvatar.enterOpenBook()
        Sequence(Wait(base.localAvatar.track.getDuration() - 0.1), Func(self.enter)).start()

    def close(self):
        self.exit()
        base.localAvatar.exitReadBook()
        base.localAvatar.enterCloseBook(callback=self.__handleClose)

    def exitFunnyFarm(self):
        self.exit()
        base.localAvatar.exitReadBook()
        base.localAvatar.enterCloseBook(callback=base.cr.exitTheTooniverse)

    def teleportTo(self, zoneId):
        self.exit()
        base.localAvatar.exitReadBook()
        base.localAvatar.enterCloseBook(callback=base.cr.teleportTo, extraArgs=[zoneId])

    def __handleClose(self):
        self.showButton()
        base.localAvatar.enable()
