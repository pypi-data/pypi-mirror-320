import flet as ft 
from .xview import Xview

class InternalErrorView(Xview):
    def init(self):
        self.markdown = ft.Ref[ft.Markdown]()

    def onBuildComplete(self):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.markdown.current.code_theme = ft.MarkdownCodeTheme.ATOM_ONE_LIGHT
        else:
            self.markdown.current.code_theme = ft.MarkdownCodeTheme.ATOM_ONE_DARK
        self.update()


    def build(self):

        return ft.View(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "500",
                    size=100,
                    weight=ft.FontWeight.BOLD,
                    opacity=0.8,
                ),
                ft.Text(
                    "An unexpected internal error has occurred.\n Please try again later or contact support if the issue persists.",
                    size=30,
                    opacity=0.8,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "[debug = true]",
                    visible=self.debug,
                    size=30,
                    opacity=0.8
                ),
                
                
                ft.Row(
                    visible= self.debug,
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
            
                ft.Markdown(
                    value=f"# Error occurred:\n\n```bash\n{self.error}\n```",
                    visible=self.debug,
                    ref=self.markdown,
                    selectable=True,
                    extension_set="gitHubWeb",
                    on_tap_link=lambda e: self.page.launch_url(e.data),
                ),
              
                
            ]
        )