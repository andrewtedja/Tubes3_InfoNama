import flet as ft
from ui.GUI import GUI

def main(page: ft.Page):
    GUI(page)

if __name__ == "__main__":
    ft.app(target=main)
