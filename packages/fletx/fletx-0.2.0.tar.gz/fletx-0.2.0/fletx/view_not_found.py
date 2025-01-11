import flet as ft 
from .xview import Xview

class NotFoundView(Xview):
    def build(self):
        return ft.View(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "404",
                    size=100,
                    weight=ft.FontWeight.BOLD,
                    opacity=0.8,
                ),
                ft.Text(
                    "Oops! page not found.",
                    size=30,
                    opacity=0.8
                ),
                
                
                ft.Row(
                    visible=self.debug,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=5,
                            margin=10,
                            border_radius=50,
                            border=ft.Border(
                                top=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                bottom=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                left=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                right=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                            ),
                            content=ft.Text("    Video tutorials    ",
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE
                            ),
                            on_click=lambda e: self.page.launch_url('https://www.youtube.com/playlist?list=PLkph27k2J8WrgXT8EyGr832qfLsWs5Psy')
                        ),
                        ft.Container(
                            padding=5,
                            margin=10,
                            border_radius=50,
                            border=ft.Border(
                                top=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                bottom=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                left=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                right=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                            ),
                            content=ft.Text("    Github repository    ",
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE
                            ),
                            on_click=lambda e: self.page.launch_url('https://github.com/saurabhwadekar/FletX')
                        ),
                        ft.Container(
                            padding=5,
                            margin=10,
                            border_radius=50,
                            border=ft.Border(
                                top=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                bottom=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                left=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                                right=ft.BorderSide(
                                    width=1,
                                    color=ft.Colors.BLUE
                                ),
                            ),
                            content=ft.Text("    Documentation    ",
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE
                            )
                        )

                    ]
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    bgcolor=ft.colors.BLUE,
                    icon_color=ft.colors.WHITE,
                    on_click=self.back
                ),
            ]
        )