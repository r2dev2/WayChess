import time
from threading import Thread, get_ident

import pygame as pg
import pygame_gui as pgg

class TextEntry(pgg.elements.UITextEntryLine):
    """
    Text Entry Class with focus callbacks
    """
    def __init__(self, onfocus, onunfocus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._focus_callback = onfocus
        self._unfocus_callback = onunfocus
        self.args = args
        self.kwargs = kwargs

    def focus(self, *args, **kwargs):
        self._focus_callback()
        super().focus(*args, **kwargs)

    def unfocus(self, *args, **kwargs):
        self._unfocus_callback(*args, **kwargs)
        super().unfocus(*args, **kwargs)


class TextShow(pgg.elements.UITextBox):
    """
    Text Box class with focus callbacks
    """
    def __init__(self, onfocus, onunfocus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._focus_callback = onfocus
        self._unfocus_callback = onunfocus

    def focus(self, *args, **kwargs):
        self._focus_callback()
        super().focus(*args, **kwargs)

    def unfocus(self, *args, **kwargs):
        self._unfocus_callback()
        super().unfocus(*args, **kwargs)


class GUI:
    has_made_ui = False
    def create_ui(self):
        if not GUI.has_made_ui:
            self.stdout("Creating ui")
            self.create_manager()
            self.create_ui_comment()

            self.create_engine_box()
            
            self.create_ui_comment_edit()
            self.comment_edit_box.hide()
            self.set_ui_comment()
            GUI.has_made_ui = True

    def display_size_refresh(self):
        """
        Used to refresh the display size in order to reload the ui

        Now just calls self.background()
        """
        self.stdout("[DISPLAY SIZE GET]", self.display_size)
        self.background()

    def box_hide(self, boxname, reloa=False):
        self.stdout("HIDING", boxname, reloa)
        self.action_queue.append(getattr(self, boxname).hide)
        if reloa:
            self.action_queue.append(self.display_size_refresh)

    def box_show(self, boxname, reloa=True):
        self.stdout("SHOWING", boxname, reloa)
        self.action_queue.append(getattr(self, boxname).show)
        if reloa:
            self.action_queue.append(self.display_size_refresh)

    def set_ui_comment(self, *args, **kwargs):
        comment = self.node.comment
        self.stdout("[COMMENT]", comment)
        try:
            self.comment_box.html_text = comment
            self.comment_box.rebuild()
            self.box_hide("comment_edit_box")
            self.box_show("comment_box")
        except AttributeError:
            pass
        self.set_ui(False)

    def create_ui_comment(self):
        self.comment_box = TextShow(
                    lambda : self.set_ui_comment_edit(),
                    lambda : None,
                    '',
                    pg.Rect((45, 555), (445, 630)),
                    self.manager,
                    object_id="#commentshow")
        self.comment_box.set_dimensions((400, 630-555))

    def create_ui_comment_edit(self):
        self.comment_edit_box = TextEntry(
                    onfocus=lambda : self.set_ui(True),
                    onunfocus=lambda : self.set_ui_comment(),
                    relative_rect = pg.Rect((45, 555), (445, -1)),
                    manager=self.manager,
                    object_id="#commentedit")

    def set_ui_comment_edit(self):
        self.box_hide("comment_box")
        self.box_show("comment_edit_box")
        self.comment_edit_box.set_text(self.node.comment)
        self.comment_edit_box.rebuild()

    def create_engine_box(self, text=''):
        try:
            self.engine_box.html_text = text
            b = time.time()
            self.engine_box.rebuild()
            self.stdout("[UI] Engine box rebuild at t =", time.time()-b, "seconds")
            self.engine_box.show()
            self.stdout("[UI] Engine box show at t =", time.time()-b, "seconds")
        except AttributeError:
            b = time.time()
            self.engine_box = TextShow(
                    lambda : self.stdout("focus"),
                    lambda : self.stdout("unfocus"),
                    text,
                    relative_rect=pg.Rect((35, 650), (755, 795)), 
                    manager=self.manager,
                    object_id="#engineeval")

            # Need to set dimensions again due to pygame_gui bug
            self.engine_box.set_dimensions((755-35, 795-650))
            self.engine_box.hide()
            self.engine_box.show()
            GUI.has_made_ui = True
            self.stdout("[UI] INIT: Built engine box in %f seconds" % (time.time()-b))

    def create_manager(self):
        try:
            self.manager
        except AttributeError:
            self.manager = pgg.UIManager((800, 800), self.pwd / "theme.json")

    def set_ui(self, val=None):
        if val is None:
            self.onui = not self.onui
        else:
            self.onui = val

    def update_ui(self, event):
        try:
            if event.type == pg.USEREVENT:
                self.stdout("[UI]", event)
                if event.user_type == "ui_text_entry_finished":
                    self.stdout("[TEXTENTRY] FINISHED")
                    self.node.comment = event.text
                    self.comment_edit_box.hide()
                    self.set_ui_comment()

                # Do not switch comment box type if scrolling
                if "scroll" in event.ui_object_id:
                    self.action_execute[:] = []
            else:
                self.handle_event(event)
        except Exception as e:
            self.manager.process_events(event)
            raise e
        self.manager.process_events(event)

