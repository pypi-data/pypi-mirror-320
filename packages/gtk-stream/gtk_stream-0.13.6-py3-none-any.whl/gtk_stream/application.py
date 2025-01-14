# Gtk-Stream : A stream-based GUI protocol
# Copyright (C) 2024  Marc Coiffier
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import threading
import signal

from . import Gtk, GLib, Gdk
from .common import print_event
from .properties import parse_property, get_prop_type, set_parse_prop

class _Object:
    pass

def app_message(name, store = None):
    """A decorator for methods that are both called from the pilot
    application and need access to the gtk main thread"""
    def app_message_f(f):
        def ret(self, *args, **kwargs):
            def cb():
                f(self, *args, **kwargs)
            self.run_when_idle(cb)
        ret.__tag_name__ = name
        ret.__store__ = store
        return ret
    return app_message_f

def single_store():
    store = _Object()
    def setChild(child):
        store.child = child
    return (lambda: store.child, setChild, None)
def multiple_store():
    children = []
    return (lambda: children, children.append, None)
def style_store():
    style = []
    return (lambda: " ".join(style),None, style.append)

class GtkStreamApp(Gtk.Application):
    def __init__(self, logger, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger
        self.named_widgets = { }
        self.named_windows = { }
        
        # The first messages from the pilot may arrive before the
        # application is ready to process them.
        # 
        # If that happens, store the actions until they can be taken
        # (when the "startup" signal is called)
        callback_queue = []
        def run_when_idle_before_startup(cb):
            callback_queue.append(cb)
        self.run_when_idle = run_when_idle_before_startup
        
        def on_startup(_):
            for cb in callback_queue:
                GLib.idle_add(cb)
            self.run_when_idle = GLib.idle_add

            def on_sigint(a,b):
                self.logger.info("SIGINT received, quitting application")
                self.quit()
            signal.signal(signal.SIGINT, on_sigint)
        self.connect('startup', on_startup)

        def on_activate(a):
            a.hold()
        self.connect('activate', on_activate)

        self.attrs_set = threading.Semaphore()
        self.attrs_set.acquire()
        
    def name_widget(self, id, w):
        if id is not None:
            self.named_widgets[id] = w

    def wait_for_init(self):
        self.attrs_set.acquire()
        
    def set_attrs(self, attrs):
        for name, val in attrs.items():
            set_parse_prop(self, self, name, val)
        self.attrs_set.release()
            
    @app_message('file-dialog')
    def open_file_dialog(self, id, parent):
        dialog = Gtk.FileDialog()
        dialog.props.modal = True
        def on_choose(_, b):
            try:
                file = dialog.open_finish(b)
                print(f"{id}:selected:{file.get_path()}")
                sys.stdout.flush()
            except GLib.GError as e:
                print(f"{id}:none-selected")
                sys.stdout.flush()
                
        dialog.open(parent = self.named_windows[parent], callback = on_choose)

    @app_message('window', single_store)
    def new_window(self, document, id, **attrs):
        win = Gtk.Window(application=self)
        for (attr_name, attr_val) in attrs.items():
            self.logger.debug("Setting attr '%s' on window", attr_name)
            set_parse_prop(self, win, attr_name, attr_val)
        self.named_windows[id] = win
        win.set_child(document.render())
        win.connect('close-request', print_event(self.logger, 'close-request', id))
        win.present()

    @app_message('style', style_store)
    def add_style(self, style):
        provider = Gtk.CssProvider()
        provider.load_from_data(style)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    @app_message('add-icon-path')
    def add_icon_path(self, path):
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        theme.add_search_path(path)
        
    @app_message('close-window')
    def close_window(self, id):
        self.named_windows[id].close()

    @app_message('remove')
    def remove_widget(self, id):
        w = self.named_widgets[id]
        w.get_parent().remove(w)

    @app_message('insert', multiple_store)
    def insert_widgets(self, documents, into):
        for doc in documents:
            self.insert_widget(doc, into)

    def insert_widget(self, document, into):
        if into in self.named_widgets:
            w = self.named_widgets[into]
            w.insert_child(document)
        else:
            raise Exception(f"Error: unknown widget id '{into}'")
    
    @app_message('set-prop')
    def set_prop(self, id, name, value):
        w = self.named_widgets[id]
        w.set_property(name, parse_property(get_prop_type(w.__class__, name), value)(self))

