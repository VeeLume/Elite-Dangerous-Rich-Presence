from multiprocessing import Pipe, Process, Queue

import win32gui
import asyncio

from TrayApp import TrayApp
from SettingsApp import SettingsApp


def open_settings(con):
    SettingsApp(con).run()
    con.send("closed")


class BackgroundApp():
    open_settings: bool = False
    q = Queue()

    def open_settings_call(self):
        if self.open_settings:
            self.parent_con.send("restore")
        else:
            self.open_settings = True

    async def app_func(self):
        self.tray = TrayApp(self.open_settings_call,
                            name="Elite Dangerous Rich Presence")

        self.parent_con, child_con = Pipe()
        app_settings = Process(target=open_settings, args=(child_con,))

        code = 0
        while code == 0:
            code = win32gui.PumpWaitingMessages()

            if self.open_settings and not app_settings.is_alive():
                app_settings.start()

            if self.parent_con.poll():
                msg = self.parent_con.recv()
                if msg == "closed":
                    app_settings = Process(
                        target=open_settings, args=(child_con,))
                    self.open_settings = False
                elif msg == "changed_settings":
                    pass

        self.parent_con.send("closed")


if __name__ == '__main__':
    asyncio.run(BackgroundApp().app_func())
