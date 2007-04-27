from xpcom import components
import ctypes
from ctypes.wintypes import DWORD, HWND, HANDLE, LPCWSTR, WPARAM, LPARAM, RECT
UINT = ctypes.c_uint
WCHAR = ctypes.c_wchar
INT = ctypes.c_int

WM_USER = 0x0400
WM_TRAYICON = WM_USER+0x1EEF
WM_GETICON = 0x007F
WM_SETICON = 0x0080
WS_EX_APPWINDOW = 0x00040000L
ICON_SMALL = 0
ICON_BIG   = 1

IMAGE_ICON = 1

LR_LOADFROMFILE = 0x0010

NIF_MESSAGE = 0x00000001
NIF_ICON    = 0x00000002
NIF_TIP     = 0x00000004

WM_LBUTTONDOWN                 = 0x0201
WM_LBUTTONUP                   = 0x0202
WM_LBUTTONDBLCLK               = 0x0203
WM_RBUTTONDOWN                 = 0x0204
WM_RBUTTONUP                   = 0x0205
WM_RBUTTONDBLCLK               = 0x0206
WM_MBUTTONDOWN                 = 0x0207
WM_MBUTTONUP                   = 0x0208
WM_MBUTTONDBLCLK               = 0x0209
WM_XBUTTONDOWN                 = 0x020B
WM_XBUTTONUP                   = 0x020C
WM_XBUTTONDBLCLK               = 0x020D

NIM_ADD     = 0
NIM_DELETE  = 2

IDI_APPLICATION = 32512
IDI_WINLOGO = 32517

ABM_GETTASKBARPOS = 5
ABE_LEFT       = 0
ABE_TOP        = 1
ABE_RIGHT      = 2
ABE_BOTTOM     = 3

IDANI_OPEN         = 1
IDANI_CAPTION      = 3

SW_HIDE = 0
SW_SHOW = 5

WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.c_int, HWND, UINT, WPARAM, LPARAM)

import config
import prefs
import resources

class GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_int32),
                ("Data2", ctypes.c_int16),
                ("Data3", ctypes.c_int16),
                ("Data4", ctypes.c_byte * 8),
                ]

class TIMEOUT(ctypes.Union):
    _fields_ = [("uTimeout", UINT),
                ("uVersion", UINT),
                ]

class NOTIFYICONDATA(ctypes.Structure):
    _fields_ = [("cbSize", DWORD),
                ("hWnd", HWND),
                ("uID", UINT),
                ("uFlags", UINT),
                ("uCallbackMessage", UINT),
                ("hIcon", HANDLE),
                ("szTip", WCHAR * 64),
                ("dwState", DWORD),
                ("dwStateMask", DWORD),
                ("szInfo", WCHAR * 256),
                ("timeout", TIMEOUT),
                ("szInfoTitle", WCHAR * 64),
                ("dwInfoFlags", DWORD),
                ("guidItem", GUID),
                ("hBalloonIcon", HANDLE),
                ]

class WNDCLASSEX(ctypes.Structure):
    _fields_ = [("cbSize", UINT),
                ("style", UINT),
                ("lpfnWndProc", WNDPROCTYPE),
                ("cbClsExtra", INT),
                ("cbWndExtra", INT),
                ("hInstance", HANDLE),
                ("hIcon", HANDLE),
                ("hCursor", HANDLE),
                ("hBrush", HANDLE),
                ("lpszMenuName", LPCWSTR),
                ("lpszClassName", LPCWSTR),
                ("hIconSm", HANDLE),
                ]
class APPBARDATA(ctypes.Structure):
    _fields_ = [("cbSize", DWORD),
                ("hWnd", HANDLE),
                ("uCallbackMessage", UINT),
                ("uEdge", UINT),
                ("rc", RECT),
                ("lParam", LPARAM)]

