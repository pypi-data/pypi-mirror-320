SRC = r"""
#define UNICODE
#define _UNICODE
#include <windows.h>
int main(){
HWND hWorkerW;
memset(&hWorkerW, 0, sizeof(hWorkerW));
HWND hShellViewMain;
memset(&hShellViewMain, 0, sizeof(hShellViewMain));
HWND hProgman = FindWindow(TEXT("Progman"), TEXT("Program Manager"));
HWND hDesktopWnd = GetDesktopWindow();
if (hProgman != NULL) {
    hShellViewMain = FindWindowEx(hProgman, 0, L"SHELLDLL_DefView", NULL);

    if (hShellViewMain == NULL) {
        hWorkerW = FindWindowEx(hDesktopWnd, hWorkerW, L"WorkerW", NULL);
        hShellViewMain = FindWindowEx(hWorkerW, NULL, L"SHELLDLL_DefView", NULL);
        while (hShellViewMain == NULL && hWorkerW != NULL) {
            hWorkerW = FindWindowEx(hDesktopWnd, hWorkerW, L"WorkerW", NULL);
            hShellViewMain = FindWindowEx(hWorkerW, 0, L"SHELLDLL_DefView", NULL);
        }
    }
}
SendMessage(hShellViewMain, WM_COMMAND, 0x7402, 0);
}
"""