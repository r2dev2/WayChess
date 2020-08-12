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
        print("[TEXTSHOW] Created", self.html_text)

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
            self.engine_box.hide()
            
            self.create_ui_comment_edit()
            self.comment_edit_box.hide()
            self.set_ui_comment()
            GUI.has_made_ui = True

    def set_ui_comment(self, *args, **kwargs):
        comment = self.node.comment
        self.stdout("[COMMENT]", comment)
        try:
            self.comment_box.html_text = comment
            self.comment_box.rebuild()
            self.comment_edit_box.hide()
            self.comment_box.show()
        except AttributeError:
            pass
        self.set_ui(False)

    def create_ui_comment(self):
        self.comment_box = TextShow(
                    lambda : self.set_ui_comment_edit(),
                    lambda : print("unfocussing on text box"),
                    '',
                    pg.Rect((45, 555), (445, 600)),
                    self.manager)
        self.comment_box.set_dimensions((400, 45))

    def create_ui_comment_edit(self):
        self.comment_edit_box = TextEntry(
                    onfocus=lambda : self.set_ui(True),
                    onunfocus=lambda : self.set_ui_comment(),
                    relative_rect=pg.Rect((45, 610), (445, -1)),
                    manager=self.manager,
                    object_id="#commentedit")

    def set_ui_comment_edit(self):
        self.comment_box.hide()
        self.comment_edit_box.show()
        self.comment_edit_box.set_text(self.node.comment)
        self.comment_edit_box.rebuild()

    def create_engine_box(self, text='hi'):
        try:
            self.engine_box.html_text = text
            self.engine_box.rebuild()
            self.engine_box.show()
        except AttributeError:
            self.engine_box = TextShow(
                    lambda : print("focus"),
                    lambda : print("unfocus"),
                    text,
                    relative_rect=pg.Rect((35, 650), (755, 795)), 
                    manager=self.manager,
                    object_id="#engineeval")

            # Need to set dimensions again due to pygame_gui bug
            self.engine_box.set_dimensions((755-35, 795-650))
            self.engine_box.hide()
            self.engine_box.show()
            GUI.has_made_ui = True

    def create_manager(self):
        try:
            self.manager
        except AttributeError:
            self.manager = pgg.UIManager((800, 800), "theme.json")

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
                    print("FINISHED")
                    self.node.comment = event.text
                    self.set_ui_comment()
                    self.comment_edit_box.hide()
            else:
                self.handle_event(event)
        except Exception as e:
            self.manager.process_events(event)
            raise e
        self.manager.process_events(event)