def PyWindProc(hWnd, uMsg, wParam, lParam):
    if uMsg == WM_TRAYICON:
        if lParam in [WM_LBUTTONUP, WM_MBUTTONUP, WM_RBUTTONUP]:
            Minimize.minimizers[hWnd].restoreAll()   
    #components.classes['@mozilla.org/consoleservice;1'].getService(components.interfaces.nsIConsoleService).logStringMessage("PYWINPROC %d %d %d %d" % (hWnd, uMsg, wParam, lParam))
    return ctypes.windll.user32.CallWindowProcW(ctypes.windll.user32.DefWindowProcW,hWnd, uMsg, wParam, lParam)

WindProc = WNDPROCTYPE(PyWindProc)

class Minimize:
    _com_interfaces_ = [components.interfaces.pcfIDTVMinimize]
    _reg_clsid_ = "{C8F996EC-599E-4749-9A70-EE9B7662981F}"
    _reg_contractid_ = "@participatoryculture.org/dtv/minimize;1"
    _reg_desc_ = "Minimizize and restorizor windizows"

    minimizers = {}

    def __init__(self):
        self.iconinfo = None
        self.wclassName = ctypes.c_wchar_p(u"PCF:DTV:Minimize:MessageWindowClass")
        self.wname = ctypes.c_wchar_p(u"PCF:DTV:Minimize:MessageWindow")
        self._gethrefcomp = components.classes["@participatoryculture.org/dtv/gethref;1"].getService(components.interfaces.pcfIDTVGetHREF)
        self.hInst = ctypes.windll.kernel32.GetModuleHandleW(0)
        self.wndClass = WNDCLASSEX(ctypes.sizeof(WNDCLASSEX),
                                   ctypes.c_uint(0x4200), # CS_NOCLOSE | CS_GLOBALCLASS
                                   WindProc,
                                   0,
                                   0,
                                   self.hInst,
                                   0,
                                   0,
                                   0,
                                   0,
                                   self.wclassName,
                                   0)
        ctypes.windll.user32.RegisterClassExW(ctypes.byref(self.wndClass))
        self.trayIconWindow = ctypes.windll.user32.CreateWindowExW(
            WS_EX_APPWINDOW,
            self.wclassName,
            self.wname,
            0x20000000L, #WS_MINIMIZE
            0x80000000, #CW_USEDEFAULT
            0x80000000, #CW_USEDEFAULT
            0x80000000, #CW_USEDEFAULT
            0x80000000, #CW_USEDEFAULT
            ctypes.windll.user32.GetDesktopWindow(),
            0,
            self.hInst,
            0)
        Minimize.minimizers[self.trayIconWindow] = self

        # By default, everything uses the XULRunner icon
        # Use the Democracy icon instead
        self.iconloc = ctypes.c_wchar_p(resources.path("..\\Democracy.ico"))
        self.hIcon = ctypes.windll.user32.LoadImageW(0, self.iconloc, IMAGE_ICON, 0, 0, LR_LOADFROMFILE)

        self.minimized = []

    def __del__(self):
        del Minimize.minimizers[self.trayIconWindow]
        self.delTrayIcon()

    def getHREFFromBaseWindow(self, win):
        return ctypes.c_int(self._gethrefcomp.getit(win))

    def getHREFFromDOMWindow(self,win):
        win = win.queryInterface(components.interfaces.nsIInterfaceRequestor)
        win = win.getInterface(components.interfaces.nsIWebNavigation)
        win = win.queryInterface(components.interfaces.nsIDocShellTreeItem)
        win = win.treeOwner
        win = win.queryInterface(components.interfaces.nsIInterfaceRequestor)
        win = win.getInterface(components.interfaces.nsIXULWindow)
        win = win.docShell
        win = win.queryInterface(components.interfaces.nsIDocShell)
        win = win.queryInterface(components.interfaces.nsIBaseWindow)
        return self.getHREFFromBaseWindow(win)

    def minimizeAll(self):
        self.minimized = []
        mediator = components.classes["@mozilla.org/appshell/window-mediator;1"].getService(components.interfaces.nsIWindowMediator)
        winList = mediator.getEnumerator(None)
        while (winList.hasMoreElements()):
            win = winList.getNext()
            href = self.getHREFFromDOMWindow(win)
            self.minimized.append(href)
            self.minimize(href)
        self.addTrayIcon()

    def addTrayIcon(self):
        self.iconinfo = NOTIFYICONDATA(ctypes.sizeof(NOTIFYICONDATA),
                                  self.trayIconWindow,
                                  1,
                                  NIF_ICON | NIF_MESSAGE | NIF_TIP,
                                  WM_TRAYICON,
                                  self.hIcon,
                                  config.get(prefs.LONG_APP_NAME),
                                  0,
                                  0,
                                  config.get(prefs.LONG_APP_NAME)+" is AWESOME",
                                  TIMEOUT(0,0),
                                  config.get(prefs.LONG_APP_NAME)+" is COOL",
                                  0,
                                  GUID(0,0,0,(ctypes.c_byte*8)(0,0,0,0,0,0,0,0)),
                                  0
                                  )
        ctypes.windll.shell32.Shell_NotifyIconW(NIM_ADD,ctypes.byref(self.iconinfo))

    def delTrayIcon(self):
        if self.iconinfo:
            ctypes.windll.shell32.Shell_NotifyIconW(NIM_DELETE,ctypes.byref(self.iconinfo))

    def getTrayRect(self):
        trayRect = RECT(0,0,0,0)

        # I don't think this ever actually works with modern windows,
        # but gAIM does this, so I'll do it to like the sheep I am -NN
        trayWindow = ctypes.windll.user32.FindWindowExW(0,0,"Shell_TrayWnd",0)
        if trayWindow != 0:
            trayNotifyWindow = ctypes.windll.user32.FindWindowEx(trayWindow,0,"TrayNotifyWnd",0)
            if trayNotifyWindow != 0:
                ctypes.windll.user32.GetWindowRect(trayNotifyWindow, ctypes.byref(trayRect))
                return trayRect

        # That hack didn't work, let's find the tray notify window the
        # by finding the task bar
        appBarData = APPBARDATA(0,0,0,0,RECT(0,0,0,0),0)
        if (ctypes.windll.shell32.SHAppBarMessage(ABM_GETTASKBARPOS,ctypes.byref(appBarData)) != 0):
            if appBarData.uEdge in [ABE_LEFT, ABE_RIGHT]:
                trayRect.top=appBarData.rc.bottom-100
                trayRect.bottom=appBarData.rc.bottom-16
                trayRect.left=appBarData.rc.left
                trayRect.right=appBarData.rc.right
            else: # ABE_TOP, ABE_BOTTOM
                trayRect.top=appBarData.rc.top
                trayRect.bottom=appBarData.rc.bottom
                trayRect.left=appBarData.rc.right-100
                trayRect.right=appBarData.rc.right-16
            return trayRect
        # Give up
        return None

    def minimize(self, href):
        fromer = RECT(0,0,0,0)
        ctypes.windll.user32.GetWindowRect(href,ctypes.byref(fromer))
        to = self.getTrayRect()
        if to:
            ctypes.windll.user32.DrawAnimatedRects(href,IDANI_CAPTION,ctypes.byref(fromer),ctypes.byref(to))
        ctypes.windll.user32.ShowWindow(href, ctypes.c_int(SW_HIDE))

    def restore(self, href):
        fromer = RECT(0,0,0,0)
        ctypes.windll.user32.GetWindowRect(href,ctypes.byref(fromer))
        to = self.getTrayRect()
        if to:
            ctypes.windll.user32.DrawAnimatedRects(href,IDANI_CAPTION,ctypes.byref(to),ctypes.byref(fromer))

        ctypes.windll.user32.ShowWindow(href, ctypes.c_int(SW_SHOW))

    def restoreAll(self):
        for href in self.minimized:
            self.restore(href)
        self.minimized = []
        self.delTrayIcon()
