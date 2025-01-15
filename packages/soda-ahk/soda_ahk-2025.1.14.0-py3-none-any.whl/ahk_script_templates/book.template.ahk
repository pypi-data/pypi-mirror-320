#Requires AutoHotkey v2.0
#SingleInstance Force

TraySetIcon "{resources}\book.ico"

Volume_Up::
{
    Send "{PgUp}"
}

Volume_Down::
{
    Send "{PgDn}"
}

Media_Play_Pause::
{
    Send " "
}

Media_Prev::
{
    Send "!{Left}"
}

Media_Next::
{
    Send "!{Right}"
}
