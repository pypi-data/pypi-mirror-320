#Requires AutoHotkey v2.0
#SingleInstance Force

TraySetIcon "{resources}\tool.ico"

#K::
{
    Send "!{F4}"
}

#O::
{
    Run "explorer.exe"
}

#I::
{
    if !WinExist("ahk_exe chrome.exe") {
        Run "C:\Program Files\Google\Chrome\Application\chrome.exe"
    }
    if WinWait("ahk_exe chrome.exe", , 3) {
        WinActivate
    }
}

#!H::
{
    if !WinExist("ahk_exe hh.exe") {
        Run "{AutoHotkey.chm}"
        WinWait("ahk_exe hh.exe", , 3)
    }
    else {
        WinActivate("ahk_exe hh.exe")
        WinMaximize("ahk_exe hh.exe")
    }
}

#S::
{
    if !WinExist("Settings") {
        Run "ms-settings:appsfeatures-app"
    }
    WinWait "Settings", , 3
    WinActivate
    Sleep 200
    Send "{Tab}"
}

#!P::
{
    Run "ms-settings:personalization-colors"
}

; Run Terminal: Ctrl+Alt+T
^!T::
{
    Run "wt.exe"
}

#Esc::
{
    if !WinExist("ahk_exe procexp.exe") {
        Run "{resources}\procexp.exe"
    }
    if WinWait("ahk_exe procexp.exe", , 3) {
        WinActivate
        WinMaximize
    }
}

; Hide/Show Desktop icons: Win+Alt+D, Win+Ctrl+D
; See https://github.com/soda92/toggle-icons for source code
#!D::
{
    Run "{resources}\toggle-icons.exe",,"Hide"
}

#^D::
{
    Run "{resources}\toggle-icons.exe",,"Hide"
}

; Ctrl + Shift + S
#+S::
{
    Send "{PrintScreen}"
}


#!K::
{
Run '"{desktop}\BGI.exe - Shortcut.lnk"'
}

#HotIf WinActive("ahk_exe BGI.exe")
f::
{
Send "{Enter}"
}

#HotIf WinActive("ahk_exe BGI.exe")
v::
{
Send "{Enter}"
}
